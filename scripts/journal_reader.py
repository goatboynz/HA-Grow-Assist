#!/usr/bin/env python3
"""
Journal Reader Script for Home Assistant command_line sensor.
Reads grow journal JSON files and formats them for display in Lovelace.

Usage:
  python3 journal_reader.py <room_id> [max_entries]

Example:
  python3 journal_reader.py f1 10
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def format_journal(room_id: str, max_entries: int = 10) -> str:
    """Read and format journal entries for a room."""
    journal_path = Path(f"/config/grow_logs/{room_id}.json")
    
    if not journal_path.exists():
        return "No journal entries yet."
    
    try:
        with open(journal_path, "r") as f:
            entries = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return f"Error reading journal: {e}"
    
    if not entries:
        return "No journal entries yet."
    
    # Get last N entries, reversed (newest first)
    recent = entries[-max_entries:][::-1]
    
    output_lines = []
    for entry in recent:
        # Parse timestamp
        ts = entry.get("timestamp", "Unknown")
        try:
            dt = datetime.fromisoformat(ts)
            ts_formatted = dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            ts_formatted = ts[:16]
        
        note = entry.get("note", "")
        image_url = entry.get("image_url")
        
        # Build entry line
        line = f"**{ts_formatted}**\n{note}"
        if image_url:
            line += f"\n📷 [View Photo]({image_url})"
        
        output_lines.append(line)
    
    return "\n\n---\n\n".join(output_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: journal_reader.py <room_id> [max_entries]")
        sys.exit(1)
    
    room_id = sys.argv[1]
    max_entries = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(format_journal(room_id, max_entries))


if __name__ == "__main__":
    main()
