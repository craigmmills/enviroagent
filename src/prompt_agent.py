def improve_agent_prompt(
    generated_json_path="data/generated_scored_articles.json",
    daily_dir=None,
    prompt_path="config/agent_prompt.txt"
):
    """
    Use an LLM-based prompt agent to produce an improved version of the original prompt,
    incorporating the detailed human feedback.
    
    Args:
        original_prompt (str): The original agent prompt.
        feedback_section (str): The human feedback section text.
    
    Returns:
        str: The improved agent prompt.
    """
    raw_response = chain.run({"original_prompt": original_prompt, "feedback_section": feedback_section})
    # If the response is a dict and contains extra keys (e.g., "text"), extract only the improved prompt text.
    if isinstance(raw_response, dict):
         improved_prompt = raw_response.get("text", raw_response)
    else:
         improved_prompt = raw_response

    improved_prompt = improved_prompt.strip()
    return improved_prompt 