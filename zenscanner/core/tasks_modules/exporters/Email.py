from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from core.models import ScanResult
from slugify import slugify


class Email():

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def is_runnable(self):
        return settings.EMAIL_BACKEND is not None

    def run(self):
        repository = self.kwargs['repository']
        scan = self.kwargs['scan']
        scanresult = ScanResult.objects.get(repository=repository, task_id=scan.uuid)
        vulnerabilities = scan.vulnerability_set.all()
        owner = repository.owner
        new_vulnerabilities = 0
        for vuln in vulnerabilities:
            if vuln.is_new:
                new_vulnerabilities += 1
        mail_data = {
            'repository': repository,
            'owner': owner,
            'vulnerabilities': vulnerabilities,
            'vulnerabilities_count': len(vulnerabilities),
            'new_vulnerabilities': new_vulnerabilities
        }

        if settings.WEBUI_URI:
            if settings.WEBUI_URI.endswith('/'):
                mail_data['email_link'] = '{}scan/{}'.format(settings.WEBUI_URI, scan.uuid)
            else:
                mail_data['email_link'] = '{}/scan/{}'.format(settings.WEBUI_URI, scan.uuid)

        msg_plain = render_to_string('email/scan_summary.txt', mail_data)
        msg_html = render_to_string('email/scan_summary.html', mail_data)
        subject = "[ZenScanner] Scan finished for {} ({})".format(repository.name, scan.branch)
        if new_vulnerabilities > 0:
            subject += " {} new vulnerabilities".format(new_vulnerabilities)
        email = EmailMultiAlternatives(subject, msg_plain, 'zenscanner@zenika.com', [owner.email])
        email.attach_alternative(msg_html, 'text/html')
        sarif_filename = "{} ({}) {}.sarif".format(slugify(repository.name), slugify(scan.branch), str(scan.uuid))
        email.attach(sarif_filename, scanresult.sarif, "application/json")
        email.send()
