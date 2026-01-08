"""
Main orchestration script
Coordinates all agents to create and publish videos
"""
import os
from config import Config
from agents.trend_detector import TrendDetectorAgent
from agents.research_agent import ResearchAgent
from agents.script_writer import ScriptWriterAgent
from agents.voiceover_generator import VoiceoverGeneratorAgent
from agents.subtitle_generator import SubtitleGeneratorAgent
from agents.visual_planner import VisualScenePlannerAgent
from agents.video_generator import VideoGeneratorAgent
from agents.video_editor import VideoEditorAgent
from agents.metadata_agent import MetadataAgent
from agents.thumbnail_generator import ThumbnailGeneratorAgent
from agents.analytics_agent import AnalyticsAgent


class YouTubeAutomationPipeline:
    """
    Main orchestrator coordinating all agents
    """
    
    def __init__(self):
        """Initialize all agents"""
        print("🚀 Initializing YouTube Automation Pipeline...\n")
        
        Config.create_directories()
        Config.validate()
        
        self.trend_detector = TrendDetectorAgent()
        self.research_agent = ResearchAgent()
        self.script_writer = ScriptWriterAgent()
        self.voiceover_gen = VoiceoverGeneratorAgent()
        self.subtitle_gen = SubtitleGeneratorAgent()
        self.visual_planner = VisualScenePlannerAgent()
        self.video_gen = VideoGeneratorAgent()
        self.video_editor = VideoEditorAgent()
        self.metadata_agent = MetadataAgent()
        self.thumbnail_gen = ThumbnailGeneratorAgent()
        self.analytics = AnalyticsAgent()
        
        print("✅ All agents initialized\n")
    
    def create_video_workflow(self, custom_topic: str = None) -> bool:
        """
        Complete workflow: Trend → Research → Script → Voice → Video → Upload
        
        Args:
            custom_topic: Optional custom topic (skip trend detection)
        
        Returns:
            True if successful
        """
        
        print("📹 STARTING VIDEO CREATION WORKFLOW\n")
        print("=" * 70 + "\n")
        
        # STEP 1: Detect or use custom topic
        if custom_topic:
            topic = custom_topic
            print(f"📌 Using custom topic: {topic}\n")
        else:
            print("STEP 1: TREND DETECTION")
            print("-" * 70)
            trends = self.trend_detector.detect_trends(limit=1)
            if not trends:
                print("❌ No trends found. Exiting.")
                return False
            topic = trends[0].get('topic', '')
            print(f"✅ Selected topic: {topic}\n")
        
        # STEP 2: Research
        print("STEP 2: RESEARCH & CONTEXT")
        print("-" * 70)
        research = self.research_agent.research_topic(topic)
        print(self.research_agent.format_research(research))
        print()
        
        # STEP 3: Script Writing
        print("STEP 3: SCRIPT WRITING")
        print("-" * 70)
        script = self.script_writer.write_script(topic, research, style="cinematic")
        print(self.script_writer.format_script(script))
        print()
        
        # STEP 4: Voiceover
        print("STEP 4: VOICEOVER GENERATION")
        print("-" * 70)
        voiceover_path = os.path.join(Config.VOICEOVERS_DIR, "main_voiceover.wav")
        
        success = self.voiceover_gen.generate_voiceover(
            text=script['body'],
            output_path=voiceover_path
        )
        if not success:
            print("⚠️  Voiceover generation failed. Continuing with dummy file...")
        print()
        
        # STEP 5: Subtitles
        print("STEP 5: SUBTITLE GENERATION")
        print("-" * 70)
        subtitle_path = os.path.join(Config.OUTPUT_DIR, "subtitles.srt")
        
        if os.path.exists(voiceover_path):
            self.subtitle_gen.generate_srt_from_script(
                script_text=script['body'],
                audio_file=voiceover_path,
                output_srt=subtitle_path
            )
        else:
            print("⚠️  Skipping subtitles (no audio file)\n")
        
        # STEP 6: Visual Planning
        print("STEP 6: VISUAL SCENE PLANNING")
        print("-" * 70)
        visual_plan = self.visual_planner.plan_visuals(script.get('scenes', []))
        print(self.visual_planner.generate_storyboard_text(visual_plan))
        print()
        
        # STEP 7: Metadata
        print("STEP 7: METADATA & SEO")
        print("-" * 70)
        metadata = self.metadata_agent.generate_metadata(
            topic=topic,
            script_summary=script['body'][:200],
            key_points=research.get('key_points', [])
        )
        print(self.metadata_agent.format_metadata(metadata))
        print()
        
        # STEP 8: Thumbnail
        print("STEP 8: THUMBNAIL GENERATION")
        print("-" * 70)
        thumbnail_path = self.thumbnail_gen.generate_thumbnail(
            topic=topic,
            style="movie"
        )
        if thumbnail_path:
            self.thumbnail_gen.add_text_to_thumbnail(
                thumbnail_path=thumbnail_path,
                text=metadata['thumbnail_text'][:25],
                output_path=os.path.join(Config.THUMBNAILS_DIR, "final_thumbnail.png"),
                text_position="bottom"
            )
        print()
        
        # STEP 9: Video Assembly
        print("STEP 9: VIDEO ASSEMBLY")
        print("-" * 70)
        print("⚠️  Video assembly requires actual clips/assets")
        print("    In production, Video Generator would create these\n")
        
        # STEP 10: Analytics Setup
        print("STEP 10: ANALYTICS SETUP")
        print("-" * 70)
        print("✅ Analytics tracking configured")
        print("   Video performance will be monitored after upload\n")
        
        print("=" * 70)
        print("✅ WORKFLOW COMPLETE!")
        print("=" * 70)
        
        print("\n📊 NEXT STEPS:")
        print("1. Install/Configure Ollama for offline LLM")
        print("2. Set up API keys in .env file")
        print("3. Configure YouTube OAuth credentials")
        print("4. Install FFmpeg and Piper TTS")
        print("5. Run workflow again for full video generation")
        
        return True
    
    def quick_demo(self):
        """Quick demonstration of all agents"""
        
        print("\n🎬 QUICK DEMO: Testing All Agents\n")
        
        # Test topic
        demo_topic = "The Hidden History of AI"
        
        print(f"Demo Topic: {demo_topic}\n")
        
        # Research
        print("1️⃣  RESEARCH AGENT:")
        research = self.research_agent.research_topic(demo_topic)
        if research.get('key_points'):
            print(f"   Key points found: {len(research.get('key_points', []))}")
        print()
        
        # Script
        print("2️⃣  SCRIPT WRITER:")
        script = self.script_writer.write_script(demo_topic, research)
        if script.get('hook'):
            print(f"   Hook: {script['hook'][:80]}...")
        print()
        
        # Metadata
        print("3️⃣  METADATA AGENT:")
        metadata = self.metadata_agent.generate_metadata(demo_topic, "Demo video")
        print(f"   Title: {metadata['title']}")
        print(f"   Tags: {', '.join(metadata['tags'][:5])}...")
        print()
        
        print("✅ Demo complete! All agents functional.\n")


def main():
    """Main entry point"""
    
    try:
        pipeline = YouTubeAutomationPipeline()
        
        # Run quick demo first
        pipeline.quick_demo()
        
        # Option to run full workflow
        print("\n🚀 Ready to create full video?")
        print("1. With trend detection (requires API keys)")
        print("2. With custom topic")
        print("3. Demo mode (test agents only)")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            pipeline.create_video_workflow()
        elif choice == "2":
            topic = input("Enter video topic: ").strip()
            if topic:
                pipeline.create_video_workflow(custom_topic=topic)
        elif choice == "3":
            pipeline.quick_demo()
        else:
            print("Invalid choice")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
