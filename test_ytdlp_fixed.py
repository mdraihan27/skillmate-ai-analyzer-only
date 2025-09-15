import yt_dlp
import json

# Test with correct YouTube search syntax
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
}

print("Testing yt-dlp YouTube search...")

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    try:
        # Use the correct ytsearch syntax
        search_query = "ytsearch5:python programming basics"
        print(f"Searching: {search_query}")
        
        results = ydl.extract_info(search_query, download=False)
        
        entries = results.get("entries", []) if isinstance(results, dict) else []
        print(f"Found {len(entries)} videos")
        
        for i, entry in enumerate(entries[:3]):  # Show first 3
            title = entry.get('title', 'No title')
            duration = entry.get('duration', 'Unknown duration')
            url = entry.get('url', 'No URL')
            print(f"{i+1}. {title} ({duration}s) - {url}")
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()