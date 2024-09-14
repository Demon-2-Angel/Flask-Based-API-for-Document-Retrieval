import logging
from flask import Flask, request, jsonify
from database import db, User
from cache import cache
from limiter import limiter
from utils import get_embedding, query_pinecone
import time
from logging.handlers import RotatingFileHandler
from scraping import start_scraping_thread
from flask import request, jsonify

app = Flask(__name__)

# Configure app (add database, caching, etc.)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
cache.init_app(app)
limiter.init_app(app)

# Set up rotating log files (1MB max, keep 3 backup files)
handler = RotatingFileHandler('api.log', maxBytes=1*1024*1024, backupCount=3)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.route('/health', methods=['GET'])
def health():
    logging.info("Health check request received.")
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

        # Log incoming request details
        logging.info(f"Search query: {query}, user_id: {user_id}, top_k: {top_k}")

        # Check user rate limits
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user.request_count += 1
            db.session.commit()
        else:
            new_user = User(user_id=user_id, request_count=1)
            db.session.add(new_user)
            db.session.commit()

        # Enforce rate limit of 5 requests
        if user and user.request_count > 5:
            logging.warning(f"Rate limit exceeded for user: {user_id}")
            return jsonify({"error": "Rate limit exceeded"}), 429

        # Get embedding and search results
        query_embedding = get_embedding(query)
        results = query_pinecone(query_embedding, top_k)

        end_time = time.time()
        inference_time = end_time - start_time
        logging.info(f"Request processed in {inference_time:.4f} seconds")

        return jsonify(results), 200

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Custom error handlers
@app.errorhandler(404)
def not_found(error):
    logging.error(f"404 Error: {error}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"500 Error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    try:
        data = request.get_json()
        url = data['url']  # Get the URL to scrape from the request
        start_scraping_thread(url)
        return jsonify({"message": f"Started scraping for {url}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
from scraping import start_scraping_thread

if __name__ == '__main__':
    logging.info("Starting Flask API server.")
    app.run(host='0.0.0.0', port=5000, debug=True)
