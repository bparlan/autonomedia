#!/usr/bin/env python
# scripts/checks/run_daily_posting.py
"""
Manual trigger script for daily posting routine.
Usage:
    python scripts/checks/run_daily_posting.py [--dry-run] [--max-items=N]
Options:
    --dry-run      Run in dry-run mode (no actual posting)
    --max-items=N  Maximum items to post per execution (default: 2)
"""
import asyncio
import sys

# Add project root to path
sys.path.insert(0, '/Users/bparlan/devcode/autonomedia')

from src.autonomedia.core.posting_routine import posting_routine


def main():
    """Main entry point for manual trigger."""
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    max_items = 2

    # Parse max_items if provided
    for arg in sys.argv:
        if arg.startswith("--max-items="):
            max_items = int(arg.split("=")[1])



    asyncio.run(posting_routine(dry_run=dry_run, max_items=max_items))


    return 0


if __name__ == "__main__":
    sys.exit(main())
