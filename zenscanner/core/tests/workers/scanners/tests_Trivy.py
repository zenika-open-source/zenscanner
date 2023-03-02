from core.tests.utils import TaskTestCase
from django.test import tag

from core.tests.workers.scanners.scanner_base_test import ScannerBaseTestTestCase

from core.tasks_modules.scanners.Trivy import Trivy
import pytest


@pytest.mark.docker
class ScanTrivyTestCase(TaskTestCase):

    @tag('docker')
    def test_trivy_scanner(self):

        sc = ScannerBaseTestTestCase(Trivy, 'trivy')
        sc.run()
