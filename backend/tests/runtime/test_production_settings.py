"""Guard the production settings against ephemeral or missing databases."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("database_url", "expected_error"),
    [
        (None, "DATABASE_URL is required in production"),
        (
            "sqlite:////tmp/tradethesis-test.sqlite3",
            "DATABASE_URL must use PostgreSQL in production",
        ),
    ],
)
def test_production_settings_reject_missing_or_sqlite_database(
    database_url, expected_error
):
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
    if database_url is None:
        env.pop("DATABASE_URL", None)
    else:
        env["DATABASE_URL"] = database_url

    result = subprocess.run(
        [sys.executable, "-c", "import config.settings.production"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode != 0
    assert expected_error in result.stderr


def test_production_settings_accept_postgresql_database_url():
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
    env["DATABASE_URL"] = (
        "postgresql://academy_user:academy_password@127.0.0.1:5432/academy_test"
    )

    result = subprocess.run(
        [sys.executable, "-c", "import config.settings.production"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
