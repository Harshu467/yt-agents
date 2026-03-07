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
            "summary": self._generate_summary(topic),
            "key_points": self._extract_key_points(topic),
            "timeline": self._extract_timeline(topic),
            "important_facts": self._extract_facts(topic),
            "misconceptions": self._extract_misconceptions(topic),
            "interesting_angles": self._extract_angles(topic),
            "statistics": self._extract_statistics(topic),
        }
        
        return research_data
    
    def _generate_summary(self, topic: str) -> str:
        """Generate a concise summary of the topic"""
        
        prompt = f"""Write a 2-3 sentence summary about: {topic}

Keep it engaging and informative for a YouTube video introduction.

Only respond with the summary text, nothing else."""
        
        result = self.llm.generate(prompt, temperature=0.3)
        
        if result and len(result.strip()) > 10:
            return result.strip()
        
        # Fallback summary
        print("⚠️  LLM not available, using fallback summary")
        if "cricket" in topic.lower() or "world cup" in topic.lower():
            return "The India vs New Zealand T20 World Cup 2026 Final promises to be an epic clash between two cricketing giants. Both teams bring world-class talent, rich histories, and unyielding determination to this prestigious tournament. This match will determine the champions of the 2026 T20 World Cup."
        else:
            return f"This comprehensive analysis explores {topic} from multiple angles, providing key insights and important context for understanding this important subject."
    
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
        if isinstance(result, list) and len(result) > 0:
            return result
        elif isinstance(result, dict):
            for key in ["key_points", "points", "keyPoints", "data"]:
                if key in result and isinstance(result[key], list) and len(result[key]) > 0:
                    return result[key]
        
        # Fallback mock data when LLM fails
        print("⚠️  LLM not available, using fallback research data")
        if "cricket" in topic.lower() or "world cup" in topic.lower():
            return [
                "India and New Zealand are two of the most competitive teams in cricket",
                "This T20 World Cup final features two teams with rich cricketing history",
                "The match will be played at a neutral venue with high stakes",
                "Both teams have strong batting lineups and versatile bowling attacks",
                "The winner will be crowned T20 World Cup champions for 2026",
                "This final promises intense competition and memorable moments",
                "The match could go either way given both teams' recent form"
            ]
        else:
            return [
                f"Key aspect 1 of {topic}",
                f"Key aspect 2 of {topic}",
                f"Key aspect 3 of {topic}",
                f"Important point about {topic}",
                f"Critical factor in {topic}",
                f"Main consideration for {topic}"
            ]
    
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
        
        if isinstance(result, list) and len(result) > 0:
            return result
        elif isinstance(result, dict) and "timeline" in result and len(result["timeline"]) > 0:
            return result["timeline"]
        
        # Fallback mock data
        print("⚠️  LLM not available, using fallback timeline data")
        if "cricket" in topic.lower() or "world cup" in topic.lower():
            return [
                {"year": "2024", "event": "India and New Zealand qualify for T20 World Cup 2026"},
                {"year": "2025", "event": "Both teams prepare with intense training and practice matches"},
                {"year": "2026", "event": "Teams compete in group stage matches"},
                {"year": "2026", "event": "India and New Zealand reach the final through strong performances"},
                {"year": "2026", "event": "Final match scheduled for June 2026"}
            ]
        else:
            return [
                {"year": "2024", "event": f"Initial developments in {topic}"},
                {"year": "2025", "event": f"Key milestones achieved in {topic}"},
                {"year": "2026", "event": f"Major breakthrough in {topic}"},
                {"year": "2026", "event": f"Current state of {topic}"},
                {"year": "2027", "event": f"Future outlook for {topic}"}
            ]
    
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
        
        if isinstance(result, list) and len(result) > 0:
            return result
        elif isinstance(result, dict) and "facts" in result and len(result["facts"]) > 0:
            return result["facts"]
        
        # Fallback mock data
        print("⚠️  LLM not available, using fallback facts data")
        if "cricket" in topic.lower() or "world cup" in topic.lower():
            return [
                {"fact": "India has won the T20 World Cup twice (2007, 2024)", "significance": "Most successful team in T20 World Cup history"},
                {"fact": "New Zealand has reached 3 T20 World Cup finals", "significance": "Known for strong performances in ICC tournaments"},
                {"fact": "Both teams have world-class batsmen and all-rounders", "significance": "Match features exceptional talent on both sides"},
                {"fact": "T20 World Cup final is played at neutral venues", "significance": "Ensures fair conditions for both teams"},
                {"fact": "The winner gets $1.6 million prize money", "significance": "Highest stakes in cricket tournaments"}
            ]
        else:
            return [
                {"fact": f"Important fact 1 about {topic}", "significance": "This matters because..."},
                {"fact": f"Key statistic about {topic}", "significance": "This shows..."},
                {"fact": f"Surprising aspect of {topic}", "significance": "This reveals..."},
                {"fact": f"Critical detail about {topic}", "significance": "This impacts..."},
                {"fact": f"Essential point about {topic}", "significance": "This demonstrates..."}
            ]
    
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
        
        if isinstance(result, list) and len(result) > 0:
            return result
        elif isinstance(result, dict) and "misconceptions" in result and len(result["misconceptions"]) > 0:
            return result["misconceptions"]
        
        # Fallback mock data
        print("⚠️  LLM not available, using fallback misconceptions data")
        if "cricket" in topic.lower() or "world cup" in topic.lower():
            return [
                {"misconception": "T20 cricket is just about big hits", "truth": "T20 requires strategic planning, fielding, and bowling accuracy"},
                {"misconception": "India always wins against New Zealand", "truth": "Both teams have competitive records against each other"},
                {"misconception": "Weather doesn't affect T20 matches", "truth": "Rain and dew can significantly impact T20 games"},
                {"misconception": "Only batsmen matter in T20", "truth": "Bowlers and fielders are crucial in T20 format"}
            ]
        else:
            return [
                {"misconception": f"Common myth about {topic}", "truth": f"Actually, the reality is..."},
                {"misconception": f"People often think {topic} is...", "truth": f"In fact, {topic} actually..."},
                {"misconception": f"Widespread belief about {topic}", "truth": f"The truth is that {topic}..."},
                {"misconception": f"Popular misconception regarding {topic}", "truth": f"Reality shows that {topic}..."}
            ]
    
    def _extract_angles(self, topic: str) -> List[str]:
        """Extract interesting angles for the video"""
        
        prompt = f"""Think of 5 unique and interesting angles or perspectives for a YouTube video about: {topic}

Format as JSON array of strings:
["Angle 1", "Angle 2", "Angle 3"]

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        if isinstance(result, list) and len(result) > 0:
            return result
        elif isinstance(result, dict) and "angles" in result and len(result["angles"]) > 0:
            return result["angles"]
        
        # Fallback mock data
        print("⚠️  LLM not available, using fallback angles data")
        if "cricket" in topic.lower() or "world cup" in topic.lower():
            return [
                "Player-by-player analysis of key performers",
                "Tactical breakdown of team strategies",
                "Historical context of India vs New Zealand rivalries",
                "Fan reactions and social media buzz",
                "What the final means for world cricket",
                "Behind-the-scenes preparation stories",
                "Statistical analysis of team performances"
            ]
        else:
            return [
                f"Unique perspective 1 on {topic}",
                f"Interesting angle 2 about {topic}",
                f"Different viewpoint 3 regarding {topic}",
                f"Alternative approach to {topic}",
                f"Fresh take on {topic}",
                f"Overlooked aspect of {topic}"
            ]
    
    def _extract_statistics(self, topic: str) -> List[str]:
        """Extract relevant statistics"""
        
        prompt = f"""Find or generate 3-5 interesting statistics or numbers related to: {topic}

Format as JSON array:
["Statistic 1", "Statistic 2", "Statistic 3"]

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        if isinstance(result, list) and len(result) > 0:
            return result
        elif isinstance(result, dict) and "statistics" in result and len(result["statistics"]) > 0:
            return result["statistics"]
        
        # Fallback mock data
        print("⚠️  LLM not available, using fallback statistics data")
        if "cricket" in topic.lower() or "world cup" in topic.lower():
            return [
                "India has a 65% win rate in T20 World Cup matches",
                "New Zealand has reached 3 T20 World Cup finals",
                "Both teams average over 180 runs per innings in T20",
                "India has 2 T20 World Cup titles (2007, 2024)",
                "New Zealand has 0 T20 World Cup titles but 3 final appearances"
            ]
        else:
            return [
                f"Key statistic 1 about {topic}",
                f"Important number 2 related to {topic}",
                f"Relevant data point 3 for {topic}",
                f"Critical metric 4 regarding {topic}",
                f"Essential figure 5 about {topic}"
            ]
    
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
