import unittest

from FSharp.sublime_plugin_lib.events import IdleIntervalEventListener


class Test_IdleIntervalEventListener(unittest.TestCase):
    def testDefaultIdleInterval(self):
        listener = IdleIntervalEventListener()
        self.assertEqual(500, listener.duration)

    def testDoesNotImplement_on_idle(self):
        listener = IdleIntervalEventListener()
        self.assertFalse(hasattr(listener, 'on_idle'))

    def test_check_ReturnsTrueByDefault(self):
        listener = IdleIntervalEventListener()
        self.assertTrue(listener.check(view=None))
