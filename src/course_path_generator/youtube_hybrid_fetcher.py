"""
Hybrid YouTube fetcher using YouTube Data API v3 + yt-dlp fallback
This approach works well on Render without cookies
"""
import os
import json
import time
import random
from typing import List, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yt_dlp


class HybridYoutubeFetcher:
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube_service = None
        self.daily_quota_used = 0
        self.max_daily_quota = 9000  # Conservative limit
        
        if self.youtube_api_key:
            try:
                self.youtube_service = build('youtube', 'v3', developerKey=self.youtube_api_key)
                print("✅ YouTube Data API initialized")
            except Exception as e:
                print(f"⚠️ YouTube Data API initialization failed: {e}")
    
    def search_videos(self, topic: str, subject: str = "", max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for videos using hybrid approach:
        1. Try YouTube Data API first (fast, reliable, no subtitles)
        2. Fallback to yt-dlp for subtitle extraction if needed
        """
        
        # Create search query
        query = f"{subject} {topic}" if subject else topic
        query = query.strip()
        
        videos = []
        
        # Try YouTube Data API first
        if self.youtube_service and self.daily_quota_used < self.max_daily_quota:
            videos = self._search_with_api(query, max_results)
            
        # If API failed or no results, try yt-dlp
        if not videos:
            print("    📡 YouTube API failed, trying yt-dlp...")
            videos = self._search_with_ytdlp(query, max_results)
        
        return videos
    
    def _search_with_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using YouTube Data API v3"""
        try:
            # Search for videos (costs 100 quota units)
            search_response = self.youtube_service.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance',
                videoDuration='medium',  # 4-20 minutes
                videoDefinition='any',
                videoCaption='any'
            ).execute()
            
            self.daily_quota_used += 100
            
            video_ids = []
            videos_info = []
            
            # Extract video IDs
            for item in search_response['items']:
                video_ids.append(item['id']['videoId'])
            
            if not video_ids:
                return []
            
            # Get detailed video information (costs 1 quota unit per video)
            videos_response = self.youtube_service.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            self.daily_quota_used += len(video_ids)
            
            # Process video details
            for video in videos_response['items']:
                video_info = self._process_api_video(video)
                if video_info:
                    videos_info.append(video_info)
            
            print(f"    ✅ YouTube API found {len(videos_info)} videos (quota used: {self.daily_quota_used})")
            return videos_info
            
        except HttpError as e:
            print(f"    ❌ YouTube API error: {e}")
            if "quotaExceeded" in str(e):
                self.daily_quota_used = self.max_daily_quota  # Disable API for today
            return []
        except Exception as e:
            print(f"    ❌ YouTube API unexpected error: {e}")
            return []
    
    def _process_api_video(self, video: dict) -> Dict[str, Any]:
        """Process video data from YouTube API"""
        try:
            snippet = video['snippet']
            statistics = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            
            # Parse duration (PT4M13S -> 253 seconds)
            duration_str = content_details.get('duration', 'PT0S')
            duration_seconds = self._parse_duration(duration_str)
            
            return {
                'title': snippet.get('title', 'N/A'),
                'url': f"https://www.youtube.com/watch?v={video['id']}",
                'video_id': video['id'],
                'description': snippet.get('description', 'N/A'),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'duration': duration_seconds,
                'upload_date': snippet.get('publishedAt', 'N/A'),
                'uploader': snippet.get('channelTitle', 'N/A'),
                'channel': snippet.get('channelTitle', 'N/A'),
                'subtitles': 'API method - subtitles not available',
                'source': 'youtube_api'
            }
        except Exception as e:
            print(f"    ⚠️ Error processing video: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse YouTube API duration format (PT4M13S) to seconds"""
        try:
            import re
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                return hours * 3600 + minutes * 60 + seconds
            return 0
        except:
            return 0
    
    def _search_with_ytdlp(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback search using yt-dlp with enhanced configuration"""
        
        search_url = f"ytsearch{max_results}:{query}"
        videos_info = []
        
        # Enhanced yt-dlp options for server environment
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'ignoreerrors': True,
            
            # Server-friendly headers
            'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
            },
            
            # Conservative rate limiting
            'sleep_interval': 3,
            'max_sleep_interval': 10,
            'retries': 2,
            'fragment_retries': 2,
            'socket_timeout': 30,
            'format': 'best',
            'noplaylist': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(search_url, download=False)
                
                if 'entries' in search_results:
                    for video in search_results['entries']:
                        if video and len(videos_info) < max_results:
                            video_info = self._process_ytdlp_video(video)
                            if video_info:
                                videos_info.append(video_info)
                
                print(f"    ✅ yt-dlp found {len(videos_info)} videos")
                return videos_info
                
        except Exception as e:
            error_msg = str(e)
            if "Sign in" in error_msg or "403" in error_msg:
                print(f"    🤖 yt-dlp blocked by YouTube: {error_msg[:100]}...")
            else:
                print(f"    ❌ yt-dlp error: {error_msg[:100]}...")
            return []
    
    def _process_ytdlp_video(self, video: dict) -> Dict[str, Any]:
        """Process video data from yt-dlp"""
        try:
            return {
                'title': video.get('title', 'N/A'),
                'url': video.get('webpage_url', 'N/A'),
                'video_id': video.get('id', 'N/A'),
                'description': video.get('description', 'N/A')[:500],  # Limit description
                'view_count': video.get('view_count', 0),
                'like_count': video.get('like_count', 0),
                'duration': video.get('duration', 0),
                'upload_date': video.get('upload_date', 'N/A'),
                'uploader': video.get('uploader', 'N/A'),
                'channel': video.get('channel', 'N/A'),
                'subtitles': self._extract_subtitles_safe(video),
                'source': 'ytdlp'
            }
        except Exception as e:
            print(f"    ⚠️ Error processing yt-dlp video: {e}")
            return None
    
    def _extract_subtitles_safe(self, video: dict) -> str:
        """Safely extract subtitles from yt-dlp video data"""
        try:
            # Try to get subtitles
            subtitles = video.get('subtitles', {})
            automatic_captions = video.get('automatic_captions', {})
            
            subtitle_source = subtitles if subtitles else automatic_captions
            
            if subtitle_source:
                for lang in ['en', 'en-US', 'en-GB']:
                    if lang in subtitle_source:
                        return f"Subtitles available in {lang}"
            
            return "No subtitles available"
            
        except Exception:
            return "Subtitle extraction failed"


# Initialize the fetcher
youtube_fetcher = HybridYoutubeFetcher()


def search_youtube_videos_hybrid(topic: str, subject: str = "") -> List[Dict[str, Any]]:
    """
    Main function to search YouTube videos using hybrid approach
    This works well on Render without cookies
    """
    return youtube_fetcher.search_videos(topic, subject, max_results=5)
