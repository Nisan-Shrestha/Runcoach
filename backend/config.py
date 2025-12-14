import os
import logging
from dotenv import load_dotenv
import boto3

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

# Model IDs
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
LLM_MODEL_ID = "amazon.nova-lite-v1:0"

# Paths
CHROMA_PERSIST_DIR = "knowledge_base/chroma_db"
PDF_DIRECTORY = "knowledge_base/pdfs"


def get_bedrock_client():
    """Create and return a Bedrock runtime client"""
    client_kwargs = {
        "service_name": "bedrock-runtime",
        "region_name": AWS_REGION,
    }
    
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        client_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        client_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY
        if AWS_SESSION_TOKEN:
            client_kwargs["aws_session_token"] = AWS_SESSION_TOKEN
    
    return boto3.client(**client_kwargs)


# Singleton client - created once, reused everywhere
_bedrock_client = None

def get_shared_client():
    """Get the shared Bedrock client (singleton)"""
    global _bedrock_client
    if _bedrock_client is None:
        logger.info(f"🔑 [Config] Initializing Bedrock client (region: {AWS_REGION})")
        _bedrock_client = get_bedrock_client()
        logger.info("✅ [Config] Bedrock client ready")
    return _bedrock_client
