from core.celery import debug_task
from core.tests.utils import TaskTestCase


class CeleryTestCase(TaskTestCase):

    def test_debug_task(self):
        self.assertEqual(debug_task.delay().get(timeout=10), "OK")
