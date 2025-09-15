#!/usr/bin/env python3
"""
Debug YouTube URL extraction to see what fields are available
"""
import sys
import os
import yt_dlp

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def debug_youtube_data_structure():
    """Debug what data structure yt-dlp returns"""
    
    print("🔍 Debugging YouTube Data Structure...")
    print("=" * 50)
    
    # Configure yt-dlp with the same settings as the working API
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Only get basic info, don't process formats
        'skip_download': True,
        'ignoreerrors': True,  # Continue on errors
        'no_check_certificate': True,  # Bypass SSL issues
        
        # Anti-detection measures
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
        },
        'sleep_interval': 1,
        'max_sleep_interval': 5,
        'retries': 2,
        'fragment_retries': 1,
        'noplaylist': True,
    }
    
    # Test search
    search_query = "Java: Introduction to Java Programming"
    search_url = f"ytsearch2:{search_query}"  # Get only 2 results for debugging
    
    print(f"🎥 Searching for: '{search_query}'")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_results = ydl.extract_info(search_url, download=False)
            
            if 'entries' in search_results:
                print(f"✅ Found {len(search_results['entries'])} videos")
                
                for i, video in enumerate(search_results['entries'][:2], 1):
                    if video:
                        print(f"\n📝 Video {i} Data Structure:")
                        print(f"   Available Keys: {list(video.keys())}")
                        
                        # Check different possible URL fields
                        url_fields = [
                            'url', 'webpage_url', 'original_url', 'ie_url', 
                            'webpage_url_basename', 'webpage_url_domain'
                        ]
                        
                        print(f"   🔗 URL Fields:")
                        for field in url_fields:
                            value = video.get(field, 'NOT_FOUND')
                            print(f"      {field}: {value}")
                        
                        # Also check ID field to construct URL
                        video_id = video.get('id', 'NO_ID')
                        print(f"   🆔 Video ID: {video_id}")
                        
                        if video_id and video_id != 'NO_ID':
                            constructed_url = f"https://www.youtube.com/watch?v={video_id}"
                            print(f"   🏗️ Constructed URL: {constructed_url}")
                        
                        # Check title
                        title = video.get('title', 'NO_TITLE')
                        print(f"   📄 Title: {title}")
                        
            else:
                print("❌ No entries found in search results")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_youtube_data_structure()