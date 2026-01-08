"""
12. Analytics & Feedback Agent
Tracks video performance and feeds insights back to Trend Detector
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import Config


class AnalyticsAgent:
    """
    Monitors YouTube analytics and provides feedback loop:
    - Tracks CTR (Click-Through Rate)
    - Monitors watch time and retention
    - Analyzes audience engagement
    - Identifies trending topics from performance
    - Feeds data back to Trend Detector
    
    Uses free YouTube Analytics API
    """
    
    def __init__(self, youtube_service=None):
        """
        Initialize analytics agent
        
        Args:
            youtube_service: Authenticated YouTube API service object
        """
        self.youtube = youtube_service
        self.channel_id = Config.YOUTUBE_CHANNEL_ID
    
    def get_video_stats(self, video_id: str, days: int = 7) -> Dict:
        """
        Get analytics for a specific video
        
        Args:
            video_id: YouTube video ID
            days: Number of days to analyze
        
        Returns:
            Dictionary with video statistics
        """
        
        if not self.youtube:
            print("⚠️  YouTube service not initialized")
            return {}
        
        print(f"📊 Fetching analytics for video: {video_id}")
        
        try:
            # Note: YouTube Analytics API requires special setup
            # Using YouTube Reporting API (free)
            
            # This is a simplified example
            # In production, you'd use YouTube Analytics API
            
            stats = {
                "video_id": video_id,
                "views": 0,
                "ctr": 0,
                "average_watch_time": 0,
                "retention": [],
                "engagement_rate": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"⚠️  Full analytics requires YouTube Analytics API setup")
            print("   Basic stats available through YouTube Data API")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error fetching analytics: {str(e)}")
            return {}
    
    def analyze_retention(self, watch_time_data: List[Dict]) -> Dict:
        """
        Analyze viewer retention patterns
        
        Args:
            watch_time_data: List of watch time data points
        
        Returns:
            Retention analysis
        """
        
        analysis = {
            "avg_retention": 0,
            "drop_points": [],
            "best_segments": [],
            "recommendations": []
        }
        
        if not watch_time_data:
            return analysis
        
        # Calculate average retention
        retentions = [d.get('retention', 0) for d in watch_time_data]
        analysis['avg_retention'] = sum(retentions) / len(retentions) if retentions else 0
        
        # Find drop points (where retention drops >10%)
        for i in range(1, len(watch_time_data)):
            drop = watch_time_data[i-1].get('retention', 0) - watch_time_data[i].get('retention', 0)
            if drop > 10:
                analysis['drop_points'].append({
                    "timestamp": watch_time_data[i].get('timestamp'),
                    "drop_percentage": drop
                })
        
        # Find best segments (retention stays high)
        for i in range(len(watch_time_data)):
            if watch_time_data[i].get('retention', 0) > 70:
                analysis['best_segments'].append({
                    "timestamp": watch_time_data[i].get('timestamp'),
                    "retention": watch_time_data[i].get('retention', 0)
                })
        
        # Recommendations
        if analysis['avg_retention'] < 50:
            analysis['recommendations'].append("Hook viewers earlier - retention drops quickly")
        if len(analysis['drop_points']) > 3:
            analysis['recommendations'].append("Tighten pacing - too many drop points")
        if not analysis['best_segments']:
            analysis['recommendations'].append("Review content - no strong retention segments")
        
        return analysis
    
    def identify_trending_insights(self, videos_data: List[Dict]) -> List[str]:
        """
        Identify patterns in successful videos
        
        Args:
            videos_data: List of video performance data
        
        Returns:
            List of insights for Trend Detector
        """
        
        insights = []
        
        if not videos_data:
            return insights
        
        # Find highest performing videos
        top_videos = sorted(
            videos_data,
            key=lambda x: x.get('views', 0),
            reverse=True
        )[:5]
        
        # Analyze topics of top videos
        top_topics = [v.get('topic', '') for v in top_videos]
        insights.append(f"Top performing topics: {', '.join(top_topics)}")
        
        # Analyze engagement rates
        avg_ctr = sum(v.get('ctr', 0) for v in videos_data) / len(videos_data)
        if avg_ctr > 5:
            insights.append("CTR is excellent - thumbnails/titles are working well")
        elif avg_ctr < 2:
            insights.append("CTR is low - improve titles and thumbnails")
        
        # Analyze watch time
        avg_watch_time = sum(v.get('watch_time_minutes', 0) for v in videos_data) / len(videos_data)
        insights.append(f"Average watch time: {avg_watch_time:.1f} minutes")
        
        return insights
    
    def generate_feedback_report(self, video_id: str) -> str:
        """
        Generate detailed feedback report for a video
        
        Args:
            video_id: Video to analyze
        
        Returns:
            Formatted report
        """
        
        print(f"📋 Generating feedback report for: {video_id}")
        
        report = f"\n📊 VIDEO PERFORMANCE REPORT\n"
        report += "=" * 70 + "\n\n"
        report += f"Video ID: {video_id}\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Get stats
        stats = self.get_video_stats(video_id)
        
        report += "📈 KEY METRICS:\n"
        report += f"  Views: {stats.get('views', 'N/A')}\n"
        report += f"  CTR: {stats.get('ctr', 'N/A')}%\n"
        report += f"  Avg Watch Time: {stats.get('average_watch_time', 'N/A')} minutes\n"
        report += f"  Engagement Rate: {stats.get('engagement_rate', 'N/A')}%\n\n"
        
        report += "💡 INSIGHTS & RECOMMENDATIONS:\n"
        report += "  • Monitor retention curves daily\n"
        report += "  • Test different thumbnails A/B style\n"
        report += "  • Optimize video length based on retention\n"
        report += "  • Engage with comments in first 24 hours\n"
        
        return report
    
    def export_analytics_json(self, videos_data: List[Dict], output_file: str) -> bool:
        """Export analytics data as JSON for analysis"""
        
        try:
            import json
            
            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(videos_data, f, indent=2, default=str)
            
            print(f"✅ Analytics exported: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Export error: {str(e)}")
            return False


# Example integration with Trend Detector
class FeedbackLoop:
    """
    Closes the loop: Analytics → Trend Detector
    """
    
    def __init__(self, trend_detector, analytics_agent):
        """
        Initialize feedback loop
        
        Args:
            trend_detector: TrendDetectorAgent instance
            analytics_agent: AnalyticsAgent instance
        """
        self.trend_detector = trend_detector
        self.analytics = analytics_agent
    
    def analyze_and_adjust(self, recent_videos: List[Dict]) -> Dict:
        """
        Analyze performance and suggest adjustments to trend detection
        
        Args:
            recent_videos: List of recent video data
        
        Returns:
            Recommendations for next videos
        """
        
        print("🔄 Running feedback loop analysis...")
        
        insights = self.analytics.identify_trending_insights(recent_videos)
        
        recommendations = {
            "insights": insights,
            "topics_to_focus_on": [],
            "topics_to_avoid": [],
            "timing_recommendations": "",
            "format_recommendations": ""
        }
        
        print("\n📊 FEEDBACK LOOP ANALYSIS:")
        for insight in insights:
            print(f"  • {insight}")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    import os
    
    analytics = AnalyticsAgent()
    
    # Generate sample report
    report = analytics.generate_feedback_report("sample_video_id")
    print(report)
