"""
7. Video Generator Agent
Creates raw visuals using:
- Stable Diffusion for AI images (free via Replicate or local)
- Stock footage from Pexels/Pixabay (free)
- Text overlays and simple animations
"""
import os
import requests
from typing import List, Dict, Optional
from config import Config


class VideoGeneratorAgent:
    """
    Generates visual content for video:
    - AI images using Stable Diffusion
    - Fetches stock videos from free sources
    - Creates text overlays
    - Generates simple animations
    
    All completely free.
    """
    
    def __init__(self):
        self.pexels_key = Config.PEXELS_API_KEY
        self.pixabay_key = Config.PIXABAY_API_KEY
        self.replicate_token = Config.REPLICATE_API_TOKEN
    
    def generate_ai_image(
        self,
        prompt: str,
        output_path: str,
        width: int = 1920,
        height: int = 1080,
        num_inference_steps: int = 30
    ) -> bool:
        """
        Generate AI image using Stable Diffusion
        
        Free options:
        1. Replicate API (has free credits)
        2. Local Stable Diffusion
        3. HuggingFace Inference API (free tier)
        """
        
        print(f"🖼️  Generating AI image: {prompt[:50]}...")
        
        # Try Replicate first
        if self.replicate_token:
            return self._generate_via_replicate(
                prompt, output_path, width, height
            )
        
        # Fallback to local stable diffusion
        return self._generate_via_local_sd(prompt, output_path)
    
    def _generate_via_replicate(
        self,
        prompt: str,
        output_path: str,
        width: int,
        height: int
    ) -> bool:
        """Generate image using Replicate API (free tier available)"""
        
        try:
            import replicate
            
            # Set token
            os.environ["REPLICATE_API_TOKEN"] = self.replicate_token
            
            # Run Stable Diffusion
            output = replicate.run(
                "stability-ai/stable-diffusion:db21e45d3f7023abc9f30a483f5029cf02d8308b0df89230ba12e848cef7d7f0",
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_inference_steps": 30,
                }
            )
            
            if output:
                # Download image
                img_url = output[0]
                response = requests.get(img_url)
                
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ AI image generated: {output_path}")
                return True
            
        except Exception as e:
            print(f"⚠️  Replicate generation failed: {str(e)}")
        
        return False
    
    def _generate_via_local_sd(self, prompt: str, output_path: str) -> bool:
        """Generate using local Stable Diffusion"""
        
        print("💡 Tip: Install Stable Diffusion locally via:")
        print("   pip install diffusers torch")
        print("   Then this will work completely offline and free!")
        
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            
            print("Loading Stable Diffusion model (first time downloads ~4GB)...")
            
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16,
                use_auth_token=False  # Use free model
            )
            
            # Try to use GPU if available
            try:
                pipe = pipe.to("cuda")
            except:
                pipe = pipe.to("cpu")
                print("⚠️  Using CPU (slower). GPU recommended.")
            
            print(f"Generating: {prompt[:60]}...")
            
            image = pipe(prompt).images[0]
            
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            image.save(output_path)
            
            print(f"✅ AI image generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Local SD generation failed: {str(e)}")
            print("Install with: pip install diffusers torch pillow")
            return False
    
    def fetch_stock_video(
        self,
        keywords: str,
        output_path: str,
        min_duration: int = 10
    ) -> bool:
        """
        Fetch stock video from Pexels or Pixabay
        
        Args:
            keywords: Search keywords
            output_path: Where to save
            min_duration: Minimum duration in seconds
        
        Returns:
            True if successful
        """
        
        print(f"📹 Fetching stock video: {keywords}...")
        
        # Try Pexels first
        if self.pexels_key:
            result = self._fetch_from_pexels(keywords, output_path)
            if result:
                return True
        
        # Try Pixabay
        if self.pixabay_key:
            result = self._fetch_from_pixabay(keywords, output_path)
            if result:
                return True
        
        print("⚠️  No stock video API keys configured")
        return False
    
    def _fetch_from_pexels(self, keywords: str, output_path: str) -> bool:
        """Fetch from Pexels Videos API (free)"""
        
        try:
            url = "https://api.pexels.com/videos/search"
            headers = {"Authorization": self.pexels_key}
            params = {
                "query": keywords,
                "per_page": 1,
                "min_duration": 10,
                "max_duration": 60
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("videos"):
                    video = data["videos"][0]
                    video_url = video["video_files"][0]["link"]
                    
                    # Download video
                    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                    
                    video_response = requests.get(video_url)
                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)
                    
                    print(f"✅ Stock video downloaded: {output_path}")
                    return True
                else:
                    print(f"⚠️  No videos found for: {keywords}")
                    return False
            else:
                print(f"❌ Pexels API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Pexels fetch error: {str(e)}")
            return False
    
    def _fetch_from_pixabay(self, keywords: str, output_path: str) -> bool:
        """Fetch from Pixabay Videos API (free)"""
        
        try:
            url = "https://pixabay.com/api/videos"
            params = {
                "key": self.pixabay_key,
                "q": keywords,
                "per_page": 1,
                "min_duration": 10,
                "max_duration": 60
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("hits"):
                    video = data["hits"][0]
                    # Get smallest video file
                    video_url = video["videos"]["small"]["url"]
                    
                    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                    
                    video_response = requests.get(video_url)
                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)
                    
                    print(f"✅ Stock video downloaded: {output_path}")
                    return True
                else:
                    print(f"⚠️  No videos found for: {keywords}")
                    return False
            else:
                print(f"❌ Pixabay API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Pixabay fetch error: {str(e)}")
            return False
    
    def fetch_stock_image(
        self,
        keywords: str,
        output_path: str
    ) -> bool:
        """
        Fetch stock image from Pexels or Pixabay
        """
        
        print(f"🖼️  Fetching stock image: {keywords}...")
        
        # Try Pexels first
        if self.pexels_key:
            result = self._fetch_image_pexels(keywords, output_path)
            if result:
                return True
        
        # Try Pixabay
        if self.pixabay_key:
            result = self._fetch_image_pixabay(keywords, output_path)
            if result:
                return True
        
        print("⚠️  No stock image API keys configured")
        return False
    
    def _fetch_image_pexels(self, keywords: str, output_path: str) -> bool:
        """Fetch image from Pexels API (free)"""
        
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_key}
            params = {
                "query": keywords,
                "per_page": 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("photos"):
                    photo = data["photos"][0]
                    image_url = photo["src"]["large2x"]
                    
                    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                    
                    image_response = requests.get(image_url)
                    with open(output_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    print(f"✅ Stock image downloaded: {output_path}")
                    return True
                else:
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"❌ Pexels image fetch error: {str(e)}")
            return False
    
    def _fetch_image_pixabay(self, keywords: str, output_path: str) -> bool:
        """Fetch image from Pixabay API (free)"""
        
        try:
            url = "https://pixabay.com/api"
            params = {
                "key": self.pixabay_key,
                "q": keywords,
                "per_page": 1
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("hits"):
                    image = data["hits"][0]
                    image_url = image["largeImageURL"]
                    
                    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                    
                    image_response = requests.get(image_url)
                    with open(output_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    print(f"✅ Stock image downloaded: {output_path}")
                    return True
                else:
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"❌ Pixabay image fetch error: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    agent = VideoGeneratorAgent()
    
    # Generate AI image
    agent.generate_ai_image(
        "A cinematic shot of artificial intelligence, glowing neon, futuristic",
        "/workspaces/yt-agents/output/ai_image_sample.png"
    )
    
    # Fetch stock video (needs API keys in .env)
    # agent.fetch_stock_video("technology", "/workspaces/yt-agents/output/stock_video.mp4")
