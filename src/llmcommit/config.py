"""Configuration management for llmcommit."""

import json
import os
from pathlib import Path
from typing import Dict, Any


# 2024 latest ultra-lightweight model configuration (for LLM mode)
ULTRA_LIGHT_CONFIG = {
    "model": "HuggingFaceTB/SmolLM-135M",  # 135M parameters - 2024 most lightweight
    "max_tokens": 20,
    "temperature": 0.1,
    "prompt_template": "Generate a concise git commit message for these changes:\n{diff}\n\nCommit message:",
    "cache_dir": "/tmp/llmcommit_cache",
    "use_onnx": False,
    "use_fast": False
}

# Lightweight high-performance model configuration
LIGHT_PERFORMANCE_CONFIG = {
    "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # 1.1B parameters - high-performance lightweight
    "max_tokens": 25,
    "temperature": 0.2,
    "prompt_template": "Write a clear git commit message for:\n{diff}\n\nCommit:",
    "cache_dir": "/tmp/llmcommit_cache",
    "use_onnx": False,
    "use_fast": False
}

# Default configuration (fast rule-based)
DEFAULT_CONFIG = {
    "model": "distilgpt2",  # For LLM mode switching
    "max_tokens": 10,
    "temperature": 0.1,
    "prompt_template": "git commit -m \"{diff}\"\n\nGenerate a concise commit message:",
    "cache_dir": "/tmp/llmcommit_cache",
    "use_onnx": False,
    "use_fast": True  # Default is fast rule-based
}


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from file or use defaults."""
    config = DEFAULT_CONFIG.copy()
    
    # Load from config file if provided
    if config_path:
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config.update(user_config)
        else:
            print(f"⚠️  Config file not found: {config_path}")
            print("ℹ️  Using default configuration with fast mode")
    else:
        # Try to load from default locations
        default_paths = [
            Path.home() / ".llmcommit" / "config.json",
            Path.cwd() / ".llmcommit.json"
        ]
        
        config_found = False
        for path in default_paths:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    config.update(user_config)
                config_found = True
                break
        
        # Auto-create .llmcommit.json in current directory if not found
        if not config_found:
            local_config_path = Path.cwd() / ".llmcommit.json"
            print(f"📝 Creating default config file: {local_config_path}")
            try:
                with open(local_config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                print("✅ Default configuration created successfully")
                print("ℹ️  Fast mode enabled for optimal performance")
            except Exception as e:
                print(f"⚠️  Could not create config file: {e}")
                print("ℹ️  Using in-memory configuration")
    
    # Expand cache directory path
    config["cache_dir"] = os.path.expanduser(config["cache_dir"])
    
    return config


def save_config(config: Dict[str, Any], config_path: str = None):
    """Save configuration to file."""
    if config_path is None:
        config_path = Path.home() / ".llmcommit" / "config.json"
    
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def create_ultra_light_config():
    """Create ultra-light LLM configuration."""
    return ULTRA_LIGHT_CONFIG.copy()


def create_fast_config():
    """Create fast rule-based configuration."""
    return DEFAULT_CONFIG.copy()


def get_preset_configs():
    """Get available preset configurations."""
    return {
        "ultra-fast": DEFAULT_CONFIG.copy(),                    # 2.5s - rule-based
        "ultra-light": ULTRA_LIGHT_CONFIG.copy(),               # 3-5s - SmolLM-135M (2024 most lightweight)
        "light": LIGHT_PERFORMANCE_CONFIG.copy(),               # 5-8s - TinyLlama-1.1B
        "balanced": {**DEFAULT_CONFIG, "model": "microsoft/DialoGPT-small", "use_fast": False},  # 8-12s
        "standard": {**DEFAULT_CONFIG, "model": "distilgpt2", "use_fast": False}  # 10-15s
    }