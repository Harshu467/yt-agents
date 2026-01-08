"""
LLM Client - Interface to Ollama for all AI tasks
"""
import aiohttp
import asyncio
import requests
from typing import Optional
from config import Config

class LLMClient:
    """
    Client for interacting with Ollama local LLM
    All inference is local and completely FREE
    """
    
    def __init__(self, model: str = None, base_url: str = None, provider: str = "ollama"):
        """
        provider: 'ollama' (default) or 'nvideo' for NVidia-compatible endpoints
        """
        self.provider = provider
        self.model = model or Config.OLLAMA_MODEL
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.endpoint = f"{self.base_url}/api/generate"
        # If nvideo is enabled in config, prefer that provider
        if Config.NVIDEO_ENABLED and Config.NVIDEO_API_URL:
            self.provider = "nvideo"
            self.nvideo_endpoint = Config.NVIDEO_API_URL
    
    def generate(self, prompt: str, stream: bool = False, temperature: float = 0.7) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: Input prompt
            stream: Whether to stream response
            temperature: Creativity level (0-1)
        
        Returns:
            Generated text
        """
        try:
            if self.provider == "nvideo":
                # Generic POST to nvideo-compatible endpoint. API specifics vary,
                # so we attempt a best-effort JSON contract: {model, prompt, temperature}
                if not hasattr(self, 'nvideo_endpoint') or not self.nvideo_endpoint:
                    print("❌ nvideo endpoint not configured. Set NVIDEO_API_URL in .env")
                    return ""
                payload = {
                    "model": Config.NVIDEO_MODEL_NAME,
                    "prompt": prompt,
                    "temperature": temperature,
                }
                response = requests.post(self.nvideo_endpoint, json=payload, timeout=300)
                if response.status_code == 200:
                    try:
                        return response.json().get("response", response.text)
                    except:
                        return response.text
                else:
                    print(f"❌ nvideo Error: {response.status_code}")
                    return ""
            else:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": stream,
                    "temperature": temperature,
                }
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    timeout=300  # 5 minute timeout for long generations
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    print(f"❌ LLM Error: {response.status_code}")
                    return ""
        except requests.exceptions.ConnectionError:
            if self.provider == "ollama":
                print("❌ ERROR: Cannot connect to Ollama. Is it running?")
                print("   Install from https://ollama.ai and run: ollama serve")
            else:
                print("❌ ERROR: Cannot connect to nvideo endpoint. Check NVIDEO_API_URL and network.")
            return ""
        except Exception as e:
            print(f"❌ LLM Error: {str(e)}")
            return ""
    
    async def generate_async(self, prompt: str, temperature: float = 0.7) -> str:
        """Async version of generate"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.generate, 
            prompt, 
            False, 
            temperature
        )
    
    def extract_json(self, prompt: str) -> dict:
        """
        Generate JSON response from LLM
        Useful for structured data extraction
        """
        json_prompt = f"""{prompt}

You MUST respond with ONLY valid JSON, no other text."""
        
        response = self.generate(json_prompt, temperature=0.2)
        
        # Try to extract JSON from response
        try:
            import json
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return {}


class EmbeddingClient:
    """
    Client for generating embeddings (for semantic search, similarity, etc.)
    Using Ollama's embedding model
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.endpoint = f"{self.base_url}/api/embeddings"
        self.model = "nomic-embed-text"  # Free embedding model
    
    def embed(self, text: str) -> list:
        """Generate embedding for text"""
        try:
            payload = {
                "model": self.model,
                "prompt": text,
            }
            
            response = requests.post(self.endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                return response.json().get("embedding", [])
            else:
                return []
                
        except Exception as e:
            print(f"❌ Embedding Error: {str(e)}")
            return []


# Singleton instances
_llm_client = None
_embedding_client = None

def get_llm_client() -> LLMClient:
    """Get or create LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

def get_embedding_client() -> EmbeddingClient:
    """Get or create embedding client instance"""
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = EmbeddingClient()
    return _embedding_client
