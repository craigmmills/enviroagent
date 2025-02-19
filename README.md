# News Article Selection RL System

This project builds a reinforcement learning (RL) system to automatically evaluate news articles for tweet-worthiness, using a combination of the Gemini API (via LangChain) and human feedback. The system ingests articles from the GDELT API, processes and scores them using an RL agent (the "rl_agent"), refines its evaluation prompt using a dedicated prompt agent, and finally produces a summary JSON of unique, high-scoring content.

## Project Workflow

Each day, the system performs the following steps:
1. **Extraction:**  
   The `extract` command queries the GDELT API for new articles and saves them as raw data in a date-tagged file (e.g. `data/raw/gdelt_articles_YYYY-MM-DD.json`).

2. **Evaluation (RL Agent):**  
   The `agent` command loads today's raw articles, runs them through the RL agent (using Gemini via LangChain) to determine a tweet-worthiness score and generate a brief summary, and saves the results to a date-tagged scored file (e.g. `data/scored/generated_scored_articles_YYYY-MM-DD.json`).

3. **Human Feedback (Web Interface):**  
   The `web` command launches a web interface for human scorers to review and update the article evaluations.

4. **Prompt Updating (Prompt Agent):**  
   The `update_prompt` command uses a prompt agent to incorporate daily human feedback into an improved evaluation prompt. This updated prompt is then stored in `config/agent_prompt.txt`.

5. **Summarization (Summary Agent):**  
   The `summary` command filters the scored articles (keeping only those with a tweet-worthiness score of 7 or above), removes duplicate stories, extracts key metadata (including the original story link), and outputs a summary JSON in a date-tagged file (e.g. `data/summary/summary_YYYY-MM-DD.json`).

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd news-article-selection-rl
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables**:  
   Create a `.env` file in the project root with the following content (adjust values as needed):
    ```env
    GEMINI_API_URL=https://api.gemini.io/test
    GDELT_API_URL=http://api.gdeltproject.org/api/v2/doc/doc
    # Also set your GOOGLE_API_KEY and any other required keys:
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```

## Usage Instructions

The project provides a command-line interface with several subcommands. Run the tasks from the project root using:

- **Extract articles from GDELT**:
    ```bash
    python src/main.py extract --config config/gdelt_config.json
    ```
   *This will save raw articles to a file in the `data/raw` folder using today's date.*

- **Evaluate articles using the RL agent**:
    ```bash
    python src/main.py agent
    ```
   *This will load today's raw file, evaluate the articles with Gemini, and save results in `data/scored`.*

- **Launch the web interface for human feedback**:
    ```bash
    python src/main.py web
    ```

- **Update the evaluation prompt with human feedback**:
    ```bash
    python src/main.py update_prompt --prompt config/agent_prompt.txt
    ```

- **Generate a summary JSON of high-scoring articles**:
    ```bash
    python src/main.py summary
    ```
   *This command filters the scored articles (score ≥ 7), removes duplicates, and outputs a summary file in `data/summary`.*

## Libraries & References

- **LangChain**: Used for chaining Gemini API calls. See the [LangChain docs](https://python.langchain.com/docs/) for more details.
- **Gemini API/SDK**: The front-end evaluation engine for the RL agent. Refer to the [Gemini API documentation](https://developers.google.com/experimental/overview) for implementation details.
- **Requests**: For HTTP requests to external APIs.
- **python-dotenv**: For handling environment variables from the `.env` file.
- **Others**: See `requirements.txt` for the complete list.

## Project Structure

- `src/`
  - `gdelt_pipeline.py`  – Extracts articles from GDELT.
  - `rl_agent.py`       – Evaluates articles using Gemini via LangChain.
  - `prompt_agent.py`   – Improves the evaluation prompt using human feedback.
  - `summary_agent.py`  – Generates a summary JSON of high-scoring, unique articles.
  - `main.py`           – Entry point with subcommands for extract, agent, web, update_prompt, and summary.
- `config/`
  - `agent_prompt.txt`  – The evaluation prompt used by the RL agent.
  - `gdelt_config.json` – Configuration for the GDELT API.
- `data/`
  - `raw/`             – Contains raw articles files (with date stamps).
  - `scored/`          – Contains scored articles files (with date stamps).
  - `summary/`         – Contains summary JSON files (with date stamps).
- `.env` – Contains API keys and environment variables (not committed).
- `.gitignore` – Ignores virtual environments, log files, and data directories.

## Next Steps

- Continue refining the RL agent's evaluation logic.
- Enhance the web interface for more intuitive human feedback.
- Expand testing and add error handling as the system evolves.
- Monitor updates in Gemini API and LangChain for new features or improvements.

Happy coding! 