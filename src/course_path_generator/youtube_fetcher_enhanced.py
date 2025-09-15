"""
Enhanced YouTube video fetcher with anti-detection measures
"""
import yt_dlp
import json
import time
import random
from typing import List, Dict, Any
import requests


def create_enhanced_ydl_opts():
    """Create yt-dlp options with enhanced anti-detection"""
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
    ]
    
    return {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Only get basic info, no format processing
        'writesubtitles': False,
        'writeautomaticsub': False,
        'skip_download': True,
        'ignoreerrors': True,
        
        # Random user agent
        'user_agent': random.choice(user_agents),
        'referer': 'https://www.youtube.com/',
        
        # Headers to mimic real browser
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        },
        
        # Rate limiting
        'sleep_interval': random.uniform(1, 3),  # Reduced delay to speed up
        'max_sleep_interval': 5,
        'retries': 2,  # Reduced retries to avoid hanging
        'fragment_retries': 1,  # Reduced fragment retries
        'socket_timeout': 15,  # Reduced timeout
        
        # Additional options
        'noplaylist': True,
        'extract_flat': False,
        'ignoreerrors': True,  # Continue on errors
        
        # Cookie handling
        'cookiesfrombrowser': None,  # Don't use browser cookies initially
    }


def search_youtube_videos_enhanced(topic: str, subject: str = "", max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Enhanced YouTube video search with multiple fallback strategies
    """
    
    # Create search query
    if subject and subject.strip():
        search_query = f"{subject.strip()}: {topic}"
    else:
        search_query = topic
    
    search_url = f"ytsearch5:{search_query}"
    videos_info = []
    
    for attempt in range(max_retries):
        try:
            print(f"    Attempt {attempt + 1}/{max_retries}")
            
            # Create new options for each attempt
            ydl_opts = create_enhanced_ydl_opts()
            
            # Add random delay between attempts
            if attempt > 0:
                delay = random.uniform(5, 15)
                print(f"    Waiting {delay:.1f} seconds before retry...")
                time.sleep(delay)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(search_url, download=False)
                
                if 'entries' in search_results:
                    for video in search_results['entries']:
                        if video:  # Sometimes entries can be None
                            video_info = extract_video_details_safe(video, ydl)
                            if video_info:
                                videos_info.append(video_info)
                    
                    if videos_info:
                        print(f"    ✅ Successfully found {len(videos_info)} videos")
                        return videos_info
            
        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ Attempt {attempt + 1} failed: {error_msg}")
            
            # Check for specific YouTube errors
            if "Sign in to confirm" in error_msg or "HTTP Error 403" in error_msg:
                print(f"    🤖 YouTube bot detection triggered, waiting longer...")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(30, 60))  # Wait 30-60 seconds
            else:
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))
    
    print(f"    ❌ All {max_retries} attempts failed")
    return videos_info


def extract_video_details_safe(video_data: Dict, ydl: yt_dlp.YoutubeDL) -> Dict[str, Any]:
    """
    Safely extract video details with error handling
    """
    try:
        # Get basic info first
        video_info = {
            'title': video_data.get('title', 'N/A'),
            'url': video_data.get('webpage_url', 'N/A'),
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
        
        # Try to get subtitles, but don't fail if we can't
        try:
            if video_data.get('id'):
                # Add small delay before subtitle extraction
                time.sleep(random.uniform(1, 3))
                
                # Get subtitle text
                subtitles_text = extract_subtitles_safe(video_data)
                video_info['subtitles'] = subtitles_text
                
        except Exception as subtitle_error:
            print(f"    ⚠️ Could not extract subtitles: {str(subtitle_error)[:100]}...")
            video_info['subtitles'] = 'Subtitle extraction failed'
        
        return video_info
        
    except Exception as e:
        print(f"    ⚠️ Error extracting video details: {str(e)[:100]}...")
        return None


def extract_subtitles_safe(video_info: Dict) -> str:
    """
    Safely extract subtitles with fallback strategies
    """
    try:
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
                    
                    # Find a suitable subtitle format
                    for entry in subtitle_entries:
                        if entry.get('url') and entry.get('ext') in ['vtt', 'srv3', 'ttml', 'json3']:
                            try:
                                # Add delay before subtitle download
                                time.sleep(random.uniform(1, 2))
                                
                                response = requests.get(
                                    entry['url'], 
                                    timeout=15,
                                    headers={
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                        'Referer': 'https://www.youtube.com/'
                                    }
                                )
                                
                                if response.status_code == 200:
                                    subtitle_content = response.text
                                    
                                    # Parse based on format
                                    if entry.get('ext') == 'vtt':
                                        return parse_vtt_subtitles(subtitle_content)
                                    elif entry.get('ext') == 'json3':
                                        return parse_json3_subtitles(subtitle_content)
                                    else:
                                        return clean_subtitle_text(subtitle_content)
                                        
                            except Exception as download_error:
                                print(f"    ⚠️ Subtitle download failed: {str(download_error)[:50]}...")
                                continue
                    
                    # If we found the language but couldn't download, break
                    if lang in subtitle_source:
                        break
        
        return "No subtitles available"
        
    except Exception as e:
        return f"Subtitle extraction error: {str(e)[:100]}..."


def parse_vtt_subtitles(vtt_content: str) -> str:
    """Parse VTT subtitle format and extract text."""
    try:
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
        
        return ' '.join(subtitle_text)[:5000]  # Limit to 5000 chars
    except:
        return "VTT parsing failed"


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
        
        return ' '.join(subtitle_text)[:5000]  # Limit to 5000 chars
    except:
        return "JSON3 parsing failed"


def clean_subtitle_text(raw_content: str) -> str:
    """Clean raw subtitle content by removing timestamps and formatting."""
    try:
        import re
        
        # Remove common timestamp patterns
        content = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', raw_content)
        content = re.sub(r'\d+\s*\n', '', content)  # Remove sequence numbers
        content = re.sub(r'<[^>]+>', '', content)    # Remove HTML/XML tags
        content = re.sub(r'\n+', ' ', content)       # Replace multiple newlines with space
        content = re.sub(r'\s+', ' ', content)       # Replace multiple spaces with single space
        
        return content.strip()[:5000]  # Limit to 5000 chars
    except:
        return "Text cleaning failed"
