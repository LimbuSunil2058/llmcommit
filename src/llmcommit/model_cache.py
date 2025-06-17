"""File-based model caching system."""

import os
import json
import time
import hashlib
import pickle
from pathlib import Path
from typing import Dict, Any, Optional


class ModelCache:
    """File-based cache for model outputs."""
    
    def __init__(self, cache_dir: str = None):
        """Initialize cache with directory."""
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.cache/llmcommit")
        
        self.cache_dir = Path(cache_dir)
        self.outputs_dir = self.cache_dir / "outputs"
        self.models_dir = self.cache_dir / "models"
        
        # Create directories
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata."""
        if self.metadata_file.exists():
            try:
                return json.loads(self.metadata_file.read_text())
            except:
                return {}
        return {}
        
    def _save_metadata(self):
        """Save cache metadata."""
        self.metadata_file.write_text(json.dumps(self.metadata, indent=2))
        
    def get_cache_key(self, diff: str, model: str) -> str:
        """Generate cache key from diff and model."""
        content = f"{model}:{diff[:500]}"  # Limit diff size
        return hashlib.sha256(content.encode()).hexdigest()[:16]
        
    def get_cached_message(self, diff: str, model: str) -> Optional[str]:
        """Get cached commit message if exists."""
        key = self.get_cache_key(diff, model)
        cache_file = self.outputs_dir / f"{key}.txt"
        
        if cache_file.exists():
            # Check if cache is still valid (24 hours)
            age = time.time() - cache_file.stat().st_mtime
            if age < 86400:  # 24 hours
                return cache_file.read_text()
                
        return None
        
    def save_message(self, diff: str, model: str, message: str):
        """Save generated message to cache."""
        key = self.get_cache_key(diff, model)
        cache_file = self.outputs_dir / f"{key}.txt"
        cache_file.write_text(message)
        
        # Update metadata
        self.metadata[key] = {
            "model": model,
            "timestamp": time.time(),
            "diff_size": len(diff)
        }
        self._save_metadata()
        
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get cached model loading info."""
        model_key = model_name.replace("/", "--")
        info_file = self.models_dir / f"{model_key}.json"
        
        if info_file.exists():
            try:
                return json.loads(info_file.read_text())
            except:
                pass
        return None
        
    def save_model_info(self, model_name: str, info: Dict[str, Any]):
        """Save model loading information."""
        model_key = model_name.replace("/", "--")
        info_file = self.models_dir / f"{model_key}.json"
        info_file.write_text(json.dumps(info, indent=2))
        
    def clear_old_cache(self, days: int = 7):
        """Clear cache entries older than specified days."""
        cutoff_time = time.time() - (days * 86400)
        
        # Clear old output files
        for cache_file in self.outputs_dir.glob("*.txt"):
            if cache_file.stat().st_mtime < cutoff_time:
                cache_file.unlink()
                
        # Update metadata
        new_metadata = {}
        for key, info in self.metadata.items():
            if info.get("timestamp", 0) >= cutoff_time:
                new_metadata[key] = info
                
        self.metadata = new_metadata
        self._save_metadata()
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_files = len(list(self.outputs_dir.glob("*.txt")))
        total_size = sum(f.stat().st_size for f in self.outputs_dir.glob("*.txt"))
        
        model_stats = {}
        for key, info in self.metadata.items():
            model = info.get("model", "unknown")
            if model not in model_stats:
                model_stats[model] = 0
            model_stats[model] += 1
            
        return {
            "total_entries": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "models": model_stats,
            "cache_dir": str(self.cache_dir)
        }


class CachedLLMClient:
    """LLM client with file-based caching."""
    
    def __init__(self, config: Dict[str, Any], cache_dir: str = None):
        """Initialize with caching."""
        self.config = config
        self.cache = ModelCache(cache_dir or config.get("cache_dir"))
        self.model_name = config["model"]
        
        # Lazy load the actual client
        self._llm_client = None
        
    def _get_llm_client(self):
        """Lazy load LLM client."""
        if self._llm_client is None:
            import time
            start = time.time()
            
            # Check if we can skip some initialization
            model_info = self.cache.get_model_info(self.model_name)
            if model_info:
                print(f"⚡ Using cached model config for {self.model_name}")
            
            # Use fast client if enabled  
            if self.config.get("use_fast", False):
                from .simple_client import FastCommitClient
                self._llm_client = FastCommitClient(self.config)
                print("⚡ Using fast rule-based client")
            # Use ONNX client if enabled
            elif self.config.get("use_onnx", False):
                try:
                    from .onnx_client import ONNXLLMClient
                    self._llm_client = ONNXLLMClient(self.config)
                except ImportError as e:
                    print(f"⚠️  ONNX not available, falling back to regular client: {e}")
                    from .llm_client import LLMClient
                    self._llm_client = LLMClient(self.config)
            else:
                from .llm_client import LLMClient
                self._llm_client = LLMClient(self.config)
                
            elapsed = time.time() - start
            print(f"⏱️  Model loaded in {elapsed:.1f}s")
            
            # Save model info for future
            self.cache.save_model_info(self.model_name, {
                "loaded_at": time.time(),
                "config": self.config
            })
            
        return self._llm_client
        
    def generate_commit_message(self, diff: str) -> str:
        """Generate or retrieve cached commit message."""
        # Check cache first
        cached = self.cache.get_cached_message(diff, self.model_name)
        if cached:
            print("⚡ Using cached commit message")
            return cached
            
        # Generate new message
        client = self._get_llm_client()
        message = client.generate_commit_message(diff)
        
        # Save to cache
        self.cache.save_message(diff, self.model_name, message)
        
        return message