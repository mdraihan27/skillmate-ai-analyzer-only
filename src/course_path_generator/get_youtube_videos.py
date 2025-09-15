import yt_dlp
import json
import time
import random
from typing import List, Dict, Any

# Import the simple and enhanced yt-dlp fetcher (no YouTube API)
try:
    from .youtube_fetcher_simple import get_youtube_videos_simple
    SIMPLE_AVAILABLE = True
except ImportError:
    SIMPLE_AVAILABLE = False

try:
    from .youtube_fetcher_enhanced import search_youtube_videos_enhanced
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False


def get_youtube_videos_for_topics(topics: List[str], subject: str = "") -> List[Dict[str, Any]]:

    
    all_topics_data = []
    
    # Configure yt-dlp options with anti-detection
    ydl_opts = {
        'quiet': True,  # Suppress most output
        'no_warnings': True,
        'extract_flat': True,  # Only get basic info, no format processing
        'writesubtitles': False,
        'writeautomaticsub': False,
        'skip_download': True,
        'ignoreerrors': True,
        
        # Anti-detection measures
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
        },
        
        # Rate limiting and retry logic
        'sleep_interval': 1,  # Sleep 1 second between requests
        'max_sleep_interval': 5,
        'retries': 2,  # Reduced retries to avoid hanging
        'fragment_retries': 1,  # Reduced fragment retries
        'socket_timeout': 15,  # Reduced timeout
        
        # Use cookies if available
        'cookiefile': None,  # We'll handle this differently
        
        # Extract format options
        'noplaylist': True,
    }
    
    print(f"Processing {len(topics)} topics...")
    
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] Searching for: '{topic}'")
        
        try:
            # Try simple approach first (most reliable)
            if SIMPLE_AVAILABLE:
                print("    Using simple yt-dlp approach...")
                topic_videos = get_youtube_videos_simple([topic], subject)
                if topic_videos and topic_videos[0]['video_count'] > 0:
                    videos_for_topic = topic_videos[0]['videos']
                else:
                    videos_for_topic = []
            # Fallback to enhanced yt-dlp
            elif ENHANCED_AVAILABLE:
                print("    Using enhanced yt-dlp approach...")
                videos_for_topic = search_youtube_videos_enhanced(topic, subject)
            # Last resort: basic yt-dlp
            else:
                print("    Using basic yt-dlp approach...")
                videos_for_topic = search_youtube_videos(topic, ydl_opts, subject)
            
            # Create topic dictionary with topic name and videos
            topic_data = {
                'topic_name': topic,
                'videos': videos_for_topic,
                'video_count': len(videos_for_topic)
            }
            
            all_topics_data.append(topic_data)
            print(f"  ✓ Found {len(videos_for_topic)} videos for '{topic}'")
            
        except Exception as e:
            print(f"  ✗ Error processing topic '{topic}': {str(e)}")
            # Add empty topic data for failed topics
            topic_data = {
                'topic_name': topic,
                'videos': [],
                'video_count': 0
            }
            all_topics_data.append(topic_data)
    
    return all_topics_data


def search_youtube_videos(topic: str, ydl_opts: Dict, subject: str = "") -> List[Dict[str, Any]]:

    
    # Create search query with subject prefix if provided
    if subject and subject.strip():
        search_query = f"{subject.strip()}: {topic}"
    else:
        search_query = topic
    
    # YouTube search URL - gets top results for the topic
    search_url = f"ytsearch5:{search_query}"  # ytsearch5 means get top 5 results
    
    videos_info = []
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract info from search results
            search_results = ydl.extract_info(search_url, download=False)
            
            if 'entries' in search_results:
                for video in search_results['entries']:
                    if video:  # Sometimes entries can be None
                        video_info = extract_video_details(video, ydl)
                        videos_info.append(video_info)
            
        except Exception as e:
            print(f"    Error searching for '{search_query}': {str(e)}")
    
    return videos_info


def extract_video_details(video_data: Dict, ydl: yt_dlp.YoutubeDL) -> Dict[str, Any]:
    
    # Get basic info - Fixed URL extraction for extract_flat=True mode
    video_info = {
        'title': video_data.get('title', 'N/A'),
        'url': video_data.get('url', video_data.get('webpage_url', 'N/A')),  # Try 'url' first, then 'webpage_url'
        'video_id': video_data.get('id', 'N/A'),
        'description': video_data.get('description', 'N/A'),
        'view_count': video_data.get('view_count', 0),
        'like_count': video_data.get('like_count', 0),
        'duration': video_data.get('duration', 0),
        'upload_date': video_data.get('upload_date', 'N/A'),
        'uploader': video_data.get('uploader', 'N/A'),
        'channel': video_data.get('channel', 'N/A'),
        'subtitles': 'N/A'
    }
    
    # Backup: If URL is still N/A, construct it from video_id
    if video_info['url'] == 'N/A' and video_info['video_id'] != 'N/A':
        video_info['url'] = f"https://www.youtube.com/watch?v={video_info['video_id']}"
    
    # Try to extract subtitles - DISABLED to avoid format validation errors
    try:
        # Skip full video extraction to avoid format validation issues
        # This was causing "Requested format is not available" errors
        # We'll rely on basic info from the search results instead
        video_info['subtitles'] = 'Available (extraction disabled to prevent errors)'
            
    except Exception as e:
        print(f"    Warning: Could not extract full details for video {video_info['title'][:50]}...: {str(e)}")
        video_info['subtitles'] = 'N/A'
    
    return video_info


