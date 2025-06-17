"""Fast model loading with state caching."""

import os
import time
import torch
import pickle
from pathlib import Path
from typing import Dict, Any, Optional


class FastModelLoader:
    """Optimized model loader with state caching."""
    
    @staticmethod
    def get_model_state_path(model_name: str, cache_dir: str) -> Path:
        """Get path for model state cache."""
        cache_path = Path(cache_dir) / "model_states"
        cache_path.mkdir(parents=True, exist_ok=True)
        
        # Create safe filename
        safe_name = model_name.replace("/", "--")
        return cache_path / f"{safe_name}.pt"
        
    @staticmethod
    def save_model_state(model, tokenizer, model_name: str, cache_dir: str):
        """Save model state to disk for fast loading."""
        state_path = FastModelLoader.get_model_state_path(model_name, cache_dir)
        
        print(f"💾 Saving model state to {state_path}")
        
        # Save model state dict
        torch.save({
            'model_state_dict': model.state_dict(),
            'model_config': model.config.to_dict(),
            'tokenizer_config': tokenizer.init_kwargs,
            'pad_token': tokenizer.pad_token,
            'pad_token_id': tokenizer.pad_token_id,
        }, state_path)
        
        print(f"✅ Model state saved ({state_path.stat().st_size / 1024 / 1024:.1f} MB)")
        
    @staticmethod
    def load_model_fast(model_name: str, cache_dir: str, config: Dict[str, Any]):
        """Try to load model from cached state first."""
        from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
        
        state_path = FastModelLoader.get_model_state_path(model_name, cache_dir)
        
        # Check if state exists and is recent (within 7 days)
        if state_path.exists():
            age_days = (time.time() - state_path.stat().st_mtime) / 86400
            if age_days < 7:
                try:
                    print(f"⚡ Loading model from cached state...")
                    start_time = time.time()
                    
                    # Load saved state
                    checkpoint = torch.load(state_path, map_location='cpu')
                    
                    # Recreate model with config
                    model_config = AutoConfig.from_dict(checkpoint['model_config'])
                    model = AutoModelForCausalLM.from_config(model_config)
                    model.load_state_dict(checkpoint['model_state_dict'])
                    
                    # Recreate tokenizer
                    tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        cache_dir=cache_dir,
                        local_files_only=True
                    )
                    
                    # Restore tokenizer settings
                    if checkpoint.get('pad_token'):
                        tokenizer.pad_token = checkpoint['pad_token']
                        tokenizer.pad_token_id = checkpoint['pad_token_id']
                    
                    elapsed = time.time() - start_time
                    print(f"✅ Model loaded from cache in {elapsed:.1f}s")
                    
                    return model, tokenizer
                    
                except Exception as e:
                    print(f"⚠️  Cache load failed: {e}, falling back to normal load")
                    
        # Normal loading
        return None, None


class OptimizedModelLoader:
    """Further optimizations for model loading."""
    
    @staticmethod
    def create_minimal_model(model_name: str, cache_dir: str):
        """Create minimal model for commit message generation."""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print(f"🚀 Loading minimal model configuration...")
        
        # Load with minimal memory
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            torch_dtype=torch.float32,  # Use float32 for CPU
            low_cpu_mem_usage=True,
            # Reduce model layers if possible
            num_hidden_layers=6 if "distil" not in model_name else None,
        )
        
        # Optimize for inference
        model.eval()
        model.requires_grad_(False)
        
        # Compile if available (PyTorch 2.0+)
        if hasattr(torch, 'compile'):
            try:
                model = torch.compile(model, mode="reduce-overhead")
                print("✅ Model compiled for faster inference")
            except:
                pass
                
        return model