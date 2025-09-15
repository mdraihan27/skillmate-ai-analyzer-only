import yt_dlp
import json

# Test with more verbose output to see what's happening
ydl_opts = {
    'quiet': False,  # Show output for debugging
    'no_warnings': False,
    'extract_flat': True,
    'default_search': 'ytsearch5:',
    'verbose': True,
}

print("Testing yt-dlp with verbose output...")

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    try:
        print("Searching for 'python programming'...")
        results = ydl.extract_info('python programming', download=False)
        
        print(f"\nResults type: {type(results)}")
        print(f"Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        entries = results.get("entries", []) if isinstance(results, dict) else []
        print(f"Found {len(entries)} videos")
        
        for i, entry in enumerate(entries[:3]):  # Show first 3
            print(f"{i+1}. {entry.get('title', 'No title')} - {entry.get('url', 'No URL')}")
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()