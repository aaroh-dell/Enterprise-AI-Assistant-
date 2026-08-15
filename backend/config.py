import os

# In production, this should point to wherever your backend is actually
# deployed - set via an environment variable rather than hardcoded.
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")