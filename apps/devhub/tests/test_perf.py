# -*- coding: utf8 -*-
import cgi
from cStringIO import StringIO
import textwrap

from mock import patch
from nose.tools import eq_, raises
import test_utils

from devhub.perf import start_perf_test, BadResponse
from files.models import File


def set_url_content(fake_urlopen, text):
    fake_urlopen.return_value = StringIO(textwrap.dedent(text))


class TestPerf(test_utils.TestCase):
    fixtures = ['devhub/addon-validation-1']

    def setUp(self):
        self.file = File.objects.get(
                            version__addon__slug='searchaddon11102010')

    def start(self, *args, **kw):
        return start_perf_test(self.file, *args, **kw)

    @patch('devhub.perf.urlopen')
    def test_success(self, urlopen):
        set_url_content(urlopen, """
            INFO: validating key os win32
            SENDCHANGE: change sent successfully
            """)
        self.start('win32', 'firefox4.0')
        assert urlopen.called
        url, params = urlopen.call_args[0][0].split('?')
        params = cgi.parse_qs(params)
        eq_(params['os'], ['win32'])
        eq_(params['firefox'], ['firefox4.0'])
        eq_(params['url'], [self.file.get_url_path(None, 'perftest')])

    @raises(BadResponse)
    @patch('devhub.perf.urlopen')
    def test_error(self, urlopen):
        set_url_content(urlopen, """
            INFO: validating key os win32
            ERROR: addon url no good
            """)
        self.start('win32', 'firefox4.0')

    @raises(BadResponse)
    @patch('devhub.perf.urlopen')
    def test_no_sendchange(self, urlopen):
        set_url_content(urlopen, """
            INFO: validating key os win32
            INFO: who knows what happened
            """)
        self.start('win32', 'firefox4.0')
