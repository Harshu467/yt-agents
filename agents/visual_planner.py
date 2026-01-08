"""
6. Visual Scene Planner Agent
Converts script scenes into visual descriptions and asset lists
"""
from typing import Dict, List
from utils.llm_client import get_llm_client


class VisualScenePlannerAgent:
    """
    Maps each script scene to visual content:
    - Determines visual type (video, image, animation, text)
    - Creates detailed visual descriptions
    - Lists required assets
    - Suggests motion/transitions
    
    Output is used by Video Generator Agent to create actual visuals.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        
        # Visual types available
        self.visual_types = [
            "stock_video",      # Free stock footage
            "ai_image",         # Generated via Stable Diffusion
            "stock_image",      # From Pexels/Pixabay
            "animation",        # Motion graphics
            "text_overlay",     # Text on solid background
            "infographic",      # Data visualization
            "screen_recording", # Demo/tutorial
            "montage",          # Multiple clips together
        ]
    
    def plan_visuals(self, scenes: List[Dict]) -> List[Dict]:
        """
        Plan visuals for each scene
        
        Args:
            scenes: Scene data from Script Writer Agent
        
        Returns:
            Enhanced scenes with visual plans
        """
        
        print("🎨 Planning visuals for each scene...")
        
        visual_plan = []
        
        for scene in scenes:
            visual_data = self._plan_scene_visuals(scene)
            visual_plan.append(visual_data)
        
        return visual_plan
    
    def _plan_scene_visuals(self, scene: Dict) -> Dict:
        """Plan visuals for a single scene"""
        
        narration = scene.get("narration", "")
        title = scene.get("title", "")
        
        prompt = f"""Plan the visuals for a YouTube video scene:

Scene Title: {title}
Narration: {narration}

Respond with JSON:
{{
  "visual_type": "one of: stock_video|ai_image|stock_image|animation|text_overlay|infographic|screen_recording|montage",
  "visual_description": "Detailed description of what should be shown (5-7 sentences)",
  "search_keywords": ["keyword1", "keyword2", "keyword3"],
  "motion_description": "What movement/transition should happen? (pan, zoom, fade, etc.)",
  "suggested_assets": ["specific stock footage/image to search for"],
  "duration_seconds": 30,
  "color_scheme": "dominant colors (e.g., blue and gold)",
  "style": "photography|animation|3d|illustrated|cinematic",
  "notes": "Any special requirements or notes"
}}

Only respond with valid JSON."""
        
        result = self.llm.extract_json(prompt)
        
        # Merge with original scene data
        return {
            **scene,
            "visuals": result
        }
    
    def generate_asset_list(self, visual_plan: List[Dict]) -> Dict:
        """
        Generate comprehensive asset list for video production
        
        Returns:
            Dictionary of all required assets organized by type
        """
        
        assets = {
            "stock_videos": [],
            "stock_images": [],
            "ai_generated_images": [],
            "text_elements": [],
            "music_needed": [],
            "sfx_needed": [],
            "animations": [],
        }
        
        for scene in visual_plan:
            visuals = scene.get("visuals", {})
            visual_type = visuals.get("visual_type", "")
            
            if visual_type == "stock_video":
                assets["stock_videos"].extend(
                    visuals.get("suggested_assets", [])
                )
            elif visual_type == "stock_image":
                assets["stock_images"].extend(
                    visuals.get("suggested_assets", [])
                )
            elif visual_type == "ai_image":
                assets["ai_generated_images"].append({
                    "description": visuals.get("visual_description", ""),
                    "keywords": visuals.get("search_keywords", []),
                    "style": visuals.get("style", "cinematic")
                })
            elif visual_type == "animation":
                assets["animations"].append({
                    "description": visuals.get("visual_description", ""),
                    "motion": visuals.get("motion_description", "")
                })
            elif visual_type == "text_overlay":
                assets["text_elements"].append({
                    "text": scene.get("narration", ""),
                    "duration": visuals.get("duration_seconds", 30)
                })
            elif visual_type == "infographic":
                assets["ai_generated_images"].append({
                    "description": f"Infographic: {visuals.get('visual_description', '')}",
                    "type": "infographic"
                })
        
        return assets
    
    def generate_storyboard_text(self, visual_plan: List[Dict]) -> str:
        """Generate text storyboard document"""
        
        output = "\n📊 VISUAL STORYBOARD\n"
        output += "=" * 70 + "\n"
        
        for scene in visual_plan:
            scene_num = scene.get("number", 1)
            title = scene.get("title", "Untitled")
            
            output += f"\n[SCENE {scene_num}] {title}\n"
            output += "-" * 70 + "\n"
            
            visuals = scene.get("visuals", {})
            
            output += f"Duration: {visuals.get('duration_seconds', 30)}s\n"
            output += f"Visual Type: {visuals.get('visual_type', 'unknown')}\n"
            output += f"Style: {visuals.get('style', 'unknown')}\n"
            output += f"Colors: {visuals.get('color_scheme', 'standard')}\n\n"
            
            output += "Visual Description:\n"
            output += f"  {visuals.get('visual_description', 'N/A')}\n\n"
            
            output += "Narration:\n"
            output += f"  {scene.get('narration', 'N/A')}\n\n"
            
            output += "Motion/Transition:\n"
            output += f"  {visuals.get('motion_description', 'standard fade')}\n\n"
            
            if visuals.get('suggested_assets'):
                output += "Assets Needed:\n"
                for asset in visuals.get('suggested_assets', []):
                    output += f"  • {asset}\n"
                output += "\n"
        
        return output


# Example usage
if __name__ == "__main__":
    agent = VisualScenePlannerAgent()
    
    # Example scene from script writer
    example_scene = {
        "number": 1,
        "title": "Introduction",
        "duration_seconds": 30,
        "narration": "Welcome to the world of artificial intelligence...",
        "visual_type": "animation"
    }
    
    visual_plan = agent.plan_visuals([example_scene])
    print(agent.generate_storyboard_text(visual_plan))
