# Instagram Reel Downloader

A GitHub Actions workflow that automatically downloads Instagram reels from CSV files containing reel URLs.

## Features

- Downloads Instagram reels in high quality
- Processes multiple CSV files automatically
- Creates organized output directories
- Provides detailed logging
- Runs on a daily schedule
- Can be triggered manually
- Handles errors gracefully

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── instagram-downloader.yml
├── src/
│   └── downloader.py
├── links/
│   ├── _.s0mebody.csv
│   └── _instant_philosophy.csv
├── requirements.txt
└── README.md
```

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

### Local Usage

```bash
python src/downloader.py --csv-dir ./links --output-dir ./downloads
```

### GitHub Actions

The workflow runs automatically every day at 12:00 UTC. You can also trigger it manually:

1. Go to the "Actions" tab in your repository
2. Select "Instagram Reel Downloader" workflow
3. Click "Run workflow"

## Output

- Downloaded reels will be saved in subdirectories based on the CSV filename
- Logs are available in the GitHub Actions artifacts
- Each CSV file gets its own output directory

## Error Handling

- Failed downloads are logged with detailed error messages
- The script continues processing even if some downloads fail
- Logs are saved both to file and GitHub Actions artifacts

## Contributing

Feel free to submit issues and enhancement requests! 