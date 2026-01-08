"""
5. Subtitle & Timestamp Agent
Creates time-coded captions (SRT format) for YouTube
"""
import os
from typing import List, Dict, Tuple
import subprocess
import wave
import contextlib


class SubtitleGeneratorAgent:
    """
    Generates SRT (SubRip) subtitle files:
    - Time-coded captions
    - YouTube compatible format
    - Hardcoded subtitle text support
    
    Pairs voiceover with script segments to create accurate timing.
    """
    
    def __init__(self):
        self.subtitle_format = "srt"  # SubRip format
    
    def get_audio_duration(self, audio_file: str) -> float:
        """
        Get duration of audio file in seconds
        """
        try:
            with contextlib.closing(wave.open(audio_file, 'rb')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            print(f"❌ Error reading audio duration: {str(e)}")
            return 0.0
    
    def seconds_to_srt_time(self, seconds: float) -> str:
        """
        Convert seconds to SRT time format: HH:MM:SS,mmm
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def generate_srt_from_script(
        self,
        script_text: str,
        audio_file: str,
        output_srt: str,
        chars_per_second: float = 12.0
    ) -> bool:
        """
        Generate SRT subtitles from script and audio
        
        Args:
            script_text: Full script text
            audio_file: Path to audio file
            output_srt: Path to output SRT file
            chars_per_second: Average reading speed
        
        Returns:
            True if successful
        """
        
        print(f"📝 Generating subtitles...")
        
        try:
            # Get audio duration
            audio_duration = self.get_audio_duration(audio_file)
            if audio_duration == 0:
                print("⚠️  Could not determine audio duration")
                return False
            
            # Split script into subtitle chunks
            # Aim for 2-3 lines per subtitle, ~5-10 seconds each
            chunks = self._chunk_text(script_text)
            
            # Calculate timing
            subtitles = self._calculate_timing(chunks, audio_duration)
            
            # Write SRT file
            success = self._write_srt_file(output_srt, subtitles)
            
            if success:
                print(f"✅ Subtitles generated: {output_srt}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error generating subtitles: {str(e)}")
            return False
    
    def _chunk_text(self, text: str, max_chars_per_chunk: int = 42) -> List[str]:
        """
        Split text into reasonable subtitle chunks
        Respects sentence boundaries
        """
        
        # Replace multiple spaces/newlines with single space
        text = ' '.join(text.split())
        
        # Split by sentences (rough)
        sentences = text.replace('? ', '?|').replace('! ', '!|').split('|')
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            # If adding this sentence exceeds limit, start new chunk
            if len(current_chunk) + len(sentence) > max_chars_per_chunk and current_chunk:
                chunks.append(current_chunk)
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _calculate_timing(
        self,
        chunks: List[str],
        total_duration: float
    ) -> List[Dict]:
        """
        Calculate start and end time for each subtitle chunk
        Distributes chunks evenly across audio duration
        """
        
        subtitles = []
        chunk_duration = total_duration / len(chunks)
        
        for i, chunk in enumerate(chunks):
            start_time = i * chunk_duration
            end_time = (i + 1) * chunk_duration
            
            # Add small overlap for readability
            if i < len(chunks) - 1:
                end_time += 0.2
            
            subtitles.append({
                "index": i + 1,
                "start": self.seconds_to_srt_time(start_time),
                "end": self.seconds_to_srt_time(end_time),
                "text": chunk
            })
        
        return subtitles
    
    def _write_srt_file(self, output_path: str, subtitles: List[Dict]) -> bool:
        """Write subtitles to SRT file"""
        
        try:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for sub in subtitles:
                    f.write(f"{sub['index']}\n")
                    f.write(f"{sub['start']} --> {sub['end']}\n")
                    f.write(f"{sub['text']}\n")
                    f.write("\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error writing SRT file: {str(e)}")
            return False
    
    def generate_hardcoded_subtitles(
        self,
        video_file: str,
        srt_file: str,
        output_video: str,
        subtitle_style: dict = None
    ) -> bool:
        """
        Burn (hardcode) subtitles into video using FFmpeg
        
        Args:
            video_file: Path to input video
            srt_file: Path to SRT subtitle file
            output_video: Path to output video with subtitles
            subtitle_style: Style dictionary
        
        Returns:
            True if successful
        """
        
        print(f"🎬 Hardcoding subtitles into video...")
        
        if subtitle_style is None:
            subtitle_style = {
                "fontsize": 24,
                "fontcolor": "white",
                "borderw": 2,
                "bordercolor": "black",
                "shadowx": 1,
                "shadowy": 1,
            }
        
        try:
            # Build FFmpeg filter for subtitles
            style_str = ":".join([f"{k}={v}" for k, v in subtitle_style.items()])
            filter_str = f"subtitles={srt_file}:{style_str}"
            
            cmd = [
                "ffmpeg",
                "-i", video_file,
                "-vf", filter_str,
                "-c:a", "aac",
                "-y",  # Overwrite
                output_video
            ]
            
            print(f"  Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Subtitles hardcoded: {output_video}")
                return True
            else:
                print(f"❌ Subtitle hardcoding failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error hardcoding subtitles: {str(e)}")
            return False
    
    def export_srt_to_json(self, srt_file: str) -> List[Dict]:
        """Parse SRT file and export as JSON"""
        
        subtitles = []
        
        try:
            with open(srt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                blocks = content.strip().split('\n\n')
                
                for block in blocks:
                    lines = block.strip().split('\n')
                    if len(lines) >= 3:
                        subtitles.append({
                            "index": int(lines[0]),
                            "start": lines[1].split(' --> ')[0],
                            "end": lines[1].split(' --> ')[1],
                            "text": '\n'.join(lines[2:])
                        })
            
            return subtitles
            
        except Exception as e:
            print(f"❌ Error parsing SRT file: {str(e)}")
            return []


# Example usage
if __name__ == "__main__":
    agent = SubtitleGeneratorAgent()
    
    # Example script
    script = """
    Artificial intelligence is changing the world. 
    It's being used in healthcare, finance, and education.
    The technology is advancing rapidly.
    """
    
    # Generate SRT
    agent.generate_srt_from_script(
        script,
        "path/to/audio.wav",
        "/workspaces/yt-agents/output/subtitles/example.srt"
    )
