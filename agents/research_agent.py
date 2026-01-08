"""
2. Research & Context Agent
Expands chosen topic into accurate, factual points and context
"""
import json
from typing import Dict, List
from utils.llm_client import get_llm_client


class ResearchAgent:
    """
    Converts a topic into comprehensive research:
    - Key points
    - Timeline/history
    - Important facts
    - Common misconceptions
    - Interesting angles
    
    Uses local Ollama LLM for all research.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
    
    def research_topic(self, topic: str) -> Dict:
        """
        Comprehensive research on a topic
        
        Args:
            topic: The topic to research
        
        Returns:
            Dictionary with all research data
        """
        print(f"📚 Researching: {topic}")
        
        research_data = {
            "topic": topic,
            "key_points": self._extract_key_points(topic),
            "timeline": self._extract_timeline(topic),
            "important_facts": self._extract_facts(topic),
            "misconceptions": self._extract_misconceptions(topic),
            "interesting_angles": self._extract_angles(topic),
            "statistics": self._extract_statistics(topic),
        }
        
        return research_data
    
    def _extract_key_points(self, topic: str) -> List[str]:
        """Extract 5-7 key points about the topic"""
        
        prompt = f"""Research the following topic and provide 5-7 key points that would be interesting for a YouTube video:

Topic: {topic}

Format your response as a JSON array of strings, where each string is a key point.
Only respond with valid JSON, nothing else.

Example format:
["Point 1", "Point 2", "Point 3"]"""
        
        result = self.llm.extract_json(prompt)
        
        # Try to get array from various possible keys
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            for key in ["key_points", "points", "keyPoints", "data"]:
                if key in result and isinstance(result[key], list):
                    return result[key]
        
        return []
    
    def _extract_timeline(self, topic: str) -> List[Dict]:
        """Extract timeline/historical events"""
        
        prompt = f"""Create a timeline of important events related to: {topic}

Provide the 5 most important historical points or milestones.

Format as JSON array:
[
  {{"year": "2020", "event": "Description"}},
  {{"year": "2021", "event": "Description"}}
]

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "timeline" in result:
            return result["timeline"]
        
        return []
    
    def _extract_facts(self, topic: str) -> List[Dict]:
        """Extract important facts and statistics"""
        
        prompt = f"""List 5-7 surprising or important facts about: {topic}

Format as JSON array:
[
  {{"fact": "Description", "significance": "Why this matters"}},
  {{"fact": "Another fact", "significance": "Why this matters"}}
]

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "facts" in result:
            return result["facts"]
        
        return []
    
    def _extract_misconceptions(self, topic: str) -> List[Dict]:
        """Extract common misconceptions"""
        
        prompt = f"""What are the top 3-5 misconceptions people have about: {topic}

For each, explain:
1. The misconception
2. The truth/reality

Format as JSON array:
[
  {{"misconception": "People think...", "truth": "Actually..."}},
  {{"misconception": "People think...", "truth": "Actually..."}}
]

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "misconceptions" in result:
            return result["misconceptions"]
        
        return []
    
    def _extract_angles(self, topic: str) -> List[str]:
        """Extract interesting angles for the video"""
        
        prompt = f"""Think of 5 unique and interesting angles or perspectives for a YouTube video about: {topic}

Format as JSON array of strings:
["Angle 1", "Angle 2", "Angle 3"]

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "angles" in result:
            return result["angles"]
        
        return []
    
    def _extract_statistics(self, topic: str) -> List[str]:
        """Extract relevant statistics"""
        
        prompt = f"""Find or generate 3-5 interesting statistics or numbers related to: {topic}

Format as JSON array:
["Statistic 1", "Statistic 2", "Statistic 3"]

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "statistics" in result:
            return result["statistics"]
        
        return []
    
    def format_research(self, research_data: Dict) -> str:
        """Format research data into readable text"""
        
        output = f"\n📖 RESEARCH REPORT: {research_data['topic']}\n"
        output += "=" * 60 + "\n"
        
        if research_data.get('key_points'):
            output += "\n🔑 KEY POINTS:\n"
            for i, point in enumerate(research_data['key_points'][:7], 1):
                output += f"  {i}. {point}\n"
        
        if research_data.get('timeline'):
            output += "\n⏰ TIMELINE:\n"
            for event in research_data['timeline']:
                year = event.get('year', 'Unknown')
                event_text = event.get('event', '')
                output += f"  {year}: {event_text}\n"
        
        if research_data.get('important_facts'):
            output += "\n💡 IMPORTANT FACTS:\n"
            for fact in research_data['important_facts']:
                fact_text = fact.get('fact', '')
                sig = fact.get('significance', '')
                output += f"  • {fact_text}\n"
                if sig:
                    output += f"    └─ {sig}\n"
        
        if research_data.get('misconceptions'):
            output += "\n❌ COMMON MISCONCEPTIONS:\n"
            for misc in research_data['misconceptions']:
                output += f"  ❌ WRONG: {misc.get('misconception', '')}\n"
                output += f"  ✅ RIGHT: {misc.get('truth', '')}\n"
        
        if research_data.get('interesting_angles'):
            output += "\n📐 VIDEO ANGLES:\n"
            for angle in research_data['interesting_angles']:
                output += f"  • {angle}\n"
        
        if research_data.get('statistics'):
            output += "\n📊 STATISTICS:\n"
            for stat in research_data['statistics']:
                output += f"  • {stat}\n"
        
        return output


# Example usage
if __name__ == "__main__":
    agent = ResearchAgent()
    research = agent.research_topic("Artificial Intelligence in 2024")
    print(agent.format_research(research))
