"""LLM client for generating commit messages."""

import os
import time
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
except ImportError:
    print("Error: transformers and torch are required. Install with: pip install transformers torch")
    exit(1)


class LLMClient:
    """Client for interacting with LLM models."""
    
    def __init__(self, config: Dict[str, Any], profiler=None):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.profiler = profiler
        self._load_model()
    
    def _load_model(self):
        """Load the specified model and tokenizer."""
        model_name = self.config["model"]
        cache_dir = self.config["cache_dir"]
        
        # Create cache directory if it doesn't exist
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Check if model is already cached
        model_path = Path(cache_dir) / f"models--{model_name.replace('/', '--')}"
        is_cached = model_path.exists()
        
        print(f"📁 Model cached: {is_cached}")
        
        # Load tokenizer
        tok_start = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            local_files_only=is_cached  # Skip download if cached
        )
        print(f"⏱️  Tokenizer loaded in {time.time() - tok_start:.1f}s")
        
        # Use float32 on CPU for better performance
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # Load model
        model_start = time.time()
        print(f"🔄 Starting model load for {model_name}...")
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                local_files_only=is_cached  # Skip download if cached
            )
            print(f"⏱️  Model loaded in {time.time() - model_start:.1f}s")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            print(f"🔄 Retrying without local_files_only...")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                torch_dtype=dtype,
                low_cpu_mem_usage=True
            )
            print(f"⏱️  Model loaded in {time.time() - model_start:.1f}s")
        
        if device == "cpu":
            # CPU optimizations
            torch.set_num_threads(4)  # Limit CPU threads
            self.model.eval()  # Set to evaluation mode
        
        # Set pad token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate_commit_message(self, diff: str) -> str:
        """Generate a commit message based on the git diff."""
        prompt = self.config["prompt_template"].format(diff=diff[:1000])  # Limit diff size
        
        # Tokenize
        tok_start = time.time()
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        print(f"⏱️  Tokenization: {time.time() - tok_start:.3f}s")
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate
        gen_start = time.time()
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs.get('attention_mask'),
                max_new_tokens=min(self.config["max_tokens"], 50),
                temperature=self.config["temperature"],
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        print(f"⏱️  Generation: {time.time() - gen_start:.3f}s")
        
        # Decode only the generated part
        input_length = inputs['input_ids'].shape[1]
        generated_text = self.tokenizer.decode(
            outputs[0][input_length:],
            skip_special_tokens=True
        )
        
        return self._clean_commit_message(generated_text)
    
    def _clean_commit_message(self, message: str) -> str:
        """Clean and format the generated commit message."""
        # Remove extra whitespace and newlines
        message = message.strip()
        
        # Split into lines and clean each line
        lines = [line.strip() for line in message.split('\n')]
        
        # Remove empty lines at the beginning and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        return '\n'.join(lines)