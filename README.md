# News Article Selection RL System

This project aims to build a reinforcement learning (RL) system that ingests news articles from GDELT, uses Gemini via LangChain as the frontier model to process the articles, and integrates human feedback for training an agent to determine tweet-worthy content.

## Project Objectives

- Set up a clean Python development environment.
- Integrate with Gemini and GDELT APIs.
- Leverage RL libraries for training models.
- Validate API connectivity with test scripts.

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd news-article-selection-rl
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables**:
    Create a `.env` file in the project root with the following content:
    ```env
    GEMINI_API_URL=https://api.gemini.io/test
    GDELT_API_URL=http://api.gdeltproject.org/api/v2/doc/doc
    ```

5. **Run the API connectivity test**:
    ```bash
    python src/main.py
    ```

## Libraries Used

- [LangChain](https://github.com/hwchase17/langchain)
- [Gemini API/SDK](#)  (Placeholder link)
- [Requests](https://docs.python-requests.org/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [PyTorch / Stable Baselines3](https://pytorch.org/ / https://stable-baselines3.readthedocs.io/en/master/)

## Next Steps

- Develop the core RL agent.
- Implement article parsing and filtering.
- Integrate LangChain for agent orchestration.
- Incorporate human feedback for training improvements. 