from core.tests.utils import TaskTestCase
from django.test import tag

from core.tests.workers.scanners.scanner_base_test import ScannerBaseTestTestCase

from core.tasks_modules.scanners.Gitleaks import Gitleaks
import pytest


@pytest.mark.docker
class ScanGitleaksTestCase(TaskTestCase):

    @tag('docker')
    def test_gitleaks_scanner(self):

        sc = ScannerBaseTestTestCase(Gitleaks, 'gitleaks')
        sc.run()
