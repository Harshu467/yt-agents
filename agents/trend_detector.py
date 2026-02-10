"""
1. Trend Detector Agent
Finds trending, viral, and high-potential video topics from multiple sources
"""
try:
    import tweepy
except ImportError:
    tweepy = None

try:
    import praw
except ImportError:
    praw = None

import requests
from typing import List, Dict
from datetime import datetime
from config import Config
from utils.llm_client import get_llm_client


class TrendDetectorAgent:
    """
    Detects trending topics from:
    - Twitter/X trending topics
    - Reddit trending posts
    - YouTube trending videos
    - Google Trends
    
    All APIs used have free tiers.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.twitter_client = self._init_twitter()
        self.reddit_client = self._init_reddit()
    
    def _init_twitter(self):
        """Initialize Twitter API client (if credentials available)"""
        if Config.TWITTER_BEARER_TOKEN:
            try:
                return tweepy.Client(bearer_token=Config.TWITTER_BEARER_TOKEN)
            except:
                print("⚠️  Twitter API credentials not valid")
                return None
        return None
    
    def _init_reddit(self):
        """Initialize Reddit API client (if credentials available)"""
        if Config.REDDIT_CLIENT_ID and Config.REDDIT_CLIENT_SECRET:
            try:
                return praw.Reddit(
                    client_id=Config.REDDIT_CLIENT_ID,
                    client_secret=Config.REDDIT_CLIENT_SECRET,
                    user_agent="yt-agents/1.0"
                )
            except:
                print("⚠️  Reddit API credentials not valid")
                return None
        return None
    
    def get_twitter_trends(self) -> List[Dict]:
        """Get trending topics from Twitter"""
        trends = []
        
        if not self.twitter_client:
            return trends
        
        try:
            # Worldwide trends (WOEID 1)
            result = self.twitter_client.get_place_trends(id=1)
            
            for trend in result[0]["trends"][:10]:  # Top 10
                trends.append({
                    "source": "twitter",
                    "topic": trend["name"],
                    "tweet_volume": trend.get("tweet_volume", 0),
                    "url": trend["url"],
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"❌ Twitter trends error: {str(e)}")
        
        return trends
    
    def get_reddit_trends(self) -> List[Dict]:
        """Get trending posts from Reddit"""
        trends = []
        
        if not self.reddit_client:
            return trends
        
        try:
            # Get trending subreddits
            subreddits = self.reddit_client.subreddits.trending()
            
            for sub in list(subreddits)[:10]:
                trends.append({
                    "source": "reddit",
                    "topic": sub.display_name,
                    "subscribers": sub.subscribers,
                    "url": f"https://reddit.com/r/{sub.display_name}",
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"❌ Reddit trends error: {str(e)}")
        
        return trends
    
    def get_youtube_trends(self) -> List[Dict]:
        """
        Get trending videos from YouTube
        Simulated since YouTube API doesn't have direct trending endpoint
        """
        trends = []
        
        if not Config.YOUTUBE_API_KEY:
            return trends
        
        try:
            from googleapiclient.discovery import build
            
            youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)
            
            request = youtube.videos().list(
                part="statistics,snippet",
                chart="mostPopular",
                regionCode="US",
                maxResults=10,
                videoCategoryId="0"
            )
            
            response = request.execute()
            
            for video in response.get("items", []):
                trends.append({
                    "source": "youtube",
                    "topic": video["snippet"]["title"],
                    "view_count": video["statistics"].get("viewCount", 0),
                    "video_id": video["id"],
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"❌ YouTube trends error: {str(e)}")
        
        return trends
    
    def analyze_trend_potential(self, topic: str) -> Dict:
        """
        Analyze the potential of a topic using AI
        Considers: searchability, retention potential, evergreen value
        """
        
        analysis_prompt = f"""Analyze this YouTube video topic for viral potential:

Topic: "{topic}"

Rate the following on a scale of 1-10:
1. Search Volume Potential (will people search for this?)
2. Retention Potential (will people watch till the end?)
3. Shareability (will people share this?)
4. Evergreen Value (will this be relevant in 6 months?)
5. Thumbnail Potential (can you make a compelling thumbnail?)

Also provide:
- Best audience demographic
- Estimated video length
- Content angles
- Potential for series

Format as JSON."""
        
        result = self.llm.extract_json(analysis_prompt)
        return result
    
    def rank_trends(self, trends: List[Dict]) -> List[Dict]:
        """
        Rank trends by potential using AI analysis
        Returns sorted list with potential scores
        """
        ranked = []
        
        for trend in trends:
            topic = trend.get("topic", "")
            
            # Quick scoring without heavy AI calls
            score = 5.0  # Base score
            
            # Boost for high engagement
            if trend.get("tweet_volume", 0) > 100000:
                score += 2
            elif trend.get("tweet_volume", 0) > 50000:
                score += 1
            
            if int(trend.get("view_count", 0)) > 1000000:
                score += 2
            elif int(trend.get("view_count", 0)) > 100000:
                score += 1
            
            if trend.get("subscribers", 0) > 1000000:
                score += 2
            elif trend.get("subscribers", 0) > 100000:
                score += 1
            
            trend["potential_score"] = min(score, 10.0)
            ranked.append(trend)
        
        # Sort by score
        ranked.sort(key=lambda x: x["potential_score"], reverse=True)
        return ranked
    
    def detect_trends(self, limit: int = 5) -> List[Dict]:
        """
        Detect and rank trending topics
        Returns top trending topics with analysis
        """
        print("🔍 Detecting trends...")
        
        all_trends = []
        
        # Collect from all sources
        all_trends.extend(self.get_twitter_trends())
        all_trends.extend(self.get_reddit_trends())
        all_trends.extend(self.get_youtube_trends())
        
        if not all_trends:
            print("⚠️  No trends found. Make sure API credentials are set in .env")
            return []
        
        # Remove duplicates
        seen = set()
        unique_trends = []
        for trend in all_trends:
            topic = trend.get("topic", "").lower()
            if topic not in seen:
                seen.add(topic)
                unique_trends.append(trend)
        
        # Rank by potential
        ranked = self.rank_trends(unique_trends)
        
        print(f"✅ Found {len(ranked)} trending topics")
        print("\n🏆 Top Trending Topics:")
        for i, trend in enumerate(ranked[:limit], 1):
            print(f"  {i}. {trend.get('topic')} (Score: {trend.get('potential_score', 0):.1f}/10)")
        
        return ranked[:limit]


# Example usage
if __name__ == "__main__":
    agent = TrendDetectorAgent()
    trends = agent.detect_trends(limit=5)
    
    print("\n📋 Selected Trend:")
    if trends:
        selected = trends[0]
        print(f"  Topic: {selected.get('topic')}")
        print(f"  Score: {selected.get('potential_score')}/10")
