"""
PROJECT: News Article Summary Agent

This agent loads a scored articles JSON file, filters stories with a tweet-worthiness score
of 7 or above, removes duplicate articles based on title, and generates a summary JSON.
For each article, it ensures that all available metadata is included and extracts the original
story link from the HTML field (assuming the first <a> tag href is the original URL).

This agent uses the Gemini API via LangChain's ChatGoogleGenerativeAI.
Ensure your environment is set with your GOOGLE_API_KEY.
"""

import os
import json
import asyncio
import logging
import re
from datetime import date
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

def load_scored_articles(filename):
    """Load scored articles from a JSON file."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def deduplicate_articles(articles):
    """Remove duplicate articles based on title (case-insensitive)."""
    seen = set()
    unique_articles = []
    for article in articles:
        title = article.get("title", "").strip().lower()
        if title and title not in seen:
            seen.add(title)
            unique_articles.append(article)
    return unique_articles

async def run_summary_agent(input_file=None, output_file=None):
    """
    Generate a summary JSON from scored articles:
      - Include only articles with tweet_worthiness >= 7.
      - Remove duplicate articles.
      - For each article, include all metadata and extract the first URL from the HTML as "link".
    Uses Gemini via LangChain to produce a clean JSON output.
    """
    today_str = date.today().strftime("%Y-%m-%d")
    # Default input: today's scored file in data/scored folder.
    if input_file is None:
         input_file = f"data/scored/generated_scored_articles_{today_str}.json"
    # Default output: summary file in data/summary folder.
    if output_file is None:
         output_file = f"data/summary/summary_{today_str}.json"
    
    if not os.path.exists(input_file):
         logging.error("Input scored articles file %s not found.", input_file)
         return
    
    articles = load_scored_articles(input_file)
    if not articles:
         logging.error("No articles found in %s", input_file)
         return
    
    # Filter articles with tweet_worthiness score >= 7.
    filtered = [a for a in articles if a.get("tweet_worthiness", 0) >= 7]
    # Remove duplicate articles based on title.
    unique_articles = deduplicate_articles(filtered)
    
    # Prepare a Gemini prompt to structure the final summary JSON.
    prompt_template = PromptTemplate(
         template="""You are a news summary agent using the Gemini model. Your task is to produce a clean summary JSON from the provided list of scored news articles.
The summary JSON should include only articles with a tweet_worthiness score of 7 or higher, and duplicates (based on title) should be removed.
For each article, include all available metadata (such as title, name, count, shareimage, html, tweet_worthiness, summary, geometry, etc.).
Additionally, extract a valid URL from the article's HTML content (assume that the first <a> tag's href is the original story link) 
and include it in a field called "link".
Output ONLY the final JSON array of article objects with no additional commentary.
Input JSON:
{articles}
""",
         input_variables=["articles"]
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    articles_json = json.dumps(unique_articles, ensure_ascii=False, indent=2)
    raw_response = await chain.ainvoke({"articles": articles_json})
    
    try:
         # Process Gemini output.
         if isinstance(raw_response, dict):
              response_str = raw_response.get("text", "")
         else:
              response_str = str(raw_response)
         response_str = response_str.strip()
         # Remove markdown code fences if present.
         if response_str.startswith("```"):
              response_str = response_str.strip("`").strip()
         # Use regex to extract JSON array.
         match = re.search(r'(\[.*\])', response_str, re.DOTALL)
         if match:
              json_str = match.group(1)
         else:
              json_str = response_str
         summary_articles = json.loads(json_str)
    except Exception as e:
         logging.error("Failed to parse Gemini response: %s", e)
         summary_articles = unique_articles  # fallback
    
    # Save the summary JSON.
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
         with open(output_file, "w", encoding="utf-8") as f:
              json.dump(summary_articles, f, ensure_ascii=False, indent=4)
         logging.info("Summary JSON saved to %s", output_file)
    except Exception as e:
         logging.error("Failed to save summary JSON: %s", e)

if __name__ == "__main__":
    asyncio.run(run_summary_agent()) 