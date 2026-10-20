from .base import *

DEBUG = True
# Local development can use local files; hosted production settings default to fail-closed durable storage.
ACADEMY_REQUIRE_DURABLE_ASSETS = env.bool("ACADEMY_REQUIRE_DURABLE_ASSETS", default=False)
ALLOWED_HOSTS = ["*"]
