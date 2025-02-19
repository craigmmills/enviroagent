import os
import json
import logging
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

def improve_prompt(
    generated_json_path="data/generated_scored_articles.json",
    daily_dir=None,
    prompt_path="config/agent_prompt.txt"
):
    """
    Improve the agent prompt by integrating human feedback from scored articles.
    
    This function reads human evaluation data (user_score and user_reasoning)
    from the specified JSON file and instructs an LLM-based agent to produce a refined
    prompt that reflects the detailed human feedback.
    
    Args:
        generated_json_path (str): Path to the generated scored articles JSON file.
        daily_dir (str): Directory containing daily scored articles JSON files.
        prompt_path (str): Path to the agent prompt file.
    
    Returns:
        bool: True if the prompt was updated successfully, False otherwise.
    """
    articles = []
    if daily_dir is not None:
        if os.path.isdir(daily_dir):
            # Aggregate articles from all .json files in daily directory.
            for filename in os.listdir(daily_dir):
                if filename.lower().endswith('.json'):
                    file_path = os.path.join(daily_dir, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            daily_articles = json.load(f)
                            articles.extend(daily_articles)
                    except Exception as e:
                        logging.exception("Failed to load file %s: %s", filename, str(e))
        else:
            logging.error(f"Provided daily_dir {daily_dir} is not a directory.")
        if not articles:
            logging.info("No daily articles found in %s, falling back to generated_json_path.", daily_dir)
            if os.path.exists(generated_json_path):
                try:
                    with open(generated_json_path, "r", encoding="utf-8") as f:
                        articles = json.load(f)
                except Exception as e:
                    logging.exception(f"Failed to load generated articles: {str(e)}")
                    return False
            else:
                logging.error(f"Generated articles file not found: {generated_json_path}")
                return False
        else:
            logging.info("Aggregated %d articles from daily directory.", len(articles))
    else:
        if os.path.exists(generated_json_path):
            try:
                with open(generated_json_path, "r", encoding="utf-8") as f:
                    articles = json.load(f)
            except Exception as e:
                logging.exception(f"Failed to load generated articles: {str(e)}")
                return False
        else:
            logging.error(f"Generated articles file not found: {generated_json_path}")
            return False

    human_scores = []
    feedback_entries = []
    for article in articles:
        if "user_score" in article and "user_reasoning" in article:
            try:
                score = float(article["user_score"])
                human_scores.append(score)
            except Exception:
                continue
            feedback_entries.append(f"Score: {score:.1f} - {article['user_reasoning']}")
    
    if not human_scores:
        logging.info("No human feedback scores available to update prompt.")
        return False

    avg_score = sum(human_scores) / len(human_scores)
    
    # Build a detailed feedback section that includes average score and each feedback entry.
    feedback_section = "\n\n=== Human Feedback Integration ===\n"
    feedback_section += f"Average Human Score: {avg_score:.2f}\n"
    feedback_section += "Detailed Feedback:\n"
    for entry in feedback_entries:
        feedback_section += f"{entry}\n"
    
    try:
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                original_prompt = f.read()
        else:
            original_prompt = ""
        
        # Use the agent to generate an improved prompt that integrates the feedback.
        improved_prompt = agent_improve_prompt(original_prompt, feedback_section)
        
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(improved_prompt)
        logging.info("Agent-improved prompt saved to %s", prompt_path)
        # If daily_dir was used, archive the processed files.
        if daily_dir is not None:
            archive_dir = os.path.join(os.path.dirname(daily_dir), "processed_daily")
            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)
            for filename in os.listdir(daily_dir):
                if filename.lower().endswith('.json'):
                    src_file = os.path.join(daily_dir, filename)
                    dest_file = os.path.join(archive_dir, filename)
                    try:
                        os.rename(src_file, dest_file)
                        logging.info("Archived daily file: %s", filename)
                    except Exception as e:
                        logging.exception("Failed to archive file %s: %s", filename, str(e))
        return True
    except Exception as e:
        logging.exception(f"Failed to save updated prompt: {str(e)}")
        return False

def agent_improve_prompt(original_prompt, feedback_section):
    """
    Use an LLM-based agent to produce an improved version of the original prompt,
    incorporating the detailed human feedback.
    
    Args:
        original_prompt (str): The original agent prompt.
        feedback_section (str): The human feedback section text.
    
    Returns:
        str: The improved agent prompt.
    """
    prompt_template = PromptTemplate(
         template="""You are a prompt improvement agent. Your task is to refine an agent prompt for evaluating news articles using human feedback.
The original prompt is provided below, followed by detailed human feedback—each entry is formatted as 'Score: <score> - <reasoning>'.
Ensure your revised prompt explicitly incorporates this feedback so that future evaluations align with human priorities.

Original Prompt:
{original_prompt}

Human Feedback:
{feedback_section}

Please output ONLY the revised prompt text with no additional commentary, greetings, or extra language. The output should consist solely of the improved prompt.
""",
         input_variables=["original_prompt", "feedback_section"]
    )
    # Instantiate the Gemini-based LLM (using latest LangChain syntax).
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    raw_response = chain.run({"original_prompt": original_prompt, "feedback_section": feedback_section})
    # If the response is a dict and contains extra keys (e.g., "text"), extract only the improved prompt text.
    if isinstance(raw_response, dict):
         improved_prompt = raw_response.get("text", raw_response)
    else:
         improved_prompt = raw_response

    improved_prompt = improved_prompt.strip()
    return improved_prompt

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Improve the agent prompt using human feedback."
    )
    parser.add_argument(
        "--generated",
        type=str,
        default="data/generated_scored_articles.json",
        help="Path to generated scored articles JSON file (used if --daily_dir is not provided)."
    )
    parser.add_argument(
        "--daily_dir",
        type=str,
        default=None,
        help="Directory containing daily scored articles JSON files."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="config/agent_prompt.txt",
        help="Path to the agent prompt file."
    )
    args = parser.parse_args()
    
    improved = improve_prompt(args.generated, daily_dir=args.daily_dir, prompt_path=args.prompt)
    if improved:
        print("Prompt updated successfully.")
    else:
        print("Failed to update prompt.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    main() 