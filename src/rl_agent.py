"""
PROJECT: News Article Selection RL System – Agent Setup & Initial Model Integration

This script integrates the Gemini model (via LangChain's ChatGoogleGenerativeAI) as the evaluation agent
for news articles. It creates a minimal RL-like flow for:
  - Generating a state representation of an article.
  - Using the Gemini model to produce an evaluation (agent action) in JSON format.
  - Printing the raw output of the Gemini API call (chain.invoke).
  
Ensure your environment is set up with your GOOGLE_API_KEY.
"""

import os
import json
import asyncio
from textwrap import dedent
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
import logging
import re
from pathlib import Path
from datetime import date

try:
    import json5  # For more forgiving JSON parsing (e.g., allowing comments or trailing commas)
except ImportError:
    json5 = None

def load_articles(filename):
    """Load articles from a JSON file."""
    with open(filename, "r", encoding="utf-8") as f:
        file_content = f.read()
    try:
        articles = json.loads(file_content)
    except json.decoder.JSONDecodeError:
        if json5:
            articles = json5.loads(file_content)
        else:
            raise
    return articles

def state_representation(article):
    """
    Create a state representation of the article from its core features.
    """
    state = (
        f"Title: {article.get('title', 'N/A')}\n"
        f"Name: {article.get('name', 'N/A')}\n"
        f"Count: {article.get('count', 'N/A')}\n"
        f"HTML: {article.get('html', '')}"
    )
    return state

def get_agent_prompt():
    prompt_path = Path("config/agent_prompt.txt")
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    else:
        # fallback to a default prompt
        return dedent("""
        You are a news evaluation agent using the state-of-the-art Gemini model. Your task is to analyze the following article details and assess its tweet-worthiness. Consider aspects such as relevance, timeliness, clarity, and public interest.

        Article details:
        {state}

        Provide your evaluation as a JSON object with the following keys:
            "tweet_worthiness": an integer score between 0 (not tweet-worthy) and 10 (highly tweet-worthy).
            "summary": a brief (1-2 sentence) summary explaining your evaluation.

        Example output:
        {{"tweet_worthiness": 8, "summary": "The article provides timely insights with significant public interest."}}

        Now, please provide your JSON evaluation.
        """)

async def get_agent_action(state_text):
    """
    Create a prompt with the article state text, invoke the Gemini LLM, and print the exact output.
    """
    prompt_template = get_agent_prompt()
    prompt = PromptTemplate(template=prompt_template, input_variables=["state"])
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Use asynchronous invocation with proper input keys.
    result = await chain.ainvoke({"state": state_text})
    # Print the raw output from the Gemini API call as soon as it comes through.
    print(result)
    return result

async def run_simulation(input_file=None, output_file=None):
    """
    Run a simulation that:
      - Loads articles from a file.
      - Creates a state representation for each article.
      - Uses the Gemini agent to produce an evaluation.
      - Parses the Gemini output and injects "tweet_worthiness" and "summary" into each article.
      - Writes the resulting scored articles to "data/generated_scored_articles.json".
    """
    from datetime import date
    today_str = date.today().strftime("%Y-%m-%d")
    if input_file is None:
         input_file = f"data/raw/gdelt_articles_{today_str}.json"
    if output_file is None:
         output_file = f"data/scored/generated_scored_articles_{today_str}.json"

    # If the output file already exists, skip processing to prevent reruns.
    if os.path.exists(output_file):
         logging.info("Output file %s already exists. Skipping simulation.", output_file)
         return

    articles = load_articles(input_file)
    if not articles:
        logging.error("No articles to process. Exiting simulation.")
        return

    scored_articles = []  # To store articles with evaluations.

    for idx, article in enumerate(articles):
        state_text = state_representation(article)
        response_text = await get_agent_action(state_text)
        try:
            response_str = ""
            if isinstance(response_text, str):
                response_str = response_text
            elif isinstance(response_text, dict):
                # Extract the 'text' field from the dict if available.
                response_str = response_text.get("text", "")
            else:
                response_str = str(response_text)

            response_str = response_str.strip()
            print(response_str)
            # If the response is wrapped in markdown fences, remove them.
            if response_str.startswith("```"):
                response_str = response_str.strip("`").strip()

            # Use regex to extract the first JSON object from the response.
            match = re.search(r'(\{.*\})', response_str, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                json_str = response_str

            action = json.loads(json_str)
        except Exception as e:
            logging.error("Failed to parse response for article %d: %s", idx, e)
            action = {"tweet_worthiness": 0, "summary": "Could not evaluate article."}

        # Inject the evaluated values into the article.
        article["tweet_worthiness"] = action.get("tweet_worthiness", 0)
        article["summary"] = action.get("summary", "No summary provided")
        scored_articles.append(article)

        # logging.info("Article %d evaluated: tweet_worthiness=%s, summary=%s", 
        #              idx, article["tweet_worthiness"], article["summary"])

    # Write the scored and summarized articles to the output file
    try:
         # Ensure the directory exists.
         os.makedirs(os.path.dirname(output_file), exist_ok=True)
         with open(output_file, "w", encoding="utf-8") as f:
             json.dump(scored_articles, f, ensure_ascii=False, indent=4)
         logging.info("Generated scored articles saved to %s", output_file)
    except Exception as e:
         logging.error("Failed to save scored articles: %s", e)

if __name__ == "__main__":
    asyncio.run(run_simulation())