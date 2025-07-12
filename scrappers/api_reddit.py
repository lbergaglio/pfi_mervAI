import praw
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

resultados = []
for post in reddit.subreddit("all").search("merval", sort="new", time_filter="day", limit=10):
    post_dict = {
        "titulo": post.title,
        "subreddit": post.subreddit.display_name,
        "karma": post.score,
        "autor": str(post.author),
        "url": post.url,
        "fecha": datetime.fromtimestamp(post.created_utc).isoformat(),
        "comentarios": []
    }

    post.comments.replace_more(limit=0)
    for c in post.comments[:3]:
        post_dict["comentarios"].append({
            "autor": str(c.author),
            "texto": c.body,
            "karma": c.score
        })

    print(f"📌 {post.title} | karma: {post.score}")
    resultados.append(post_dict)

# Guardar en archivo
with open("reddit_merval.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)
