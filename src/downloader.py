"""
Instagram Reel Downloader

This script downloads Instagram reels from provided links using Instaloader.
It extracts the shortcode from the URL and downloads the reel in high quality.

Features:
- Downloads Instagram reels in high quality
- Processes multiple CSV files automatically
- Creates organized output directories
- Provides detailed logging
- Handles errors gracefully
- Implements rate limiting to avoid Instagram blocks
"""

import instaloader
import re
import os
import sys
import argparse
import csv
import logging
import traceback
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import List, Optional

def setup_logging(log_dir: str = None) -> logging.Logger:
    """Configure logging with file and console handlers."""
    try:
        log_dir = Path(log_dir) if log_dir else Path.cwd()
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'instagram_downloader.log'
        
        # Remove any existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file)
            ]
        )
        return logging.getLogger(__name__)
    except Exception as e:
        print(f"Error setting up logging: {e}", file=sys.stderr)
        sys.exit(1)

class InstagramDownloader:
    def __init__(self, base_output_dir: str, log_dir: str = None):
        self.logger = setup_logging(log_dir)
        try:
            self.base_output_dir = Path(base_output_dir)
            self.base_output_dir.mkdir(parents=True, exist_ok=True)
            self.instaloader = self._setup_instaloader()
            self.max_retries = 3  # Maximum number of retries for failed downloads
            self.retry_delay = 60  # Delay between retries in seconds
        except Exception as e:
            self.logger.error(f"Error initializing downloader: {e}")
            raise

    def _setup_instaloader(self) -> instaloader.Instaloader:
        """Initialize and configure Instaloader."""
        try:
            loader = instaloader.Instaloader(
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                post_metadata_txt_pattern="",
                filename_pattern="{date_utc:%Y-%m-%d_%H-%M-%S}"
            )
            # Add rate limiting
            loader.context._rate_controller = instaloader.RateController(
                loader.context,
                max_attempts=3,  # Maximum number of attempts per request
                wait_between_attempts=60  # Wait 60 seconds between attempts
            )
            return loader
        except Exception as e:
            self.logger.error(f"Error setting up Instaloader: {e}")
            raise

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
            self.logger.error(f"Error extracting shortcode from URL {url}: {e}")
            return None

    def download_reel(self, shortcode: str, output_dir: Path) -> bool:
        """Download a reel using its shortcode with retry logic."""
        for attempt in range(self.max_retries):
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                self.instaloader.dirname_pattern = str(output_dir)
                post = instaloader.Post.from_shortcode(self.instaloader.context, shortcode)
                self.instaloader.download_post(post, target=None)
                self.logger.info(f"Successfully downloaded reel: {shortcode}")
                return True
            except instaloader.exceptions.InstaloaderException as e:
                if "Please wait a few minutes" in str(e):
                    self.logger.warning(f"Rate limited on attempt {attempt + 1}/{self.max_retries}. Waiting {self.retry_delay} seconds...")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                self.logger.error(f"Instaloader error downloading reel {shortcode}: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error downloading reel {shortcode}: {e}")
                return False
        return False

    def process_csv(self, csv_path: Path) -> None:
        """Process a CSV file containing Instagram reel URLs."""
        try:
            if not csv_path.exists():
                self.logger.error(f"CSV file not found: {csv_path}")
                return

            output_dir = self.base_output_dir / csv_path.stem.lstrip('_')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Processing CSV: {csv_path}")
            self.logger.info(f"Output directory: {output_dir}")

            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                next(csv_reader, None)
                urls = [row[0].strip() for row in csv_reader if row and row[0].strip()]

            total = len(urls)
            self.logger.info(f"Found {total} URLs to process")

            successful = 0
            for i, url in enumerate(urls, 1):
                self.logger.info(f"Processing {i}/{total}: {url}")
                shortcode = self.extract_shortcode(url)
                if shortcode:
                    if self.download_reel(shortcode, output_dir):
                        successful += 1
                        self.logger.info(f"Successfully downloaded {i}/{total}")
                    else:
                        self.logger.error(f"Failed to download {i}/{total}")
                else:
                    self.logger.error(f"Could not extract shortcode from URL: {url}")
                
                # Add delay between downloads to avoid rate limiting
                if i < total:
                    time.sleep(5)  # 5 second delay between downloads

            self.logger.info(f"Download complete. Successfully downloaded {successful}/{total} reels")

        except Exception as e:
            self.logger.error(f"Error processing CSV file {csv_path}: {e}")
            self.logger.error(traceback.format_exc())

def main():
    try:
        parser = argparse.ArgumentParser(description='Download Instagram reels from CSV files')
        parser.add_argument('--csv-dir', type=str, default='./links',
                          help='Directory containing CSV files (default: ./links)')
        parser.add_argument('--output-dir', type=str, default='./downloads',
                          help='Base directory for saving downloaded reels (default: ./downloads)')
        parser.add_argument('--log-dir', type=str, default=None,
                          help='Directory for log files (default: current directory)')
        args = parser.parse_args()

        # Initialize downloader with logging
        downloader = InstagramDownloader(args.output_dir, args.log_dir)
        
        # Process all CSV files in the directory
        csv_dir = Path(args.csv_dir)
        if not csv_dir.exists():
            downloader.logger.error(f"CSV directory not found: {csv_dir}")
            sys.exit(1)

        for csv_file in csv_dir.glob('*.csv'):
            downloader.process_csv(csv_file)

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 