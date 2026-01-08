"""
3. Script Writer Agent
Converts research into a cinematic, high-retention script
"""
from typing import Dict, List
from utils.llm_client import get_llm_client


class ScriptWriterAgent:
    """
    Converts research into a cinematic script with:
    - Hook (first 3 seconds)
    - Body (main content)
    - CTA (call-to-action)
    - Scene-by-scene breakdown
    
    Focuses on retention and viewer engagement.
    """
    
    def __init__(self, video_duration: int = 600):  # 10 minutes default
        self.llm = get_llm_client()
        self.video_duration = video_duration
    
    def write_script(self, topic: str, research_data: Dict, style: str = "cinematic") -> Dict:
        """
        Write complete video script
        
        Args:
            topic: Video topic
            research_data: Research from Research Agent
            style: Script style (cinematic, educational, entertaining)
        
        Returns:
            Complete script with all sections
        """
        print(f"✍️  Writing {style} script for: {topic}")
        
        script_data = {
            "topic": topic,
            "style": style,
            "hook": self._write_hook(topic),
            "body": self._write_body(topic, research_data),
            "cta": self._write_cta(topic),
            "scenes": self._break_into_scenes(topic, research_data),
        }
        
        return script_data
    
    def _write_hook(self, topic: str) -> str:
        """
        Write attention-grabbing hook (first 3-5 seconds)
        Goal: Stop the scroll
        """
        
        prompt = f"""Write a 2-3 sentence attention-grabbing HOOK for a YouTube video about: {topic}

Requirements:
- Must create curiosity/urgency
- Must stop someone from scrolling
- Short and punchy (3-5 seconds to read)
- No fluff, straight to intrigue
- Can use statements like "Wait until...", "You won't believe...", "This changed everything..."

Format: Just the hook text, nothing else."""
        
        return self.llm.generate(prompt, temperature=0.9).strip()
    
    def _write_body(self, topic: str, research_data: Dict) -> str:
        """
        Write the main body of the script
        Incorporates research data and maintains engagement
        """
        
        # Prepare research summary
        key_points = "\n".join(
            f"- {point}" 
            for point in research_data.get('key_points', [])[:5]
        )
        
        prompt = f"""Write the MAIN BODY of a YouTube video script about: {topic}

Duration: ~{self.video_duration - 60} seconds (for ~300 words)

Key points to cover:
{key_points}

Requirements:
- Hook them in first sentence
- Build momentum
- Use storytelling techniques
- Make it conversational (as if speaking to camera)
- Include surprising/shocking facts
- Maintain high retention
- Flow naturally
- Explain complex things simply

Format: Natural script text, as if narrating to camera."""
        
        return self.llm.generate(prompt, temperature=0.8).strip()
    
    def _write_cta(self, topic: str) -> str:
        """
        Write Call-To-Action for the end of video
        """
        
        prompt = f"""Write a compelling CALL-TO-ACTION (CTA) for the end of a YouTube video about: {topic}

Requirements:
- Should be 10-15 seconds of narration
- Encourage: Like, Subscribe, Comment
- Can ask a question to drive engagement
- Create reason to come back
- Make it feel natural, not salesy

Examples of good CTAs:
"What do YOU think about this? Let me know in the comments!"
"If this blew your mind, smash that subscribe button for more"
"What would you do in this situation? Comment below!"

Format: Just the CTA text."""
        
        return self.llm.generate(prompt, temperature=0.7).strip()
    
    def _break_into_scenes(self, topic: str, research_data: Dict) -> List[Dict]:
        """
        Break script into scenes with visual descriptions
        Each scene corresponds to a part of the video
        """
        
        key_points = "\n".join(
            f"{i+1}. {point}" 
            for i, point in enumerate(research_data.get('key_points', [])[:5])
        )
        
        prompt = f"""Break down a YouTube video about "{topic}" into 5-7 scenes.

Key content points:
{key_points}

For each scene, provide in JSON format:
{{
  "scenes": [
    {{
      "number": 1,
      "title": "Scene title",
      "duration_seconds": 30,
      "narration": "What the narrator says",
      "visual_type": "stock_video|animation|text_overlay|infographic|image",
      "visual_description": "What should be shown on screen"
    }}
  ]
}}

Duration: Each scene 25-45 seconds
Total: 5-7 scenes

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        if isinstance(result, dict) and "scenes" in result:
            return result["scenes"]
        elif isinstance(result, list):
            return result
        
        return []
    
    def format_script(self, script_data: Dict) -> str:
        """Format script data into readable document"""
        
        output = f"\n📝 VIDEO SCRIPT: {script_data['topic'].upper()}\n"
        output += "=" * 70 + "\n"
        output += f"Style: {script_data['style']}\n"
        output += "=" * 70 + "\n"
        
        output += "\n🎬 HOOK (0-5 seconds):\n"
        output += "-" * 70 + "\n"
        output += f"{script_data['hook']}\n"
        
        output += "\n📖 BODY:\n"
        output += "-" * 70 + "\n"
        output += f"{script_data['body']}\n"
        
        output += "\n🎯 SCENE BREAKDOWN:\n"
        output += "-" * 70 + "\n"
        
        for scene in script_data.get('scenes', []):
            output += f"\n📌 Scene {scene.get('number', 1)}: {scene.get('title', 'Untitled')}\n"
            output += f"   Duration: {scene.get('duration_seconds', 30)}s\n"
            output += f"   Visual Type: {scene.get('visual_type', 'unknown')}\n"
            output += f"   Description: {scene.get('visual_description', '')}\n"
            output += f"   Narration: {scene.get('narration', '')}\n"
        
        output += "\n📣 CALL-TO-ACTION (Last 10-15 seconds):\n"
        output += "-" * 70 + "\n"
        output += f"{script_data['cta']}\n"
        
        return output


# Example usage
if __name__ == "__main__":
    from agents.research_agent import ResearchAgent
    
    research_agent = ResearchAgent()
    research = research_agent.research_topic("How AI is Changing Jobs")
    
    writer = ScriptWriterAgent(video_duration=600)
    script = writer.write_script("How AI is Changing Jobs", research)
    
    print(writer.format_script(script))
