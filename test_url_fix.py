#!/usr/bin/env python3
"""
Test the URL fix to ensure YouTube URLs are properly extracted
"""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from course_path_generator.get_youtube_videos import search_youtube_videos

def test_url_fix():
    """Test that YouTube URLs are properly extracted now"""
    
    print("🔍 Testing YouTube URL Fix...")
    print("=" * 50)
    
    # Configure yt-dlp with the same settings as the API
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
    
    # Test with a sample topic
    test_topic = "Introduction to Java Programming"
    subject = "Java"
    
    print(f"🎥 Testing URL extraction for: '{subject}: {test_topic}'")
    
    try:
        videos = search_youtube_videos(test_topic, ydl_opts, subject)
        print(f"✅ Found {len(videos)} videos")
        
        urls_found = 0
        urls_missing = 0
        
        for i, video in enumerate(videos, 1):
            title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
            url = video['url']
            video_id = video['video_id']
            
            print(f"\n📝 Video {i}:")
            print(f"   📄 Title: {title}")
            print(f"   🆔 Video ID: {video_id}")
            print(f"   🔗 URL: {url}")
            
            if url and url != 'N/A' and 'youtube.com' in url:
                urls_found += 1
                print(f"   ✅ URL Status: VALID")
            else:
                urls_missing += 1
                print(f"   ❌ URL Status: MISSING")
        
        print(f"\n📊 URL Extraction Results:")
        print(f"   ✅ URLs Found: {urls_found}")
        print(f"   ❌ URLs Missing: {urls_missing}")
        print(f"   📈 Success Rate: {(urls_found / len(videos) * 100):.1f}%")
        
        if urls_missing == 0:
            print(f"\n🎉 PERFECT! All YouTube URLs are now properly extracted!")
            return True
        else:
            print(f"\n⚠️ Some URLs are still missing. Need further investigation.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_url_fix()
    if success:
        print("\n🚀 URL fix successful! API responses will now include all YouTube URLs.")
    else:
        print("\n💥 URL fix needs more work.")