#!/usr/bin/env python3
"""Main CLI module for llmcommit."""

import argparse
import os
import sys
import time
from pathlib import Path

# Suppress tokenizers warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from .config import load_config
from .git_handler import GitHandler
from .profiler import SimpleProfiler
from . import __version__


def print_status(message: str, status: str = "info", quiet: bool = False):
    """Print status message with emoji."""
    if quiet and status not in ["error", "success"]:
        return
    
    emojis = {
        "info": "ℹ️ ",
        "success": "✅",
        "loading": "⏳",
        "error": "❌",
        "rocket": "🚀"
    }
    print(f"{emojis.get(status, '')} {message}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Generate git commit messages using LLM")
    parser.add_argument("--version", "-v", action="version", version=f"llmcommit {__version__}")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--model", type=str, help="Override model to use")
    parser.add_argument("--dry-run", action="store_true", help="Show message without committing")
    parser.add_argument("--add-all", "-a", action="store_true", help="Automatically stage all modified files before committing")
    parser.add_argument("--no-verify", action="store_true", help="Skip git hooks for faster commits")
    parser.add_argument("--push", "-p", action="store_true", help="Automatically push after committing")
    parser.add_argument("--force-push", action="store_true", help="Force push (use with caution)")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--profile", action="store_true", help="Show performance profiling")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--cache-dir", type=str, help="Cache directory path")
    parser.add_argument("--preset", choices=["ultra-fast", "ultra-light", "light", "balanced", "standard"], 
                       help="Use configuration preset (ultra-fast: 2.5s rule-based, ultra-light: 3-5s SmolLM-135M, light: 5-8s TinyLlama-1.1B)")
    
    args = parser.parse_args()
    
    profiler = SimpleProfiler() if args.profile else None
    
    try:
        if profiler:
            profiler.start("config_load")
        
        # Load config with preset support
        if args.preset:
            from .config import get_preset_configs
            preset_configs = get_preset_configs()
            if args.preset in preset_configs:
                config = preset_configs[args.preset]
                print_status(f"Using preset: {args.preset}", "info")
            else:
                config = load_config(args.config)
        else:
            config = load_config(args.config)
            
        if profiler:
            profiler.end("config_load")
        
        if args.model:
            config["model"] = args.model
            
        git_handler = GitHandler()
        
        # Auto-stage files if requested
        if args.add_all:
            print_status("Staging all files...", "loading")
            if not git_handler.add_all():
                print_status("Failed to stage files.", "error")
                sys.exit(1)
            print_status("Files staged successfully", "success")
        
        print_status("Checking for changes...", "loading")
        diff = git_handler.get_staged_diff()
        
        if not diff:
            # Try to get unstaged diff if no staged changes
            unstaged_diff = git_handler.get_unstaged_diff()
            if unstaged_diff and not args.add_all:
                print_status("No staged changes found. Use 'git add' or run with --add-all/-a flag.", "error")
                sys.exit(1)
            elif not unstaged_diff:
                print_status("No changes found.", "error")
                sys.exit(1)
            diff = unstaged_diff
            
        print_status(f"Loading model: {config['model']}...", "loading")
        start_time = time.time()
        if profiler:
            profiler.start("model_load")
        
        # Use fast client if enabled
        if config.get("use_fast", False):
            from .simple_client import FastCommitClient
            llm_client = FastCommitClient(config)
            print_status("Using fast rule-based client", "info")
        # Use cached client unless disabled
        elif args.no_cache:
            from .llm_client import LLMClient
            llm_client = LLMClient(config)
        else:
            from .model_cache import CachedLLMClient
            cache_dir = args.cache_dir or config.get("cache_dir")
            llm_client = CachedLLMClient(config, cache_dir)
            
        if profiler:
            profiler.end("model_load")
        
        print_status("Generating commit message...", "loading")
        if profiler:
            profiler.start("message_generation")
        commit_message = llm_client.generate_commit_message(diff)
        if profiler:
            profiler.end("message_generation")
        elapsed = time.time() - start_time
        print_status(f"Message generated in {elapsed:.1f}s", "success")
        
        if args.dry_run:
            print(f"\n📝 Generated commit message:\n{commit_message}")
        else:
            print_status("Committing changes...", "loading")
            success = git_handler.commit(commit_message, no_verify=args.no_verify)
            if success:
                print_status(f"Committed: {commit_message}", "success")
                
                # Auto-push if requested
                if args.push or args.force_push:
                    print_status("Pushing to remote...", "loading")
                    push_success = git_handler.push(force=args.force_push)
                    if push_success:
                        print_status("Successfully pushed to remote!", "rocket")
                    else:
                        print_status("Failed to push. You may need to pull first or use --force-push.", "error")
                        sys.exit(1)
            else:
                print_status("Failed to commit changes.", "error")
                sys.exit(1)
            
    except KeyboardInterrupt:
        print_status("\nOperation cancelled by user.", "info")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error: {e}", "error")
        sys.exit(1)
    finally:
        if profiler:
            print("\n" + profiler.report())


if __name__ == "__main__":
    main()