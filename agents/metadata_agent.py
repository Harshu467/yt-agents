"""
9. Metadata & SEO Agent
Creates YouTube SEO-optimized metadata:
- Title (60 chars max)
- Description (with keywords, links, timestamps)
- Keywords/Tags
- Hashtags
- Thumbnail text hints
"""
from typing import Dict
from utils.llm_client import get_llm_client


class MetadataAgent:
    """
    Generates YouTube metadata optimized for:
    - Click-through rate (CTR)
    - Search discoverability
    - Watch time retention
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.max_title_length = 60
        self.max_tags = 30
    
    def generate_metadata(
        self,
        topic: str,
        script_summary: str,
        key_points: list = None
    ) -> Dict:
        """
        Generate complete YouTube metadata
        
        Args:
            topic: Video topic
            script_summary: Brief summary of video
            key_points: Main points from research
        
        Returns:
            Dictionary with all metadata
        """
        
        print(f"🏷️  Generating YouTube metadata...")
        
        metadata = {
            "title": self._generate_title(topic),
            "description": self._generate_description(topic, script_summary, key_points),
            "tags": self._generate_tags(topic),
            "hashtags": self._generate_hashtags(topic),
            "keywords": self._generate_keywords(topic),
            "thumbnail_text": self._generate_thumbnail_text(topic),
            "category": "Education",
            "language": "en",
            "license": "Standard YouTube License"
        }
        
        return metadata
    
    def _generate_title(self, topic: str) -> str:
        """
        Generate clickable, SEO-friendly title
        
        Rules:
        - Max 60 characters
        - Include keyword early
        - Use power words
        - Create curiosity
        """
        
        prompt = f"""Create 3 YouTube video titles for: {topic}

Requirements:
- Max 60 characters each
- Include power words (Revealed, Secret, Shocking, Insane, etc.)
- Create curiosity and urgency
- Include main keyword
- Start with hook/number if possible

Return only the titles, one per line."""
        
        response = self.llm.generate(prompt, temperature=0.9)
        titles = response.strip().split('\n')[:3]
        
        # Choose the best one (first is usually best)
        best_title = titles[0] if titles else topic
        
        # Trim to 60 chars
        if len(best_title) > self.max_title_length:
            best_title = best_title[:self.max_title_length - 3] + "..."
        
        return best_title.strip()
    
    def _generate_description(
        self,
        topic: str,
        script_summary: str,
        key_points: list = None
    ) -> str:
        """
        Generate SEO-optimized description
        
        YouTube Description Structure:
        1. Hook (first 2-3 lines visible before expand)
        2. Timestamps
        3. Key points
        4. Links/Resources
        5. Social/Subscribe CTA
        6. Keywords naturally scattered
        """
        
        points_str = ""
        if key_points:
            points_str = "\nKey Points:\n" + "\n".join([f"• {point}" for point in key_points[:5]])
        
        prompt = f"""Create a YouTube description for: {topic}

Summary: {script_summary}
{points_str}

Format:
- Start with hook (compelling first line)
- Include timestamps if applicable
- Add key points
- Add relevant links/resources
- End with CTA

Make it SEO-friendly by naturally including related keywords.
Max 5000 characters.

Format as plain text."""
        
        return self.llm.generate(prompt, temperature=0.7).strip()
    
    def _generate_tags(self, topic: str) -> List[str]:
        """
        Generate YouTube tags (max 30, max 500 chars total)
        """
        
        prompt = f"""Generate 15-20 YouTube tags for: {topic}

Tags should:
- Include main topic
- Include long-tail keywords
- Include related searches
- Be specific and searchable
- Include both broad and specific terms

Return only tags, one per line, without hashtags or special characters."""
        
        response = self.llm.generate(prompt, temperature=0.8)
        
        tags = [tag.strip().replace("#", "").lower() for tag in response.strip().split('\n')]
        tags = [tag for tag in tags if tag]  # Remove empty
        tags = tags[:30]  # Max 30 tags
        
        # Ensure total length doesn't exceed 500 chars
        total = 0
        final_tags = []
        for tag in tags:
            if total + len(tag) + 1 <= 500:  # +1 for comma/space
                final_tags.append(tag)
                total += len(tag) + 1
        
        return final_tags
    
    def _generate_hashtags(self, topic: str) -> List[str]:
        """
        Generate hashtags for description/title
        YouTube now uses hashtags more prominently
        """
        
        prompt = f"""Generate 5-7 hashtags for: {topic}

Hashtags should:
- Be relevant and searchable
- Include main topic
- Be specific to content
- Be trending if possible

Return only hashtags, one per line (with # symbol)."""
        
        response = self.llm.generate(prompt, temperature=0.8)
        
        hashtags = response.strip().split('\n')
        hashtags = [h.strip() for h in hashtags if h.strip()]
        
        return hashtags[:7]  # Max 7
    
    def _generate_keywords(self, topic: str) -> List[str]:
        """
        Generate SEO keywords for internal tracking
        """
        
        prompt = f"""Generate 10 SEO keywords for: {topic}

Format: keyword1, keyword2, keyword3...

Focus on:
- Search volume
- User intent
- Long-tail keywords
- Question-based keywords (What, How, Why)"""
        
        response = self.llm.generate(prompt, temperature=0.7)
        
        keywords = [k.strip() for k in response.split(',')]
        keywords = [k for k in keywords if k]
        
        return keywords[:10]
    
    def _generate_thumbnail_text(self, topic: str) -> str:
        """
        Generate text suggestions for video thumbnail
        """
        
        prompt = f"""Generate 3 short text phrases for a YouTube video thumbnail about: {topic}

Requirements:
- Max 3 words each
- High contrast/readable
- Creates curiosity
- Numbers or power words if possible

Return as list."""
        
        response = self.llm.generate(prompt, temperature=0.9)
        
        return response.strip()
    
    def format_metadata(self, metadata: Dict) -> str:
        """Format metadata for easy copying to YouTube"""
        
        output = "\n📋 YOUTUBE METADATA\n"
        output += "=" * 70 + "\n\n"
        
        output += "📌 TITLE (60 chars max):\n"
        output += f"  {metadata['title']}\n"
        output += f"  ({len(metadata['title'])} characters)\n\n"
        
        output += "📝 DESCRIPTION:\n"
        output += "-" * 70 + "\n"
        output += f"{metadata['description']}\n"
        output += "-" * 70 + "\n\n"
        
        output += "🏷️  TAGS (30 max):\n"
        for i, tag in enumerate(metadata['tags'], 1):
            output += f"  {tag}"
            if i < len(metadata['tags']):
                output += ", "
            if i % 5 == 0:
                output += "\n"
        output += "\n\n"
        
        output += "# HASHTAGS:\n"
        for hashtag in metadata['hashtags']:
            output += f"  {hashtag} "
        output += "\n\n"
        
        output += "🎨 THUMBNAIL TEXT:\n"
        output += f"  {metadata['thumbnail_text']}\n\n"
        
        output += "🔑 SEO KEYWORDS:\n"
        output += f"  {', '.join(metadata['keywords'])}\n"
        
        return output


# Example usage
if __name__ == "__main__":
    agent = MetadataAgent()
    
    metadata = agent.generate_metadata(
        "The Rise of AI in 2024",
        "Comprehensive overview of AI trends and applications in 2024",
        ["AI becoming mainstream", "New applications", "Job market impact"]
    )
    
    print(agent.format_metadata(metadata))
