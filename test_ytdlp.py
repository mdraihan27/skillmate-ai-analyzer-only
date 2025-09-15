import yt_dlp
import json

# Test basic yt-dlp functionality
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,  # Just get basic info
    'default_search': 'ytsearch5:',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    try:
        results = ydl.extract_info('python programming basics', download=False)
        print(f'Found {len(results.get("entries", []))} videos')
        if results.get('entries'):
            print(f'First video: {results["entries"][0].get("title", "No title")}')
    except Exception as e:
        print(f'Error: {e}')