"""
Instagram Reel Downloader

This script downloads Instagram reels from provided links using Instaloader.
It extracts the shortcode from the URL and downloads the reel in high quality.

Features:
- Downloads Instagram reels in high quality
- Processes multiple CSV files
- Creates organized output directories
- Provides detailed logging
- Handles errors gracefully
"""

import instaloader
import re
import os
import argparse
import csv
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('instagram_downloader.log')
    ]
)
logger = logging.getLogger(__name__)

class InstagramDownloader:
    def __init__(self, base_output_dir: str):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.instaloader = self._setup_instaloader()

    def _setup_instaloader(self) -> instaloader.Instaloader:
        """Initialize and configure Instaloader."""
        return instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="",
            filename_pattern="{date_utc:%Y-%m-%d_%H-%M-%S}"
        )

    def extract_shortcode(self, url: str) -> Optional[str]:
        """Extract the shortcode from an Instagram URL."""
        try:
            if "/reel/" in url:
                match = re.search(r'/reel/([A-Za-z0-9_-]+)/?', url)
                if match:
                    return match.group(1)
            elif "/p/" in url:
                match = re.search(r'/p/([A-Za-z0-9_-]+)/?', url)
                if match:
                    return match.group(1)
            elif "/tv/" in url:
                match = re.search(r'/tv/([A-Za-z0-9_-]+)/?', url)
                if match:
                    return match.group(1)
            
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            if 'shortcode' in query_params:
                return query_params['shortcode'][0]
            
            return None
        except Exception as e:
            logger.error(f"Error extracting shortcode from URL {url}: {e}")
            return None

    def download_reel(self, shortcode: str, output_dir: Path) -> bool:
        """Download a reel using its shortcode."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Set the output directory for this download
            self.instaloader.dirname_pattern = str(output_dir)
            
            # Get and download the post
            post = instaloader.Post.from_shortcode(self.instaloader.context, shortcode)
            self.instaloader.download_post(post, target=None)
            
            logger.info(f"Successfully downloaded reel: {shortcode}")
            return True
            
        except instaloader.exceptions.InstaloaderException as e:
            logger.error(f"Instaloader error downloading reel {shortcode}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading reel {shortcode}: {e}")
            return False

    def process_csv(self, csv_path: Path) -> None:
        """Process a CSV file containing Instagram reel URLs."""
        try:
            if not csv_path.exists():
                logger.error(f"CSV file not found: {csv_path}")
                return

            # Create output directory based on CSV filename
            output_dir = self.base_output_dir / csv_path.stem.lstrip('_')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Processing CSV: {csv_path}")
            logger.info(f"Output directory: {output_dir}")

            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                # Skip header row if it exists
                next(csv_reader, None)
                urls = [row[0].strip() for row in csv_reader if row and row[0].strip()]

            total = len(urls)
            logger.info(f"Found {total} URLs to process")

            successful = 0
            for i, url in enumerate(urls, 1):
                logger.info(f"Processing {i}/{total}: {url}")
                shortcode = self.extract_shortcode(url)
                if shortcode:
                    if self.download_reel(shortcode, output_dir):
                        successful += 1
                        logger.info(f"Successfully downloaded {i}/{total}")
                    else:
                        logger.error(f"Failed to download {i}/{total}")
                else:
                    logger.error(f"Could not extract shortcode from URL: {url}")

            logger.info(f"Download complete. Successfully downloaded {successful}/{total} reels")

        except Exception as e:
            logger.error(f"Error processing CSV file {csv_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Download Instagram reels from CSV files')
    parser.add_argument('--csv-dir', type=str, default='./links',
                      help='Directory containing CSV files (default: ./links)')
    parser.add_argument('--output-dir', type=str, default='./downloads',
                      help='Base directory for saving downloaded reels (default: ./downloads)')
    args = parser.parse_args()

    # Initialize downloader
    downloader = InstagramDownloader(args.output_dir)
    
    # Process all CSV files in the directory
    csv_dir = Path(args.csv_dir)
    if not csv_dir.exists():
        logger.error(f"CSV directory not found: {csv_dir}")
        return

    for csv_file in csv_dir.glob('*.csv'):
        downloader.process_csv(csv_file)

if __name__ == "__main__":
    main() 