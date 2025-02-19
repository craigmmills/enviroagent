import os
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Endpoints and API keys from environment variables
GDELT_ENDPOINT = os.getenv("GDELT_API_URL", "http://api.gdeltproject.org/api/v2/doc/doc")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit(1)

# Configure the Gemini API with the provided API key
genai.configure(api_key=GOOGLE_API_KEY)

def test_gdelt_fetch():
    """
    Fetch a sample of news articles from the GDELT API.
    """
    params = {
        "query": "biodiversity nature conservation",         # Search for news articles
        "format": "json",
        "mode": "ArtList",        # Use Article List mode as per @GDELTDOC documentation
        "maxrecords": 10,          # Limit number of articles
        "sort": "DateDesc",       # Sort by most recent articles
        "timespan": "100h"         # Limit to articles from the last 24 hours
    }
    try:
        headers = {
            "User-Agent": "NewsArticleSelectionRL/1.0 (contact: your-email@example.com)"
        }
        response = requests.get(GDELT_ENDPOINT, params=params, timeout=10, headers=headers)
        if response.ok:
            data = response.json()
            print("GDELT API returned data:")
            print(json.dumps(data, indent=2))
            # Attempt to extract headlines if available
            if isinstance(data, dict) and "articles" in data:
                headlines = []
                for article in data["articles"]:
                    if "title" in article:
                        headlines.append(article["title"])
                if headlines:
                    summary = "Headlines: " + "; ".join(headlines)
                else:
                    summary = "Fetched data: " + json.dumps(data)
            else:
                summary = "Fetched data: " + json.dumps(data)
            return summary
        else:
            print("GDELT API request failed with status code:", response.status_code)
            return ""
    except Exception as e:
        print("Error fetching data from GDELT API:", str(e))
        return ""

def test_gemini_prompt(gdelt_context):
    """
    Test the Gemini API by generating content using a prompt that includes GDELT data.
    """
    try:
        # Initialize Gemini model and send a prompt that includes GDELT data
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"Based on the following news data: '{gdelt_context}', "
            "craft a well-structured, engaging short story of about 300 words. The narrative should "
    "flow naturally, clearly weaving together the events and themes from the news, such as "
    "environmental crises, landslides, mining incidents, and deforestation. Use vivid descriptions "
    "and a creative, coherent style that respects the gravity of these events while bringing the story "
    "to life in an imaginative yet realistic way."
        )
        result = model.generate_content(prompt)
        print("Gemini API response:")
        print(result.text)
    except Exception as e:
        print("Error calling Gemini API:", str(e))

if __name__ == "__main__":
    print("Starting environment validation tests...")
    print("-" * 50)
    gdelt_data = test_gdelt_fetch()
    print("-" * 50)
    test_gemini_prompt(gdelt_data)
    print("-" * 50)