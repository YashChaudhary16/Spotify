# Spotify Streaming History Analytics Dashboard

This is an interactive dashboard for analyzing your Spotify streaming history data.

## Features

- **Overall Listening Stats**: View total listening time, number of tracks/episodes, and daily averages
- **Listening Patterns**: Analyze your listening by hour of day and day of week
- **Monthly Trends**: See how your listening habits have changed over time
- **Content Analysis**: Discover your top artists, tracks, shows, and episodes
- **Platform Usage**: See which devices you use most for streaming

## Screenshots

![Dashboard Preview](dashboard_preview.jpg)

## Requirements

- Python 3.7+
- Libraries listed in `requirements.txt`

## Installation

1. Clone or download this repository
2. Install required libraries:

```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your Spotify data files are in the same directory as the script
2. Run the dashboard application:

```bash
streamlit run spotify_dashboard.py
```

3. The dashboard will open in your default web browser at http://localhost:8501

## Data Requirements

The dashboard expects the following files:
- `Streaming_History_Audio_*.json`: One or more JSON files containing audio streaming history
- `Streaming_History_Video_2021-2025.json`: JSON file containing video streaming history

## Troubleshooting

If you encounter dependency issues, try:

```bash
pip install numpy==1.24.3 --force-reinstall
pip install pandas==1.5.3
pip install streamlit==1.32.0
pip install plotly==5.18.0
```

## Notes

- The dashboard handles deduplication of entries to avoid counting the same track multiple times
- Filtering options allow you to focus on specific years or content types 