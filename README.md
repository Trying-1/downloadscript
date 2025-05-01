# Instagram Reel Downloader

A GitHub Actions workflow that automatically downloads Instagram reels from CSV files containing reel URLs.

## Features

- Downloads Instagram reels in high quality
- Processes multiple CSV files
- Creates organized output directories
- Runs automatically on schedule
- Can be triggered manually

## Setup

1. Create a new GitHub repository
2. Add your CSV files to the `links` directory
3. Set up the following secret in your repository:
   - `BASE_OUTPUT_DIR`: The base directory where downloaded reels will be saved

## CSV File Format

Your CSV files should contain Instagram reel URLs in the first column. Example:
```
https://www.instagram.com/reel/ABC123/
https://www.instagram.com/reel/DEF456/
```

## Usage

The workflow runs automatically every day at 12:00 UTC. You can also trigger it manually:

1. Go to the "Actions" tab in your repository
2. Select "Instagram Reel Downloader" workflow
3. Click "Run workflow"

## Output

Downloaded reels will be saved in subdirectories based on the CSV filename:
- `{BASE_OUTPUT_DIR}/s0mebody/` for `_.s0mebody.csv`
- `{BASE_OUTPUT_DIR}/instant_philosophy/` for `_instant_philosophy.csv` 