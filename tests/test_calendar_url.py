import unittest
from unittest import mock

from ppld_calendar import main as app
from ppld_calendar.caldav import CalDavClient, CalDavError, validate_calendar_url

GOOD = "https://caldav.example.test/dav/calendars/user/someone@example.com/cal-id/"
HC = "https://hc.example.test/abc"


class ValidateCalendarUrlTests(unittest.TestCase):
    def assert_rejected(self, url, expected_fragment):
        with self.assertRaises(CalDavError) as ctx:
            validate_calendar_url(url)
        msg = str(ctx.exception)
        self.assertIn(expected_fragment, msg)
        # The URL carries the account email; the message must never echo it or the host.
        self.assertNotIn("someone@example.com", msg)
        self.assertNotIn("caldav.example.test", msg)

    def test_valid_urls_pass(self):
        validate_calendar_url(GOOD)
        validate_calendar_url(GOOD.rstrip("/"))

    def test_double_slash_after_host_rejected(self):
        self.assert_rejected(
            "https://caldav.example.test//dav/calendars/user/someone@example.com/cal-id",
            "empty path segment",
        )

    def test_double_slash_inside_path_rejected(self):
        self.assert_rejected("https://caldav.example.test/dav//calendars/user/x/y", "empty path segment")

    def test_double_trailing_slash_rejected(self):
        self.assert_rejected("https://caldav.example.test/dav/calendars/user/x/y//", "empty path segment")

    def test_plain_http_rejected(self):
        self.assert_rejected("http://caldav.example.test/dav/calendars/user/x/y", "https")

    def test_query_string_rejected(self):
        self.assert_rejected(GOOD.rstrip("/") + "?export", "query string")

    def test_fragment_rejected(self):
        self.assert_rejected(GOOD + "#frag", "fragment")

    def test_server_root_rejected(self):
        self.assert_rejected("https://caldav.example.test/", "calendar collection")

    def test_empty_rejected(self):
        self.assert_rejected("", "https")


class WiringTests(unittest.TestCase):
    def test_client_constructor_validates(self):
        with self.assertRaises(CalDavError):
            CalDavClient("https://caldav.example.test//dav/calendars/user/x/y", "u", "p")

    def test_main_rejects_bad_url_before_login(self):
        env = {
            "PPLD_CARD_NUMBER": "12345",
            "PPLD_PIN": "s3cret",
            "CALDAV_USERNAME": "someone@example.com",
            "CALDAV_APP_PASSWORD": "app-pw",
            "CALDAV_CALENDAR_URL": "https://caldav.example.test//dav/calendars/user/x/y",
            "HEALTHCHECK_URL": HC,
        }
        with mock.patch.object(app.ppld, "login") as login, mock.patch.object(app, "ping") as ping:
            with self.assertLogs("ppld-calendar", level="ERROR") as logs:
                code = app.main(env)
        self.assertEqual(code, 1)
        login.assert_not_called()
        ping.assert_called_once_with(HC, "/fail")
        joined = "\n".join(logs.output)
        self.assertIn("empty path segment", joined)
        self.assertNotIn("caldav.example.test", joined)


if __name__ == "__main__":
    unittest.main()
