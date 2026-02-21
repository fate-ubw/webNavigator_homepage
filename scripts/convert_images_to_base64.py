#!/usr/bin/env python3
"""
Convert all screenshot images in graph folders to base64 and embed them into web_graph.json.
This reduces the number of files for GitHub Pages deployment.

Usage:
    python scripts/convert_images_to_base64.py

After running:
    1. The web_graph.json files will be updated with embedded base64 images
    2. You can safely delete the screenshots_cropped_resized folders
    3. Commit the changes
"""

import json
import base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import sys


def image_to_base64(image_path: Path) -> str | None:
    """Convert an image file to base64 data URL."""
    if not image_path.exists():
        print(f"  Warning: Image not found: {image_path}")
        return None
    
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        
        # Determine MIME type
        suffix = image_path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_types.get(suffix, "image/png")
        
        # Create data URL
        b64_data = base64.b64encode(data).decode("utf-8")
        return f"data:{mime_type};base64,{b64_data}"
    except Exception as e:
        print(f"  Error processing {image_path}: {e}")
        return None


def process_graph_folder(graph_folder: Path) -> dict:
    """Process a single graph folder and return statistics."""
    stats = {"folder": graph_folder.name, "nodes": 0, "images_converted": 0, "errors": 0}
    
    web_graph_path = graph_folder / "web_graph.json"
    screenshots_folder = graph_folder / "screenshots_cropped_resized"
    
    if not web_graph_path.exists():
        print(f"  Skipping {graph_folder.name}: web_graph.json not found")
        return stats
    
    if not screenshots_folder.exists():
        print(f"  Skipping {graph_folder.name}: screenshots_cropped_resized folder not found")
        return stats
    
    print(f"\nProcessing: {graph_folder.name}")
    
    # Load existing web_graph.json
    with open(web_graph_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    nodes = data.get("nodes", {})
    stats["nodes"] = len(nodes)
    
    # Convert each node's image to base64
    for node_id, node_data in nodes.items():
        screen_path = node_data.get("screen_path")
        if not screen_path:
            continue
        
        image_path = screenshots_folder / screen_path
        base64_data = image_to_base64(image_path)
        
        if base64_data:
            # Add base64 data to node
            node_data["image_base64"] = base64_data
            stats["images_converted"] += 1
        else:
            stats["errors"] += 1
    
    # Save updated web_graph.json
    with open(web_graph_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    
    print(f"  Converted {stats['images_converted']}/{stats['nodes']} images")
    if stats["errors"] > 0:
        print(f"  Errors: {stats['errors']}")
    
    return stats


def main():
    # Find the public/graph folder
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    graph_root = project_root / "public" / "graph"
    
    if not graph_root.exists():
        print(f"Error: Graph folder not found at {graph_root}")
        sys.exit(1)
    
    print(f"Graph root: {graph_root}")
    
    # Find all graph subfolders
    graph_folders = [f for f in graph_root.iterdir() if f.is_dir() and f.name.startswith("run_id-")]
    
    if not graph_folders:
        print("No graph folders found")
        sys.exit(1)
    
    print(f"Found {len(graph_folders)} graph folders")
    
    # Process each folder
    total_stats = {"nodes": 0, "images_converted": 0, "errors": 0}
    
    for folder in sorted(graph_folders):
        stats = process_graph_folder(folder)
        total_stats["nodes"] += stats["nodes"]
        total_stats["images_converted"] += stats["images_converted"]
        total_stats["errors"] += stats["errors"]
    
    # Print summary
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Total nodes: {total_stats['nodes']}")
    print(f"  Images converted: {total_stats['images_converted']}")
    print(f"  Errors: {total_stats['errors']}")
    print("=" * 50)
    
    if total_stats["images_converted"] > 0:
        print("\nNext steps:")
        print("  1. Test the website locally: npm run dev")
        print("  2. If everything works, delete the screenshots folders:")
        for folder in sorted(graph_folders):
            screenshots_folder = folder / "screenshots_cropped_resized"
            if screenshots_folder.exists():
                print(f"     rm -rf {screenshots_folder.relative_to(project_root)}")
        print("  3. Commit the changes")


if __name__ == "__main__":
    main()
