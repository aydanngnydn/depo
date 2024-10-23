from flask import Flask, jsonify, request
import random
from openai import OpenAI
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

page_name = "074e000e-87b2-11ef-bbab-54bf6465a3fe"
emotions =  ["happy","grateful","sad","stressed","angry"]
emotion = random.choice(emotions)
usernames = {"happy":"Jane","grateful":"Hannah","sad":"Jerry","stressed":"Steven","angry":"Amy"}
comments_db = {}
def get_content(file):
    with open(file, 'rb') as file:
            content = file.read()
    return content

def generateComment(post_id):
    
    file = f"newblog/content/posts/{post_id}.md"
    content = get_content(file)
    os.environ["OPENAI_API_KEY"] = "sk--ux-UbzKqCTCxNVsSx8Z4ZBr5FQTxdgSXyXAm7hptMT3BlbkFJWj9-34ypfUmZtPQ6cnAc49X7RndZX5zHgjg2ClmZUA"
    client = OpenAI()
  
    
    stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Emotion: ${emotion}. Write a comment in this emotion with max 50 words about this content:${content}"}],
    stream=True,
)
    content = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content += chunk.choices[0].delta.content

    return content
  
@app.route('/api/comments/posts/<post_id>', methods=['GET'])
def get_comments(post_id):
    comment = generateComment(post_id)
    username = usernames[emotion]
    return jsonify({"comment": comment, "username": username})


if __name__ == '__main__':
    app.run(debug=True)

