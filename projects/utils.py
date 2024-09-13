from dotenv import load_dotenv
import os
import pinecone
from transformers import AutoTokenizer, AutoModel
import torch
import warnings

# Suppress specific FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning, message="`clean_up_tokenization_spaces`")


load_dotenv()

# Load API key and environment from environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")

# Create an instance of the Pinecone class
pc = pinecone.Pinecone(api_key=pinecone_api_key)

# Connect to or create the index
index_name = "trademarkia"  # Replace with your actual index name

# Check if the index exists, if not, create it
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Assuming you're using a BERT model with 768 dimensions
        metric='cosine',  # Use cosine similarity metric
        spec=pinecone.ServerlessSpec(
            cloud="gcp",  # Use your cloud provider and region (e.g., 'gcp' or 'aws')
            region=pinecone_environment  # Load the correct region from environment variables
        )
    )

# Connect to the index
pinecone_index = pc.Index(index_name)

# Load pre-trained BERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained('bert-base-uncased')

def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    outputs = model(**inputs)
    decoded_text = tokenizer.decode(inputs['input_ids'][0], clean_up_tokenization_spaces=True)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

def query_pinecone(embedding, top_k):
    # Query Pinecone index
    result = pinecone_index.query(vector=embedding.flatten().tolist(), top_k=top_k)
    return [{"id": match["id"], "score": match["score"]} for match in result["matches"]]
