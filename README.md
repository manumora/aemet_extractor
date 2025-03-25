# AEMET Extractor

## Overview
This Python script extracts weather forecast data from the Spanish Meteorological Agency (AEMET) website for the city of Mérida. It retrieves the content from the weather prediction page, processes it, and saves it as a standalone HTML file that can be viewed locally.

## Features
- Extracts the main content from AEMET's weather prediction page for Mérida
- Processes CSS and converts relative links to absolute URLs
- Adds a custom title to the weather forecast
- Removes unnecessary elements from the page
- Creates a self-contained HTML file with all styles included
- Disables navigation links to keep the content static

## Requirements
- Python 3.x
- Required libraries:
  - requests
  - BeautifulSoup4
  - re (Regular Expressions, built-in)
  - os (built-in)
  - urllib.parse (built-in)

## Usage
Simply run the script:
```
python aemet_extractor.py
```

The script will:
1. Connect to the AEMET website and retrieve the weather forecast for Mérida
2. Extract and process the relevant HTML content
3. Save the result as "aemet.html" in the same directory as the script

## Output
The output is a standalone HTML file (`aemet.html`) that displays the weather forecast information for Mérida without requiring an internet connection after initial download.
