import os
import json
import requests
import logging
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set up logging
LOG_FILENAME = "pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler()  # also output to console
    ]
)

# Get the GDELT API endpoint from environment variables
GDELT_ENDPOINT = os.getenv("GDELT_API_URL", "http://api.gdeltproject.org/api/v2/doc/doc")

def fetch_gdelt_articles(custom_params=None):
    """
    Query the GDELT API for environmental news articles and process the returned data.
    Returns:
        A list of dictionaries containing the cleaned article data.
    """
    default_params = {
        "query": "landslide",
        "mode": "PointData",
        "timespan": "1d",
        "format": "geojson",
        "maxrecords": 10
    }
    if custom_params:
        default_params.update(custom_params)
    params = default_params
    headers = {
        "User-Agent": "NewsArticleSelectionRL/1.0 (contact: your-email@example.com)"
    }
    try:
        logging.info("Sending request to GDELT API with query: %s", params.get("query"))
        response = requests.get("https://api.gdeltproject.org/api/v2/geo/geo", params=params, timeout=15, headers=headers)
        if response.ok:
            data = response.json()
            logging.info("GDELT API returned successfully.")
            
            processed_articles = []
            # Process GeoJSON features
            features = data.get("features", [])
            if not features:
                logging.warning("No features found in the response.")
            else:
                for feature in features[:10]:
                    properties = feature.get("properties", {})
                    geometry = feature.get("geometry", {})
                    html_content = properties.get("html", "")
                    title_value = properties.get("title")
                    if not title_value:
                        # Try to extract title from the HTML anchor tag's title attribute
                        match = re.search(r'title\s*=\s*"([^"]+)"', html_content)
                        if match:
                            title_value = match.group(1)
                        else:
                            title_value = properties.get("name", "N/A")

                    processed = {
                        "title": title_value,
                        "name": properties.get("name", "N/A"),
                        "count": properties.get("count", "N/A"),
                        "shareimage": properties.get("shareimage", "N/A"),
                        "html": html_content,
                        "geometry": geometry
                    }
                    processed_articles.append(processed)
                    
            logging.info("Processed %d articles.", len(processed_articles))
            return processed_articles
        else:
            logging.error("GDELT API request failed with status code: %s", response.status_code)
            return []
    except Exception as e:
        logging.exception("Error fetching data from GDELT API: %s", str(e))
        return []

def save_articles_to_file(articles, filename="data/gdelt_articles.json"):
    """
    Save the processed articles to a local JSON file.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        logging.info("Successfully saved articles to %s", filename)
    except Exception as e:
        logging.exception("Failed to save articles to file: %s", str(e))

def main():
    logging.info("Starting GDELT Data Pipeline")
    articles = fetch_gdelt_articles()
    if articles:
        save_articles_to_file(articles)
    else:
        logging.warning("No articles were fetched; nothing to save.")
    logging.info("GDELT Data Pipeline finished.")

if __name__ == "__main__":
    main() 