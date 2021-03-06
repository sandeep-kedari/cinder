
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from cinder import exception
from cinder import test


class FakeNotifier(object):
    """Acts like the cinder.openstack.common.notifier.api module."""
    ERROR = 88

    def __init__(self):
        self.provided_publisher = None
        self.provided_event = None
        self.provided_priority = None
        self.provided_payload = None

    def notify(self, context, publisher, event, priority, payload):
        self.provided_publisher = publisher
        self.provided_event = event
        self.provided_priority = priority
        self.provided_payload = payload


def good_function():
    return 99


def bad_function_error():
    raise exception.Error()


def bad_function_exception():
    raise test.TestingException()


class CinderExceptionTestCase(test.TestCase):
    def test_default_error_msg(self):
        class FakeCinderException(exception.CinderException):
            message = "default message"

        exc = FakeCinderException()
        self.assertEqual('default message', unicode(exc))

    def test_error_msg(self):
        self.assertEqual('test', unicode(exception.CinderException('test')))

    def test_default_error_msg_with_kwargs(self):
        class FakeCinderException(exception.CinderException):
            message = "default message: %(code)s"

        exc = FakeCinderException(code=500)
        self.assertEqual('default message: 500', unicode(exc))

    def test_error_msg_exception_with_kwargs(self):
        # NOTE(dprince): disable format errors for this test
        self.flags(fatal_exception_format_errors=False)

        class FakeCinderException(exception.CinderException):
            message = "default message: %(misspelled_code)s"

        exc = FakeCinderException(code=500)
        self.assertEqual('default message: %(misspelled_code)s', unicode(exc))

    def test_default_error_code(self):
        class FakeCinderException(exception.CinderException):
            code = 404

        exc = FakeCinderException()
        self.assertEqual(404, exc.kwargs['code'])

    def test_error_code_from_kwarg(self):
        class FakeCinderException(exception.CinderException):
            code = 500

        exc = FakeCinderException(code=404)
        self.assertEqual(404, exc.kwargs['code'])
