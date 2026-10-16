"""
Test script to verify Telegram bot configuration
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings

print("=" * 60)
print("TELEGRAM BOT CONFIGURATION CHECK")
print("=" * 60)

# Check token
token = settings.TELEGRAM_BOT_TOKEN
if token:
    print(f"✓ TELEGRAM_BOT_TOKEN is set")
    print(f"  Length: {len(token)} characters")
    if ':' in token:
        parts = token.split(':')
        print(f"  First part: {parts[0]}")
        if parts[0].isdigit():
            print(f"  ⚠️  First part is numeric ID, not username")
        else:
            print(f"  ✓ First part looks like a username")
    else:
        print(f"  ✗ Invalid token format (no colon found)")
else:
    print(f"✗ TELEGRAM_BOT_TOKEN is NOT set")

# Check username
username = settings.TELEGRAM_BOT_USERNAME
if username:
    print(f"✓ TELEGRAM_BOT_USERNAME is set: @{username}")
else:
    print(f"✗ TELEGRAM_BOT_USERNAME is NOT set")
    print(f"  This is REQUIRED for the Login Widget to work")

print("=" * 60)

if username:
    print("✅ Configuration looks good!")
else:
    print("⚠️  Please add TELEGRAM_BOT_USERNAME to your .env file")
    print("   Example: TELEGRAM_BOT_USERNAME=tradingedgebot")
