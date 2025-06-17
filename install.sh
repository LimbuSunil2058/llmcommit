#!/bin/bash

# LLMCommit Installation Script
# Usage: curl -sSL https://raw.githubusercontent.com/0xkaz/llmcommit/main/install.sh | bash

set -e

echo "🚀 Installing LLMCommit..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
required_version="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python 3.8+ is required, but $python_version is installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Install LLMCommit
echo "📦 Installing LLMCommit from PyPI..."
pip3 install --user llmcommit

# Check if installation was successful
if command -v llmcommit &> /dev/null; then
    echo "✅ LLMCommit installed successfully!"
    echo ""
    echo "🎉 Ready to use! Try running:"
    echo "   llmcommit --help"
    echo ""
    echo "Quick start:"
    echo "   cd your-git-repo"
    echo "   llmcommit              # Generate and commit"
    echo "   llmcommit -a           # Auto-add files and commit"
    echo "   llmcommit --dry-run    # Preview commit message"
    echo ""
    echo "For more information, visit:"
    echo "   https://github.com/0xkaz/llmcommit"
else
    echo "⚠️  Installation completed, but 'llmcommit' command not found."
    echo "You may need to add ~/.local/bin to your PATH:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "Add this line to your ~/.bashrc or ~/.zshrc to make it permanent."
fi