def extract_subtitles_text(video_info: Dict) -> str:

    import requests
    
    # Try to get subtitles or automatic subtitles
    subtitles = video_info.get('subtitles', {})
    automatic_captions = video_info.get('automatic_captions', {})
    
    # Prefer manual subtitles over automatic ones
    subtitle_source = subtitles if subtitles else automatic_captions
    
    if subtitle_source:
        # Try to get English subtitles
        for lang in ['en', 'en-US', 'en-GB']:
            if lang in subtitle_source:
                subtitle_entries = subtitle_source[lang]
                
                # Find a suitable subtitle format and download it
                for entry in subtitle_entries:
                    if entry.get('url') and entry.get('ext') in ['vtt', 'srv3', 'ttml', 'json3']:
                        try:
                            # Download the subtitle file content
                            response = requests.get(entry['url'], timeout=10)
                            if response.status_code == 200:
                                subtitle_content = response.text
                                
                                # Parse based on format
                                if entry.get('ext') == 'vtt':
                                    return parse_vtt_subtitles(subtitle_content)
                                elif entry.get('ext') == 'json3':
                                    return parse_json3_subtitles(subtitle_content)
                                else:
                                    # For other formats, return raw content (cleaned)
                                    return clean_subtitle_text(subtitle_content)
                                    
                        except Exception as e:
                            print(f"    Warning: Could not download subtitles from {entry.get('url')}: {str(e)}")
                            continue
                
                # If we found the language but couldn't download, break
                if lang in subtitle_source:
                    break
    
    return "No subtitles available"


def parse_vtt_subtitles(vtt_content: str) -> str:
    """Parse VTT subtitle format and extract text."""
    lines = vtt_content.split('\n')
    subtitle_text = []
    
    for line in lines:
        line = line.strip()
        # Skip VTT headers, timestamps, and empty lines
        if (line and 
            not line.startswith('WEBVTT') and 
            not line.startswith('NOTE') and
            not '-->' in line and
            not line.isdigit()):
            # Remove VTT styling tags
            import re
            clean_line = re.sub(r'<[^>]+>', '', line)
            if clean_line:
                subtitle_text.append(clean_line)
    
    return ' '.join(subtitle_text)


def parse_json3_subtitles(json_content: str) -> str:
    """Parse JSON3 subtitle format and extract text."""
    try:
        import json
        data = json.loads(json_content)
        
        subtitle_text = []
        if 'events' in data:
            for event in data['events']:
                if 'segs' in event:
                    for seg in event['segs']:
                        if 'utf8' in seg:
                            subtitle_text.append(seg['utf8'])
        
        return ' '.join(subtitle_text)
    except:
        return clean_subtitle_text(json_content)


def clean_subtitle_text(raw_content: str) -> str:
    """Clean raw subtitle content by removing timestamps and formatting."""
    import re
    
    # Remove common timestamp patterns
    content = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', raw_content)
    content = re.sub(r'\d+\s*\n', '', content)  # Remove sequence numbers
    content = re.sub(r'<[^>]+>', '', content)    # Remove HTML/XML tags
    content = re.sub(r'\n+', ' ', content)       # Replace multiple newlines with space
    content = re.sub(r'\s+', ' ', content)       # Replace multiple spaces with single space
    
    return content.strip()


def print_videos_data(videos_data: List[Dict[str, Any]]) -> None:

    
    print("\n" + "="*80)
    print("YOUTUBE VIDEOS DATA FOR ALL TOPICS")
    print("="*80)
    
    total_videos = sum(topic_data['video_count'] for topic_data in videos_data)
    print(f"Total Topics: {len(videos_data)}")
    print(f"Total Videos: {total_videos}")
    
    for topic_num, topic_data in enumerate(videos_data, 1):
        topic_name = topic_data['topic_name']
        videos = topic_data['videos']
        video_count = topic_data['video_count']
        
        print(f"\n{'-'*60}")
        print(f"TOPIC {topic_num}: {topic_name.upper()}")
        print(f"{'-'*60}")
        print(f"Videos found: {video_count}")
        
        for video_num, video in enumerate(videos, 1):
            print(f"\n  VIDEO {video_num}:")
            print(f"    Title: {video['title']}")
            print(f"    Channel: {video['channel']}")
            print(f"    Views: {video['view_count']:,}" if video['view_count'] else "    Views: N/A")
            print(f"    Likes: {video['like_count']:,}" if video['like_count'] else "    Likes: N/A")
            print(f"    Duration: {video['duration']} seconds" if video['duration'] else "    Duration: N/A")
            print(f"    Upload Date: {video['upload_date']}")
            print(f"    URL: {video['url']}")
            
            # Print complete description
            description = video['description']
            if description and description != 'N/A':
                print(f"    Description: {description}")
            else:
                print(f"    Description: N/A")
            
            print(f"    Subtitles: {video['subtitles']}")


# Example usage and test function
def test_with_sample_topics():

    sample_topics = [
        "functions tutorial",
        "loops explained", 
        "machine learning basics"
    ]
    
    subject = "Python Programming"
    
    print("Testing with sample topics...")
    videos_data = get_youtube_videos_for_topics(sample_topics, subject)
    print_videos_data(videos_data)
    
    return videos_data


if __name__ == "__main__":
    # Test the function
    test_data = test_with_sample_topics()
