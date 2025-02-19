import argparse
import asyncio
import json
import logging
import os
from datetime import date

from src.gdelt_pipeline import fetch_gdelt_articles, save_articles_to_file
from src.rl_agent import run_simulation
from src import prompt_agent  # Import the prompt_agent module

def run_extract(args):
    config_path = args.config or "config/gdelt_config.json"
    # Load GDELT configuration from file
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            gdelt_config = json.load(f)
        logging.info("Loaded GDELT config from %s", config_path)
    else:
        logging.warning("Config file %s not found. Using default parameters.", config_path)
        gdelt_config = {}
    
    articles = fetch_gdelt_articles(custom_params=gdelt_config)
    today_str = date.today().strftime("%Y-%m-%d")
    # Save extracted articles into a dedicated raw folder with today's date.
    out_file = args.output or f"data/raw/gdelt_articles_{today_str}.json"
    save_articles_to_file(articles, filename=out_file)
    print(f"Extraction complete. Saved {len(articles)} articles to {out_file}.")

def run_agent(args):
    # Run the RL agent simulation asynchronously.
    # By default, it will look for today's raw file and generate a scored file in the "scored" folder.
    asyncio.run(run_simulation())

def run_web(args):
    from app import app
    app.run(debug=True)

def run_prompt_update(args):
    from datetime import date
    today_str = date.today().strftime("%Y-%m-%d")
    # If no generated file provided explicitly, use today's scored file.
    default_generated = f"data/scored/generated_scored_articles_{today_str}.json"
    if args.generated == "data/generated_scored_articles.json":
         args.generated = default_generated

    updated = prompt_agent.improve_agent_prompt(
        generated_json_path=args.generated,
        daily_dir=args.daily_dir,
        prompt_path=args.prompt
    )
    if updated:
        print("Prompt updated successfully.")
    else:
        print("Failed to update prompt.")

def run_summary_agent(args):
    from src.summary_agent import run_summary_agent
    import asyncio
    asyncio.run(run_summary_agent(input_file=args.input, output_file=args.output))

def main():
    parser = argparse.ArgumentParser(
        description="Run various tasks in the News Article Selection app."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: extract
    parser_extract = subparsers.add_parser("extract", help="Extract articles from GDELT.")
    parser_extract.add_argument("--config", type=str, help="Path to the GDELT configuration file.")
    parser_extract.add_argument("--output", type=str, help="Output file path for extracted articles.")

    # Subcommand: agent
    parser_agent = subparsers.add_parser("agent", help="Evaluate articles using the RL agent.")

    # Subcommand: web
    parser_web = subparsers.add_parser("web", help="Run the web interface for human scoring.")

    # Updated Subcommand: update_prompt
    # Instead of relying on the local update_prompt function,
    # we now call the prompt_updater module (from src/prompt_updater.py).
    parser_update = subparsers.add_parser("update_prompt", help="Update the agent prompt using human feedback.")
    parser_update.add_argument("--generated", type=str, default="data/generated_scored_articles.json",
                               help="Path to generated scored articles JSON file. (Will be replaced by today's file if not provided.)")
    parser_update.add_argument("--daily_dir", type=str, default=None,
                               help="Directory containing daily scored articles JSON files.")
    parser_update.add_argument("--prompt", type=str, default="config/agent_prompt.txt",
                               help="Path to the agent prompt file.")

    # Subcommand: summary
    parser_summary = subparsers.add_parser("summary", help="Generate summary JSON from scored articles (include only stories with score 7 and above, remove duplicates).")
    parser_summary.add_argument("--input", type=str, help="Path to the input scored articles JSON file (defaults to today's file in data/scored).")
    parser_summary.add_argument("--output", type=str, help="Path to the output summary JSON file (defaults to data/summary/summary_YYYY-MM-DD.json).")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    if args.command == "extract":
        run_extract(args)
    elif args.command == "agent":
        run_agent(args)
    elif args.command == "web":
        run_web(args)
    elif args.command == "update_prompt":
        run_prompt_update(args)
    elif args.command == "summary":
        run_summary_agent(args)

if __name__ == "__main__":
    main() 