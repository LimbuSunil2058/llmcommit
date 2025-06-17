#!/usr/bin/env python3
"""Cache management CLI."""

import argparse
import sys
from .model_cache import ModelCache
from .config import load_config


def main():
    """Cache management CLI."""
    parser = argparse.ArgumentParser(description="LLMCommit cache management")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show cache statistics")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear old cache entries")
    clear_parser.add_argument("--days", type=int, default=7, 
                             help="Clear entries older than N days")
    clear_parser.add_argument("--all", action="store_true",
                             help="Clear all cache entries")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show cache directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    # Load config for cache directory
    config = load_config()
    cache = ModelCache(config.get("cache_dir"))
    
    if args.command == "stats":
        stats = cache.get_cache_stats()
        print("Cache Statistics:")
        print(f"  Directory: {stats['cache_dir']}")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Total size: {stats['total_size_mb']} MB")
        print(f"  Models:")
        for model, count in stats['models'].items():
            print(f"    {model}: {count} entries")
            
    elif args.command == "clear":
        if args.all:
            # Clear all
            for f in cache.outputs_dir.glob("*.txt"):
                f.unlink()
            cache.metadata = {}
            cache._save_metadata()
            print("All cache cleared")
        else:
            cache.clear_old_cache(args.days)
            print(f"Cleared cache entries older than {args.days} days")
            
    elif args.command == "show":
        print(f"Cache directory: {cache.cache_dir}")
        print(f"Outputs: {cache.outputs_dir}")
        print(f"Models: {cache.models_dir}")


if __name__ == "__main__":
    main()