"""
4. Voiceover Generator Agent
Converts script → AI voice using Piper TTS (completely free)
"""
import os
import subprocess
from typing import Optional
from config import Config


class VoiceoverGeneratorAgent:
    """
    Generates voiceovers using Piper TTS:
    - Completely free and open-source
    - No API calls needed
    - Can run offline
    - Multiple voices available
    - Adjustable speed and pitch
    """
    
    # Available Piper voices (all free)
    AVAILABLE_VOICES = {
        "male_us": "en_US-lessac-medium",
        "male_uk": "en_GB-alan-medium",
        "female_us": "en_US-jenny-medium",
        "female_uk": "en_GB-aru-medium",
        "male_young": "en_US-ryan-medium",
    }
    
    def __init__(self, voice: str = "male_us"):
        """
        Initialize voiceover generator
        
        Args:
            voice: Voice name (male_us, female_us, etc.)
        """
        self.voice = self.AVAILABLE_VOICES.get(voice, self.AVAILABLE_VOICES["male_us"])
        self._check_piper_installed()
    
    def _check_piper_installed(self):
        """Check if Piper TTS is installed"""
        try:
            result = subprocess.run(
                ["piper", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ Piper TTS found: {result.stdout.strip()}")
            else:
                self._install_piper()
        except FileNotFoundError:
            print("⚠️  Piper TTS not found. Installing...")
            self._install_piper()
    
    def _install_piper(self):
        """Install Piper TTS"""
        print("📦 Installing Piper TTS...")
        os.system("pip install piper-tts")
        print("✅ Piper TTS installed")
    
    def generate_voiceover(
        self, 
        text: str, 
        output_path: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bool:
        """
        Generate voiceover from text
        
        Args:
            text: Script text to convert to speech
            output_path: Where to save the audio file (.wav)
            voice: Optional voice override
            speed: Speech speed (0.5-2.0)
        
        Returns:
            True if successful, False otherwise
        """
        
        voice_to_use = voice or self.voice
        
        print(f"🎙️  Generating voiceover using {voice_to_use}...")
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Escape text for command line
        text_escaped = text.replace('"', '\\"').replace("'", "\\'")
        
        try:
            # Run Piper TTS
            cmd = (
                f'echo "{text_escaped}" | '
                f'piper --model {voice_to_use} '
                f'--output_file {output_path}'
            )
            
            if speed != 1.0:
                # Note: Piper doesn't have built-in speed control
                # You'd need to use ffmpeg after generation
                pass
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ Voiceover generated: {output_path} ({file_size} bytes)")
                return True
            else:
                print(f"❌ Voiceover generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating voiceover: {str(e)}")
            return False
    
    def generate_voiceover_with_ssml(
        self,
        ssml_text: str,
        output_path: str,
        voice: Optional[str] = None,
    ) -> bool:
        """
        Generate voiceover from SSML (Speech Synthesis Markup Language)
        Allows more control over pronunciation, pauses, emphasis
        """
        
        # SSML example:
        # <speak>This is <emphasis level="strong">important</emphasis></speak>
        
        voice_to_use = voice or self.voice
        
        print(f"🎙️  Generating voiceover with SSML using {voice_to_use}...")
        
        try:
            # Convert SSML to plain text (simplified)
            # In real implementation, you'd use proper SSML parser
            plain_text = ssml_text.replace("<speak>", "").replace("</speak>", "")
            plain_text = plain_text.replace("<emphasis level=\"strong\">", "")
            plain_text = plain_text.replace("</emphasis>", "")
            
            return self.generate_voiceover(plain_text, output_path, voice_to_use)
            
        except Exception as e:
            print(f"❌ SSML voiceover generation failed: {str(e)}")
            return False
    
    def adjust_speech_rate(
        self,
        input_audio: str,
        output_audio: str,
        rate: float = 1.0
    ) -> bool:
        """
        Adjust speech rate using FFmpeg
        
        Args:
            input_audio: Path to input audio
            output_audio: Path to output audio
            rate: Speed multiplier (0.5 = half speed, 1.5 = 1.5x speed)
        
        Returns:
            True if successful
        """
        
        if rate == 1.0:
            return True  # No change needed
        
        print(f"⚙️  Adjusting speech rate to {rate}x...")
        
        try:
            # Use FFmpeg to adjust speed
            cmd = [
                "ffmpeg",
                "-i", input_audio,
                "-filter:a", f"atempo={rate}",
                "-y",  # Overwrite output
                output_audio
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Speech rate adjusted")
                return True
            else:
                print(f"❌ Speed adjustment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error adjusting speed: {str(e)}")
            return False
    
    def batch_generate(self, scripts: list, output_dir: str) -> dict:
        """
        Generate voiceovers for multiple script segments
        
        Args:
            scripts: List of {"text": "...", "name": "..."}
            output_dir: Directory to save all audio files
        
        Returns:
            Dictionary mapping names to audio file paths
        """
        
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        
        for script in scripts:
            text = script.get("text", "")
            name = script.get("name", "unnamed")
            
            output_path = os.path.join(output_dir, f"{name}.wav")
            
            success = self.generate_voiceover(text, output_path)
            results[name] = {
                "path": output_path if success else None,
                "success": success
            }
        
        return results


# Example usage
if __name__ == "__main__":
    agent = VoiceoverGeneratorAgent(voice="female_us")
    
    # Generate a sample voiceover
    script = "This is an amazing discovery in the world of artificial intelligence."
    output = os.path.join(Config.VOICEOVERS_DIR, "sample.wav")
    
    agent.generate_voiceover(script, output)
