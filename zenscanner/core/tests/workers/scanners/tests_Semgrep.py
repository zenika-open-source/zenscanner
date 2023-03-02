from core.tests.utils import TaskTestCase
from django.test import tag

from core.tests.workers.scanners.scanner_base_test import ScannerBaseTestTestCase

from core.tasks_modules.scanners.Semgrep import Semgrep
import pytest


@pytest.mark.docker
class ScanSemgrepTestCase(TaskTestCase):

    @tag('docker')
    def test_semgrep_scanner(self):

        sc = ScannerBaseTestTestCase(Semgrep, 'semgrep')
        sc.run()
