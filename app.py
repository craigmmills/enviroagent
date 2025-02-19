from flask import Flask, render_template, request, redirect, url_for
import json
import os
import glob
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-here'  # For session management if needed

def get_latest_file():
    # Look for scored articles files in the "data/scored" folder.
    files = glob.glob("data/scored/generated_scored_articles_*.json")
    if files:
        files.sort()  # Assumes filename contains the date in sortable format YYYY-MM-DD.
        return files[-1]
    return "data/generated_scored_articles.json"

DATA_PATH = get_latest_file()

def load_articles():
    """Load the JSON articles from the file."""
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    return articles

def save_articles(articles):
    """Save the updated articles list back to the file."""
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    # Redirect to the first article
    return redirect(url_for('article', article_index=0))

@app.route('/article/<int:article_index>', methods=['GET', 'POST'])
def article(article_index):
    articles = load_articles()
    total_articles = len(articles)
    
    # If the index is out of bounds, redirect to the completion page.
    if article_index >= total_articles:
        return redirect(url_for('completed'))
    
    article_data = articles[article_index]
    
    if request.method == 'POST':
        # Check if the user clicked the Agree button versus a manual submission
        if request.form.get('action') == 'agree':
            user_score = article_data.get('tweet_worthiness')
            user_reasoning = article_data.get('summary')
        else:
            user_score = int(request.form.get('user_score'))
            user_reasoning = request.form.get('user_reasoning')
        
        # Add new keys to the article entry (or update if already exists)
        article_data['user_score'] = user_score
        article_data['user_reasoning'] = user_reasoning
        
        # Save the updated article back into the articles list and persist the changes.
        articles[article_index] = article_data
        save_articles(articles)
        
        # Move to the next article
        next_index = article_index + 1
        return redirect(url_for('article', article_index=next_index))
    
    # Calculate a progress percentage for the progress bar.
    progress = ((article_index) / total_articles) * 100

    return render_template('article.html', 
                           article=article_data, 
                           article_index=article_index,
                           total_articles=total_articles,
                           progress=progress)

@app.route('/completed')
def completed():
    return render_template('completed.html')

if __name__ == '__main__':
    app.run(debug=True) 