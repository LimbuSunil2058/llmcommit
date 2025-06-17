"""Test configuration management."""

import json
import tempfile
import pytest
from pathlib import Path

from llmcommit.config import load_config, save_config, DEFAULT_CONFIG


def test_load_default_config():
    """Test loading default configuration."""
    config = load_config()
    assert config["model"] == DEFAULT_CONFIG["model"]
    assert config["max_tokens"] == DEFAULT_CONFIG["max_tokens"]


def test_load_config_from_file():
    """Test loading configuration from file."""
    test_config = {
        "model": "test-model",
        "max_tokens": 100,
        "temperature": 0.5
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f)
        config_path = f.name
    
    try:
        config = load_config(config_path)
        assert config["model"] == "test-model"
        assert config["max_tokens"] == 100
        assert config["temperature"] == 0.5
    finally:
        Path(config_path).unlink()


def test_save_config():
    """Test saving configuration."""
    test_config = {
        "model": "saved-model",
        "max_tokens": 200
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    
    try:
        save_config(test_config, config_path)
        
        # Load and verify
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        assert loaded_config["model"] == "saved-model"
        assert loaded_config["max_tokens"] == 200
    finally:
        Path(config_path).unlink()