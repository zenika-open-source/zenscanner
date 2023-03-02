from django.urls import path, include
import posixpath
from pathlib import Path
from django.urls import re_path

import mimetypes

from django.http import FileResponse, Http404
from django.utils._os import safe_join
from django.utils.http import http_date
from django.utils.translation import gettext as _


def serve(request, path, document_root=None, show_indexes=False):
    if path == '':
        path = "index.html"
    path = posixpath.normpath(path).lstrip("/")
    fullpath = Path(safe_join(document_root, path))
    if not fullpath.exists():
        raise Http404(_("“%(path)s” does not exist") % {"path": fullpath})
    statobj = fullpath.stat()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    response = FileResponse(fullpath.open("rb"), content_type=content_type)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response.headers["Content-Encoding"] = encoding
    return response


def static(**kwargs):
    return [
        re_path(r"^(?P<path>.*)$", serve, kwargs=kwargs)
    ]


urlpatterns = [
    path('', include('core.urls')),
] + static(document_root='/zenscanner/app/')
