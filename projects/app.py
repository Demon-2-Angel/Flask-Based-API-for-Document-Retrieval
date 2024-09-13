from flask import Flask, request, jsonify
from database import db, User
from cache import cache
from limiter import limiter
from utils import get_embedding, query_pinecone
import time

app = Flask(__name__)

# Configure app (add database, caching, etc.)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
cache.init_app(app)
limiter.init_app(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is running"}), 200

@app.route('/search', methods=['POST'])
@limiter.limit("5 per minute")
@cache.cached(timeout=300, query_string=True)
def search():
    start_time = time.time()
    try:
        data = request.get_json()
        query = data['query']
        user_id = data['user_id']
        top_k = data.get('top_k', 3)

        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user.request_count += 1
            db.session.commit()
        else:
            new_user = User(user_id=user_id, request_count=1)
            db.session.add(new_user)
            db.session.commit()

        if user and user.request_count > 5:
            return jsonify({"error": "Rate limit exceeded"}), 429

        query_embedding = get_embedding(query)
        results = query_pinecone(query_embedding, top_k)

        end_time = time.time()
        inference_time = end_time - start_time
        print(f"Inference time: {inference_time:.4f} seconds")

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
