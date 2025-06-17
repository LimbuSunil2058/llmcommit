# LLMCommit

AI-powered Git commit message generator with ultra-fast performance.
Generate, commit, and push with a single command.

🚀 **NEW**: File-based caching for instant processing of identical diffs!

## Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/0xkaz/llmcommit/main/install.sh | bash
```

## Key Features

- 🤖 **AI-Powered**: Uses Hugging Face Transformers for intelligent commit messages
- ⚡ **Ultra-Fast**: Rule-based engine executes in 2.5 seconds (default mode)
- 💾 **Smart Caching**: File-based cache for instant repeat processing (<0.1s)
- 🐳 **Docker Ready**: Containerized execution prevents environment issues
- 🔧 **Flexible Presets**: From ultra-fast (2.5s) to high-quality LLM modes
- 📦 **One Command**: `llmcommit -a -p` handles add → commit → push
- 🌐 **Multi-language**: English generation with Japanese documentation support

## Problems Solved

### Before LLMCommit 😩
- Spending 3-5 minutes thinking of commit messages
- Repetitive `git add` → `git commit` → `git push` workflow
- Generic messages like "update" or "fix"
- Difficulty with English expressions for non-native speakers
- Development flow interruption

### After LLMCommit ✅
- **2.5 seconds** for automatic message generation
- Single command: `llmcommit -a -p`
- Contextual messages: "Update user authentication logic"
- AI-generated proper English
- Seamless development experience

## Installation Options

### Option 1: One-liner (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/0xkaz/llmcommit/main/install.sh | bash
```

### Option 2: Python Package
```bash
pip install llmcommit
```

### Option 3: Docker Development
```bash
git clone https://github.com/0xkaz/llmcommit.git
cd llmcommit
make setup
```

## Usage

### Basic Commands
```bash
# Auto add + commit + push
llmcommit -a -p

# Ultra-fast mode (skip hooks)
llmcommit -a -p --no-verify

# Preview only (dry run)
llmcommit --dry-run

# Cache management
llmcommit-cache stats    # Show statistics
llmcommit-cache clear    # Clear old cache
```

### Command Options
- `-a, --add-all`: Automatically git add all files
- `-p, --push`: Auto-push after commit
- `--no-verify`: Skip git hooks (faster)
- `--force-push`: Force push (use with caution)
- `--dry-run`: Show commit message without committing
- `--preset PRESET`: Use configuration preset
- `--no-cache`: Disable caching
- `--cache-dir PATH`: Custom cache directory

### Performance Presets
```bash
# Ultra-fast rule-based (2.5s) - Default
llmcommit --preset ultra-fast -a -p

# Lightweight LLM (3-5s)
llmcommit --preset ultra-light -a -p

# High-performance light (5-8s)
llmcommit --preset light -a -p

# Balanced quality (8-12s)
llmcommit --preset balanced -a -p

# Standard quality (10-15s)
llmcommit --preset standard -a -p
```

## Performance Benchmarks

| Mode | Time | Description |
|------|------|-------------|
| **Ultra-Fast (Default)** | **2.5s** | ⚡ Rule-based engine |
| First LLM run | 30-60s | Model download included |
| Subsequent LLM runs | 10-30s | Model loading only |
| Cache hit | <0.1s | Identical diff cases |

### Supported Models

| Model | Size | Speed | Use Case |
|-------|------|-------|----------|
| **SmolLM-135M** | 135M | ⚡⚡ Ultra-fast | 🏆 2024's lightest |
| **TinyLlama-1.1B** | 1.1B | ⚡ Fastest LLM | 🎯 High-performance light |
| distilgpt2 | 82M | 🚀 Fast | Basic usage |
| DialoGPT-small | 117M | 🌟 Medium | Dialog-optimized |
| gpt2 | 124M | 🌠 Medium | Standard quality |

## Configuration

Create `.llmcommit.json` for customization:

```json
{
  "preset": "ultra-fast",
  "cache_dir": "~/.cache/llmcommit",
  "auto_add": true,
  "auto_push": false
}
```

## Docker Environment

When using Docker, these volumes are automatically created and persisted:
- `huggingface_cache`: Model files
- `llmcommit_cache`: Generated message cache

### Makefile Commands
```bash
make commit-all     # Auto add + commit
make fast-commit    # Ultra-fast mode (add + commit + skip hooks)
make install        # Local installation
make build          # Docker build
make clean          # Cleanup
```

## Common Usage Patterns

```bash
# Fast development commits
llmcommit -a -p --no-verify

# Careful commits (preview first)
llmcommit --dry-run
llmcommit -a

# Cache management
llmcommit-cache stats
llmcommit-cache clear --days 7
```

## Architecture Overview

### Core Components
```
llmcommit/
├── main.py              # CLI entry point
├── config.py           # Configuration management
├── git_handler.py      # Git operations (add/commit/push)
├── llm_client.py       # LLM model client
├── model_cache.py      # File-based caching
├── simple_client.py    # Ultra-fast rule-based client
├── onnx_client.py      # ONNX optimization client
└── profiler.py         # Performance measurement
```

### Execution Flow
1. **Initialization**: Load configuration (`.llmcommit.json`)
2. **Git Operations**: Staging and diff extraction
3. **Message Generation**:
   - `ultra-fast`: Rule-based engine (2.5s) ⚡ Default
   - `onnx`: ONNX-optimized (5-10s)
   - `llm`: Full LLM client (10-30s)
4. **Cache Check**: SHA256 hash-based cache lookup
5. **Commit/Push**: Execute Git operations

### Optimization Strategies

#### 1. Ultra-Fast Rule-Based Engine (Recommended)
- **Execution Time**: **2.5 seconds** (message generation: 0.0s)
- **Mechanism**: File pattern and diff analysis-based generation
- **Quality**: Production-ready appropriate messages
- **Default**: Automatically enabled on first run

#### 2. File-Based Cache System
```
~/.cache/llmcommit/
├── outputs/           # Generated messages
│   ├── a1b2c3d4.txt
│   └── ...
├── models/            # Model information
└── cache_metadata.json
```

- **Cache Key**: `SHA256(preset:diff[:500])[:16]`
- **TTL**: 24 hours
- **Hit Time**: <0.1 seconds

#### 3. Lazy Import Strategy
```python
# Don't load LLM libraries in ultra-fast mode
if config.get("preset") == "ultra-fast":
    from .simple_client import FastCommitClient
else:
    from .llm_client import LLMClient  # Only when needed
```

## Troubleshooting

### Model Download is Slow
Initial model download is required. Once downloaded, models are persisted.

### Cache Not Working
```bash
# Check cache statistics
llmcommit-cache stats

# Check cache directory
llmcommit-cache show
```

### Memory Issues
Use smaller models (ultra-fast) or run in Docker environment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License

---

**For Japanese documentation**: [README_ja.md](README_ja.md)