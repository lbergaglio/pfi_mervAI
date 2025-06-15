
from flask import Flask, request, jsonify
import praw
from textblob import TextBlob

app = Flask(__name__)

# Configura tu cliente Reddit con tus credenciales
reddit = praw.Reddit(
    client_id='TU_CLIENT_ID',
    client_secret='TU_CLIENT_SECRET',
    user_agent='mervAI-sentiment-app'
)

@app.route('/sentiment/reddit', methods=['POST'])
def sentiment_reddit():
    data = request.json
    query = data.get('query', 'MERVAL')
    subreddit_name = data.get('subreddit', 'argentina')

    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = subreddit.search(query, limit=10)
        results = []

        for post in posts:
            analysis = TextBlob(post.title)
            sentiment_score = analysis.sentiment.polarity
            sentiment = 'positive' if sentiment_score > 0 else 'negative' if sentiment_score < 0 else 'neutral'
            results.append({
                'title': post.title,
                'score': post.score,
                'sentiment': sentiment
            })

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
