"""
Instagram Reel Downloader

This script downloads Instagram reels from provided links using Instaloader.
It extracts the shortcode from the URL and downloads the reel in high quality.

Features:
- Downloads reels from Instagram links
- Extracts shortcode from various URL formats
- Saves reels with original quality
- Handles multiple reels in batch
- Provides progress feedback
"""

import instaloader
import re
import os
import argparse
import csv
from urllib.parse import urlparse, parse_qs
from pathlib import Path

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Download Instagram reels from a CSV file')
    parser.add_argument('csv_file', help='Path to the CSV file containing Instagram reel URLs')
    parser.add_argument('--output-dir', '-o', default='./downloads',
                      help='Base directory for saving downloaded reels (default: ./downloads)')
    return parser.parse_args()

def get_output_directory(csv_path, base_output_dir):
    """Generate output directory based on CSV filename."""
    # Get the CSV filename without extension and remove leading underscores
    csv_name = os.path.splitext(os.path.basename(csv_path))[0].lstrip('_')
    # Create output directory path
    output_dir = os.path.join(base_output_dir, csv_name)
    return output_dir

def extract_shortcode(url):
    """Extract the shortcode from an Instagram URL."""
    # Handle different URL formats
    if "/reel/" in url:
        # Reel URL
        match = re.search(r'/reel/([A-Za-z0-9_-]+)/?', url)
        if match:
            return match.group(1)
    elif "/p/" in url:
        # Regular post URL
        match = re.search(r'/p/([A-Za-z0-9_-]+)/?', url)
        if match:
            return match.group(1)
    elif "/tv/" in url:
        # TV/IGTV URL
        match = re.search(r'/tv/([A-Za-z0-9_-]+)/?', url)
        if match:
            return match.group(1)
    
    # Try to extract from query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    if 'shortcode' in query_params:
        return query_params['shortcode'][0]
    
    return None

def download_reel(shortcode, output_dir, filename_template="reel_{shortcode}"):
    """Download a reel using its shortcode."""
    try:
        # Create output directory if it doesn't exist
        output_dir = str(Path(output_dir))  # Convert to proper path
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Instaloader with specific dirname pattern
        L = instaloader.Instaloader(
            dirname_pattern=output_dir,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="",
            filename_pattern="{date_utc:%Y-%m-%d_%H-%M-%S}"
        )
        
        # Get the post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Generate filename
        filename = filename_template.format(shortcode=shortcode)
        
        # Download the post
        print(f"Downloading reel: {shortcode}")
        print(f"Saving to directory: {output_dir}")
        L.download_post(post, target=None)  # target is None since we set dirname_pattern
        
        return os.path.join(output_dir, filename)
    
    except instaloader.exceptions.InstaloaderException as e:
        print(f"Error downloading reel {shortcode}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def download_from_url(url, output_dir, filename_template="reel_{shortcode}"):
    """Download a reel from an Instagram URL."""
    shortcode = extract_shortcode(url)
    if shortcode:
        return download_reel(shortcode, output_dir, filename_template)
    else:
        print(f"Could not extract shortcode from URL: {url}")
        return None

def download_from_csv(csv_path, output_dir):
    """Download reels from a CSV file containing URLs."""
    try:
        print(f"Reading CSV file: {csv_path}")
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            # Skip header row if it exists
            next(csv_reader, None)
            urls = [row[0].strip() for row in csv_reader if row and row[0].strip()]
        
        total = len(urls)
        print(f"Found {total} URLs to process")
        
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\nProcessing {i}/{total}: {url}")
            result = download_from_url(url, output_dir)
            if result:
                results.append(result)
                print(f"Successfully downloaded {i}/{total}")
            else:
                print(f"Failed to download {i}/{total}")
        
        print(f"\nDownload complete. Successfully downloaded {len(results)}/{total} reels")
        return results
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Get the output directory based on CSV filename
    output_dir = get_output_directory(args.csv_file, args.output_dir)
    
    print(f"Starting download process...")
    print(f"Input file: {args.csv_file}")
    print(f"Output directory: {output_dir}")
    
    if not os.path.exists(args.csv_file):
        print(f"Error: Input file not found: {args.csv_file}")
        return
    
    if not args.csv_file.lower().endswith('.csv'):
        print("Error: Only CSV files are supported")
        return
    
    download_from_csv(args.csv_file, output_dir)

if __name__ == "__main__":
    main() 