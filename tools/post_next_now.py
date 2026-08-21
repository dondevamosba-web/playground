#!/usr/bin/env python3
"""
Post the next Storm Digital image without needing Sheets API.
Uploads local image to Google Drive and posts to Instagram.
"""
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path('.env'))

# Use the newly generated image
image_path = Path('.tmp/storm_images/post_05.png')

if not image_path.exists():
    print(f"ERROR: Image not found at {image_path}")
    sys.exit(1)

# Upload to Google Drive using fresh OAuth token
print(f"Uploading image to Google Drive...")
from tools.sheets_client import get_services

try:
    _, drive = get_services()
except Exception as e:
    print(f"ERROR: Could not connect to Google Drive: {e}")
    sys.exit(1)

# Upload file to Drive
file_metadata = {'name': image_path.name}
media = drive.files().create(body=file_metadata, media_body=str(image_path), fields='id').execute()
file_id = media.get('id')
print(f"✓ Uploaded to Drive with ID: {file_id}")

# Make file public
drive.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()

# Generate public URL
image_url = f"https://drive.google.com/uc?export=download&id={file_id}"
print(f"✓ Public URL: {image_url}")

# Post to Instagram
caption = """Are your Google Ads wasting money?

We audit paid ad accounts for home service contractors — for free.

We'll find where budget is leaking and show you exactly how to fix it.

DM us for your free audit. ⬇️"""

hashtags = "#homeservicemarketing #googleads #roofing #hvac #plumbing #handyman #electrical #windows"

result = subprocess.run([
    'python3', 'tools/post_instagram.py',
    '--account', 'storm',
    '--type', 'single',
    '--image-url', image_url,
    '--caption', caption,
    '--hashtags', hashtags
], capture_output=True, text=True)

print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr)
    sys.exit(result.returncode)

# Parse the media ID from output
for line in result.stdout.split('\n'):
    if 'Media ID:' in line:
        media_id = line.split('Media ID:')[-1].strip()
        print(f"\n✓ Posted with ID: {media_id}")
        break
