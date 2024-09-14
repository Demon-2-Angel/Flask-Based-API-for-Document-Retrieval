# 21BAI10054_ML

# Flask-Based API for Document Retrieval with Pinecone, Caching, Rate Limiting, and Background Scraping

## Project Overview

This project is a Flask-based API designed to retrieve documents using Pinecone for vector search. It includes features like:
- Caching for faster retrieval
- Rate limiting to control API usage
- Background scraping to periodically update the database
- Dockerization for easy deployment and scalability

The application uses:
- **Pinecone** for vector-based document retrieval
- **Hugging Face Transformers** (BERT) for generating text embeddings
- **Flask-SQLAlchemy** for user management and tracking API usage
- **Flask-Caching** for caching API results
- **Flask-Limiter** for rate-limiting users
- **Docker** for packaging the app into a containerized environment

---

## Approach and Project Flow

### 1. **Setting Up the Flask API**
We started by setting up the basic Flask application and API endpoints:
- `/health`: A simple endpoint to check if the API is running.
- `/search`: An endpoint to query Pinecone with text embeddings and retrieve results.

### 2. **Embedding Generation with BERT**
For each query, we generate embeddings using a pre-trained **BERT model** (via Hugging Face’s `transformers` library). These embeddings are used to perform vector searches using Pinecone.

### 3. **Integration with Pinecone**
We integrated **Pinecone**, a vector database, to store and query document embeddings. This allows efficient and fast retrieval of documents based on similarity search.

### 4. **Rate Limiting and User Management**
We implemented **rate limiting** using `Flask-Limiter` to restrict users from making more than 5 requests per minute:
- Users are tracked using a SQLite database with **Flask-SQLAlchemy**.
- If a user exceeds the rate limit, the API returns an HTTP 429 error (Too Many Requests).

### 5. **Caching for Faster Retrieval**
We added **caching** using `Flask-Caching`. Caching ensures that identical queries are served from memory, reducing the need to hit the database and vector search engine repeatedly. Cached results expire after 5 minutes.

### 6. **Background Scraping**
We implemented a background scraper that can scrape a user-provided website for articles or data and update the Pinecone index with new documents:
- Scraping is handled by `BeautifulSoup`.
- The scraping task runs in the background on a separate thread and updates the Pinecone index periodically.

### 7. **Dockerization**
We Dockerized the project using a **Dockerfile**. This allows the project to be easily deployed in any environment with consistent behavior across different systems.

---

## Features

1. **Document Retrieval**: Retrieve documents based on similarity search using embeddings.
2. **Rate Limiting**: Prevent API abuse by limiting requests to 5 per minute per user.
3. **Caching**: Cache the results of similar queries for faster response times.
4. **User Management**: Track the number of API calls made by each user.
5. **Background Scraping**: Scrape websites in the background to continuously update the Pinecone index.
6. **Dockerization**: Easily run and deploy the application using Docker.

---

## Project Structure

```
project/
├── app.py               # Main Flask application
├── database.py          # Database setup for user management
├── cache.py             # Caching configuration
├── limiter.py           # Rate limiting configuration
├── utils.py             # Utility functions (embedding, Pinecone query)
├── scraping.py          # Background scraping logic
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── .env                 # Environment variables (not committed to version control)
├── .dockerignore        # Ignore unnecessary files in the Docker build
└── README.md            # Project documentation
```

## Key Files:

- **`app.py`**: Contains the Flask application and all API routes.
- **`database.py`**: Handles the setup and schema for user management using SQLite.
- **`cache.py`**: Manages caching for faster response times.
- **`limiter.py`**: Implements rate-limiting functionality.
- **`utils.py`**: Provides helper functions for generating embeddings and querying Pinecone.
- **`scraping.py`**: Contains the logic for background scraping and updating the Pinecone index.
- **`Dockerfile`**: Used to build and run the application in a Docker container.

---

## Setup and Installation

### Prerequisites:
- **Python 3.9+**
- **Docker** (optional, for running the app in a container)

### Step 1: Clone the Repository

```
git clone <repository-url>
cd project
```

### Step 2: Set Up a Virtual Environment (Optional but Recommended)
```
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```
### Step 3: Install the Dependencies

```
pip install -r requirements.txt
```

###Step 4: Set Up Environment Variables

Create a .env file in the project root and add your Pinecone API key and environment:

```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
```

### Step 5: Initialize the Database
To set up the database, run the following code:

```
>>> from app import db, app
>>> with app.app_context():
>>>     db.create_all()
```

### Step 6: Run the Application

```
python app.py
```
The app will be running at `http://localhost:5000`.

## Docker Setup

### Step 1: Build the Docker Image

```
docker build -t flask-app .
```
### Step 2: Run the Docker Container
```
docker run -p 5000:5000 flask-app
```
Now, your app will be running at   `http://localhost:5000`.

## API Endpoints

1. Health Check

**URL**: `/health`
**Method**: `GET`
**Description**: Checks if the API is running.
**Response**:
```
json
Copy code
{
  "status": "API is running"
}
```

2. Search

**URL**: `/search`
**Method**: `POST`
**Description**: Search documents based on text queries.
**Request Body**:
```
json
Copy code
{
  "query": "Your search query",
  "user_id": "user123",
  "top_k": 3
}
```
**Response**: Returns a list of matching documents based on the query.

3. Start Scraping
**URL**: `/start_scraping`
**Method**: `POST`
**Description**: Starts the background scraping process for a specific site.
**Request Body**:
```
json
Copy code
{
  "url": "https://example.com"
}
```

**Response**:
```
json

{
  "message": "Started scraping for https://example.com"
}
```

## Troubleshooting

### Common Issues:
1. Rate Limit Exceeded: If you hit the rate limit, the API will return a 429 error.
2. Caching Delay: If cached results are returned, you might need to wait 5 minutes before new results appear.
3. Logs: The application logs all requests and errors in `api.log`.
Background scraping logs are written to scraping.log.

## Future Enhancements

1. Authentication: Adding API key-based authentication for added security.
2. Improved Error Handling: More detailed error messages for invalid queries or scraping failures.
3. Support for Multiple Scraping Sites: Enhance the scraper to handle multiple sites in parallel.
