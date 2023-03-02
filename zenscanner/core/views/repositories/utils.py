from django.http import JsonResponse, HttpResponse
from django.conf import settings
from core.models import WorkerToken, Scan
import os
import magic
from minio import Minio
from core.celery import run_uploaded_scan
from ninja import Schema
from uuid import UUID, uuid4
from ninja.errors import HttpError


class RepositoryUploadInformation(Schema):
    type: str
    url: str


class TaskId(Schema):
    task_id: UUID


class RemoteUpload():

    def __init__(self, repository):
        self.repository = repository
        if settings.UPLOAD_TYPE == "s3":
            self.s3client = Minio(
                settings.UPLOAD_ENDPOINT,
                access_key=settings.UPLOAD_ACCESS_KEY,
                secret_key=settings.UPLOAD_SECRET_KEY,
                region=settings.UPLOAD_REGION,
            )

    def get_link(self, request):
        if settings.UPLOAD_TYPE == "s3":
            bucket_name = settings.UPLOAD_BUCKET
            final_name = str(uuid4()) + ".tgz"
            if not self.s3client.bucket_exists(bucket_name):
                self.s3client.make_bucket(bucket_name)  # TODO: Add private policy
            url = self.s3client.presigned_put_object(bucket_name, final_name)

        elif settings.UPLOAD_TYPE == "local":
            url = request.build_absolute_uri('/api/repositories/{}/upload'.format(self.repository.uuid))
            if request.is_secure():
                url = url.replace('http://', 'https://')
        return {"type": settings.UPLOAD_TYPE, "url": url}

    def upload(self, request):
        scan = Scan(repository=self.repository)
        scan.save()
        worker_token = WorkerToken(scan=scan)
        worker_token.save()
        if settings.UPLOAD_TYPE != "local":
            bucket_name = settings.UPLOAD_BUCKET
            final_name = str(uuid4()) + ".tgz"
            run_uploaded_scan.apply_async(args=[worker_token.token, self.s3client.presigned_get_object(bucket_name, final_name)], task_id=str(scan.uuid))
        else:
            file_path = self.upload_path(request, scan)
            with open(file_path, "wb") as uploaded_file:
                uploaded_file.write(request.body)
            if magic.from_file(file_path, mime=True) != 'application/gzip':
                os.remove(file_path)
                worker_token.delete()
                return JsonResponse({'message': "Unprocessable Entity"}, status=422)
            run_uploaded_scan.apply_async(args=[worker_token.token, "/api/workers/download"], task_id=str(scan.uuid))

        return {"task_id": scan.uuid}

    def upload_path(self, request, scan):
        upload_dir = os.path.join(settings.UPLOAD_DIR, str(self.repository.uuid))
        file_path = os.path.join(upload_dir, str(scan.uuid) + ".tgz")
        os.makedirs(upload_dir, exist_ok=True)
        return file_path

    def download(self, request):
        if settings.UPLOAD_TYPE != "local":
            raise HttpError(404, "Not Found")
        file_path = self.upload_path(request, request.worker.scan)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/gzip")
                response['Content-Disposition'] = 'inline; filename=scan.tgz'
                return response
        raise HttpError(404, "Not Found")
