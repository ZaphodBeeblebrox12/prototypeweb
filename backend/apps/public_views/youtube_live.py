"""Public, read-only YouTube live-broadcast status for the sitewide LIVE pill.

The API key is only used server-side. The endpoint fails closed: missing settings,
quota issues, or network errors never produce a LIVE badge.
"""
import json
import logging
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
# YouTube search.list costs 100 quota units; a 15-minute shared cache stays within
# the default 10,000-unit daily quota for one worker while keeping status current.
STATUS_CACHE_SECONDS = 15 * 60


def _youtube_get(resource, params, api_key):
    query = urlencode({**params, "key": api_key})
    request = Request(
        f"{YOUTUBE_API_BASE}/{resource}?{query}",
        headers={"Accept": "application/json", "User-Agent": "TradeThesis-LiveStatus/1.0"},
    )
    with urlopen(request, timeout=4) as response:
        return json.load(response)


def _public_response(payload):
    response = JsonResponse(payload)
    # The static marketing site and Django member area are separate origins.
    # This public, read-only status response does not use credentials or cookies.
    response["Access-Control-Allow-Origin"] = "*"
    response["Cache-Control"] = "no-store"
    return response


@require_GET
def youtube_live_status(request):
    """Return the public channel's active live video, or an offline/unknown state."""
    api_key = str(getattr(settings, "YOUTUBE_API_KEY", "") or "").strip()
    channel_id = str(getattr(settings, "YOUTUBE_CHANNEL_ID", "") or "").strip()
    if not api_key or not channel_id:
        return _public_response({
            "configured": False,
            "is_live": False,
            "status": "unconfigured",
            "watch_url": None,
        })

    cache_key = f"tradethesis:youtube-live-status:{channel_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return _public_response(cached)

    try:
        # Search's eventType=live filter only returns currently live public videos.
        # Unlike the uploads playlist, it can see a broadcast before it has ended.
        data = _youtube_get(
            "search",
            {
                "part": "snippet",
                "channelId": channel_id,
                "eventType": "live",
                "type": "video",
                "maxResults": 1,
            },
            api_key,
        )
        items = data.get("items") or []
        video_id = None
        if items:
            video_id = (items[0].get("id") or {}).get("videoId")
        is_live = bool(video_id)
        payload = {
            "configured": True,
            "is_live": is_live,
            "status": "live" if is_live else "offline",
            "watch_url": f"https://www.youtube.com/watch?v={video_id}" if is_live else None,
        }
        cache.set(cache_key, payload, timeout=STATUS_CACHE_SECONDS)
        return _public_response(payload)
    except (OSError, TimeoutError, ValueError, TypeError, KeyError) as exc:
        # Do not expose API errors, the channel ID, or the API key in a public response.
        logger.warning("YouTube live status check unavailable (%s).", type(exc).__name__)
        payload = {
            "configured": True,
            "is_live": False,
            "status": "unknown",
            "watch_url": None,
        }
        # Cache failure states too, so a bad key/quota response cannot trigger a request
        # from every visitor and consume additional quota.
        cache.set(cache_key, payload, timeout=STATUS_CACHE_SECONDS)
        return _public_response(payload)
