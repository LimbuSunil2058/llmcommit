"""ONNX-based LLM client for faster inference."""

import os
import time
from typing import Dict, Any
from pathlib import Path

try:
    from transformers import AutoTokenizer
    from optimum.onnxruntime import ORTModelForCausalLM
    import torch
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("Warning: optimum not installed. Install with: pip install optimum[onnxruntime]")


class ONNXLLMClient:
    """ONNX-optimized LLM client."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with ONNX model."""
        if not ONNX_AVAILABLE:
            raise ImportError("Please install optimum: pip install optimum[onnxruntime]")
            
        self.config = config
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load ONNX model and tokenizer."""
        model_name = self.config["model"]
        cache_dir = self.config.get("cache_dir", "/tmp/llmcommit_cache")
        onnx_cache = Path(cache_dir) / "onnx_models"
        onnx_cache.mkdir(parents=True, exist_ok=True)
        
        print(f"🚀 Loading ONNX model: {model_name}")
        
        # Load tokenizer
        tok_start = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        print(f"⏱️  Tokenizer loaded in {time.time() - tok_start:.1f}s")
        
        # Load or convert to ONNX
        model_start = time.time()
        onnx_path = onnx_cache / model_name.replace("/", "--")
        
        if onnx_path.exists():
            print("📁 Loading cached ONNX model")
            self.model = ORTModelForCausalLM.from_pretrained(
                onnx_path,
                provider="CPUExecutionProvider"
            )
        else:
            print("🔄 Converting to ONNX (first time only)")
            self.model = ORTModelForCausalLM.from_pretrained(
                model_name,
                export=True,
                cache_dir=str(onnx_cache),
                provider="CPUExecutionProvider"
            )
            # Save for next time
            self.model.save_pretrained(onnx_path)
            
        print(f"⏱️  ONNX model loaded in {time.time() - model_start:.1f}s")
        
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate_commit_message(self, diff: str) -> str:
        """Generate commit message using ONNX model."""
        prompt = self.config["prompt_template"].format(diff=diff[:1000])
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        # Generate with ONNX
        gen_start = time.time()
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=min(self.config["max_tokens"], 50),
            temperature=self.config["temperature"],
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id
        )
        print(f"⏱️  ONNX Generation: {time.time() - gen_start:.3f}s")
        
        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0][len(inputs['input_ids'][0]):],
            skip_special_tokens=True
        )
        
        return self._clean_commit_message(generated_text)
    
    def _clean_commit_message(self, message: str) -> str:
        """Clean and format the generated commit message."""
        message = message.strip()
        lines = [line.strip() for line in message.split('\n')]
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        return '\n'.join(lines)