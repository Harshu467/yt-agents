"""
11. Thumbnail Generator Agent
Creates cinematic, AI-powered thumbnails using Stable Diffusion
"""
import os
from typing import Optional
from config import Config
from agents.video_generator import VideoGeneratorAgent


class ThumbnailGeneratorAgent:
    """
    Creates YouTube thumbnails using Stable Diffusion:
    - AI-generated cinematic images
    - Text overlay support
    - YouTube-optimized dimensions (1280x720)
    - High contrast for small previews
    """
    
    def __init__(self):
        self.video_gen = VideoGeneratorAgent()
        self.thumbnail_width = 1280
        self.thumbnail_height = 720
    
    def generate_thumbnail(
        self,
        topic: str,
        style: str = "cinematic",
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate AI thumbnail for video topic
        
        Args:
            topic: Video topic
            style: cinematic|movie|dramatic|colorful
            output_path: Where to save thumbnail
        
        Returns:
            Path to thumbnail if successful
        """
        
        if not output_path:
            output_path = os.path.join(
                Config.THUMBNAILS_DIR,
                f"{topic[:30].replace(' ', '_')}_thumb.png"
            )
        
        print(f"🎨 Generating thumbnail for: {topic}")
        
        # Create compelling prompt
        prompt = self._create_thumbnail_prompt(topic, style)
        
        # Generate image
        success = self.video_gen.generate_ai_image(
            prompt=prompt,
            output_path=output_path,
            width=self.thumbnail_width,
            height=self.thumbnail_height
        )
        
        if success:
            print(f"✅ Thumbnail generated: {output_path}")
            return output_path
        else:
            print(f"❌ Thumbnail generation failed")
            return None
    
    def _create_thumbnail_prompt(self, topic: str, style: str) -> str:
        """
        Create detailed prompt for Stable Diffusion
        YouTube thumbnails need:
        - High contrast
        - Clear focal point
        - Engaging visuals
        - Cinematic quality
        """
        
        style_descriptions = {
            "cinematic": "cinematic lighting, dramatic shadows, high contrast, professional photography",
            "movie": "movie poster style, bold colors, dramatic composition, Avengers-like",
            "dramatic": "dramatic composition, intense emotions, powerful visuals, dark moody lighting",
            "colorful": "vibrant colors, saturated, eye-catching, neon accents, bold design"
        }
        
        style_desc = style_descriptions.get(style, style_descriptions["cinematic"])
        
        prompt = f"""
        YouTube video thumbnail for: {topic}
        
        Style: {style_desc}
        
        Requirements:
        - High contrast colors (easy to see at small size)
        - Clear focal point (centered)
        - Engaging and clickable design
        - Professional quality
        - No text (will be added separately)
        - 16:9 aspect ratio
        - Bold, saturated colors
        - Cinematic composition
        
        Make it look like a movie poster or Hollywood trailer thumbnail.
        """
        
        return prompt.strip()
    
    def add_text_to_thumbnail(
        self,
        thumbnail_path: str,
        text: str,
        output_path: str,
        text_position: str = "center",
        font_size: int = 60
    ) -> bool:
        """
        Add text overlay to thumbnail using PIL
        
        Args:
            thumbnail_path: Input thumbnail image
            text: Text to add
            output_path: Output image
            text_position: center|top|bottom|top-left|top-right|bottom-left|bottom-right
            font_size: Font size in pixels
        
        Returns:
            True if successful
        """
        
        print(f"📝 Adding text to thumbnail...")
        
        try:
            from PIL import Image, ImageDraw, ImageFont, ImageFilter
            
            # Open image
            img = Image.open(thumbnail_path)
            width, height = img.size
            
            # Create draw object
            draw = ImageDraw.Draw(img)
            
            # Try to load a good font (fallback to default)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position
            positions = {
                "center": ((width - text_width) // 2, (height - text_height) // 2),
                "top": ((width - text_width) // 2, 20),
                "bottom": ((width - text_width) // 2, height - text_height - 20),
                "top-left": (20, 20),
                "top-right": (width - text_width - 20, 20),
                "bottom-left": (20, height - text_height - 20),
                "bottom-right": (width - text_width - 20, height - text_height - 20),
            }
            
            position = positions.get(text_position, positions["center"])
            
            # Add text with outline (for visibility)
            # Draw outline
            for adj_x in [-2, -1, 0, 1, 2]:
                for adj_y in [-2, -1, 0, 1, 2]:
                    if adj_x != 0 or adj_y != 0:
                        draw.text(
                            (position[0] + adj_x, position[1] + adj_y),
                            text,
                            font=font,
                            fill="black"
                        )
            
            # Draw main text
            draw.text(position, text, font=font, fill="white")
            
            # Save
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            img.save(output_path, "PNG", quality=95)
            
            print(f"✅ Text added to thumbnail: {output_path}")
            return True
            
        except ImportError:
            print("⚠️  PIL not installed. Install with: pip install Pillow")
            return False
        except Exception as e:
            print(f"❌ Error adding text: {str(e)}")
            return False
    
    def create_thumbnail_from_video_frame(
        self,
        video_path: str,
        timestamp_seconds: float,
        output_path: str
    ) -> bool:
        """
        Extract and use frame from video as thumbnail
        
        Args:
            video_path: Path to video file
            timestamp_seconds: Frame to extract
            output_path: Output thumbnail
        
        Returns:
            True if successful
        """
        
        print(f"📽️  Extracting frame from video at {timestamp_seconds}s...")
        
        try:
            import subprocess
            
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            
            # Use FFmpeg to extract frame
            cmd = [
                "ffmpeg",
                "-ss", str(timestamp_seconds),
                "-i", video_path,
                "-vframes", "1",
                "-vf", "scale=1280:720",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Frame extracted: {output_path}")
                return True
            else:
                print(f"❌ Frame extraction failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error extracting frame: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    agent = ThumbnailGeneratorAgent()
    
    # Generate AI thumbnail
    thumb_path = agent.generate_thumbnail(
        topic="The Future of Artificial Intelligence",
        style="movie"
    )
    
    # Add text
    if thumb_path:
        agent.add_text_to_thumbnail(
            thumbnail_path=thumb_path,
            text="SHOCKING TRUTHS",
            output_path="/workspaces/yt-agents/output/thumbnails/final_thumb.png",
            text_position="bottom",
            font_size=60
        )
