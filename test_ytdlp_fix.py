#!/usr/bin/env python3
"""
Quick test to verify yt-dlp fix
"""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from course_path_generator.get_youtube_videos import search_youtube_videos

def test_ytdlp_fix():
    """Test if the yt-dlp fix works"""
    
    print("🧪 Testing yt-dlp fix...")
    
    # Configure yt-dlp with the same settings as main_course_creator.py
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
        'retries': 2,  # Reduced retries
        'fragment_retries': 1,  # Reduced fragment retries
        'noplaylist': True,
        # Removed 'format': 'best' to avoid validation errors
    }
    
    # Test with a problematic topic
    test_topic = "Looping Constructs: for, while, and do-while Loops"
    subject = "Java"
    
    print(f"🎥 Searching for: '{subject}: {test_topic}'")
    
    try:
        videos = search_youtube_videos(test_topic, ydl_opts, subject)
        print(f"✅ Success! Found {len(videos)} videos without format errors")
        
        for i, video in enumerate(videos, 1):
            print(f"  {i}. {video['title'][:60]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ytdlp_fix()
    if success:
        print("\n🎉 yt-dlp fix works! The API should work now.")
    else:
        print("\n💥 yt-dlp still has issues.")