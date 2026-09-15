#!/usr/bin/env python3
"""
Post all remaining Storm Digital images to Instagram.
Skips already-posted images and uploads new ones.
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path('.env'))

# Already posted (from earlier in this session)
POSTED_IDS = {
    0: "18123051823632957",
    1: "17879058999599661", 
    2: "18180596236384309",
    3: "17966049872915966",
    4: "18204910687345393",
    5: "18139406677533254",
}

# Post copy for each post
POST_COPY = {
    0: ("We generate leads for roofers, HVAC, windows, plumbers", 
        "That's all we do. We're obsessed with your vertical. We generate an average of 15-30 qualified leads per month for our clients.\n\nReady to dominate your market?"),
    1: ("We only work with home service contractors",
        "Deep vertical expertise means better results. We know your seasonality, your CPL benchmarks, your objections.\n\nWe're not another generalist agency."),
    2: ("97% search online before calling",
        "If you're not on page 1, you're invisible. We make sure you're there."),
    3: ("Cost per lead: $38",
        "Our roofing clients beat industry average by 3.1x. That means more jobs for less spend."),
    4: ("5 Things Killing Your Google Ranking",
        "Missing GBP, zero reviews, slow mobile, no local schema, duplicate content.\n\nFix these 5 and you'll see movement in 30 days."),
    5: ("Are your Google Ads wasting money?",
        "We audit paid ad accounts for home service contractors — for free.\n\nWe'll find where budget is leaking and show you exactly how to fix it."),
    6: ("4.8-star average rating across our clients",
        "When reviews are your job, you get good at asking. Our clients average 4.8 stars and convert 3x higher from reviews.\n\nHaving a 4+ rating changes everything."),
}

hashtags = "#homeservicemarketing #googleads #roofing #hvac #plumbing #handyman #electrical #windows #seo #marketing #contractors"

images_dir = Path('.tmp/storm_images')
posted = 0

for post_id in sorted([f for f in images_dir.glob('post_*.png')]):
    post_num = int(post_id.stem.split('_')[1])
    
    # Skip already posted
    if post_num in POSTED_IDS:
        print(f"⊘ Post {post_num}: Already posted (ID: {POSTED_IDS[post_num]})")
        continue
    
    print(f"\n{'='*60}")
    print(f"Posting post_{post_num:02d}.png...")
    print(f"{'='*60}")
    
    # Get copy
    if post_num not in POST_COPY:
        print(f"⚠ Post {post_num}: No copy defined, skipping")
        continue
    
    headline, body = POST_COPY[post_num]
    caption = f"{headline}\n\n{body}"
    
    # Upload to Drive
    print(f"Uploading to Google Drive...")
    from tools.sheets_client import get_services
    
    try:
        _, drive = get_services()
    except Exception as e:
        print(f"ERROR: Could not connect to Google Drive: {e}")
        sys.exit(1)
    
    file_metadata = {'name': post_id.name}
    media = drive.files().create(body=file_metadata, media_body=str(post_id), fields='id').execute()
    file_id = media.get('id')
    print(f"✓ Uploaded to Drive: {file_id}")
    
    # Make public
    drive.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()
    
    image_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"✓ Public URL created")
    
    # Post to Instagram
    print(f"Posting to Instagram...")
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
        continue
    
    # Extract media ID
    for line in result.stdout.split('\n'):
        if 'Media ID:' in line:
            media_id = line.split('Media ID:')[-1].strip()
            print(f"✓ Posted with ID: {media_id}")
            posted += 1
            POSTED_IDS[post_num] = media_id
            break

print(f"\n{'='*60}")
print(f"✓ Done! Posted {posted} new images")
print(f"{'='*60}")
