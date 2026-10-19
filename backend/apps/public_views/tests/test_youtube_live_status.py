import io
import json
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings


def api_response(payload):
    return io.BytesIO(json.dumps(payload).encode("utf-8"))


class YouTubeLiveStatusTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @override_settings(YOUTUBE_API_KEY="", YOUTUBE_CHANNEL_ID="")
    def test_missing_configuration_fails_closed_without_api_call(self):
        with patch("apps.public_views.youtube_live.urlopen") as urlopen_mock:
            response = self.client.get("/api/youtube/live-status/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["configured"])
        self.assertFalse(response.json()["is_live"])
        self.assertIsNone(response.json()["watch_url"])
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        urlopen_mock.assert_not_called()

    @override_settings(YOUTUBE_API_KEY="test-api-key", YOUTUBE_CHANNEL_ID="UC-test")
    def test_live_video_is_returned_for_the_pill(self):
        with patch("apps.public_views.youtube_live.urlopen", return_value=api_response({
            "items": [{
                "id": {"kind": "youtube#video", "videoId": "live-video-123"},
                "snippet": {"liveBroadcastContent": "live"},
            }]
        })) as urlopen_mock:
            response = self.client.get("/api/youtube/live-status/")

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["configured"])
        self.assertTrue(payload["is_live"])
        self.assertEqual(payload["status"], "live")
        self.assertEqual(payload["watch_url"], "https://www.youtube.com/watch?v=live-video-123")
        self.assertEqual(urlopen_mock.call_count, 1)
        request_url = urlopen_mock.call_args.args[0].full_url
        self.assertIn("eventType=live", request_url)
        self.assertIn("channelId=UC-test", request_url)
        self.assertIn("key=test-api-key", request_url)

    @override_settings(YOUTUBE_API_KEY="test-api-key", YOUTUBE_CHANNEL_ID="UC-test")
    def test_no_active_broadcast_does_not_show_live_pill(self):
        with patch("apps.public_views.youtube_live.urlopen", return_value=api_response({"items": []})):
            response = self.client.get("/api/youtube/live-status/")

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["configured"])
        self.assertFalse(payload["is_live"])
        self.assertEqual(payload["status"], "offline")
        self.assertIsNone(payload["watch_url"])
