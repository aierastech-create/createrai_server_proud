import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Debug
print("🔑 API KEY Loaded:", bool(os.getenv("GROQ_API_KEY")))

# LLM instance
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=1024,
)


def safe_invoke(prompt: str):
    """Invoke LLM with automatic retry on rate limit errors."""
    retries = 0
    max_retries = 5

    while retries < max_retries:
        try:
            return llm.invoke(prompt)
        except Exception as e:
            if "rate_limit" in str(e).lower():
                wait_time = 2 ** retries  # exponential backoff: 1, 2, 4, 8, 16s
                print(f"⏳ Rate limit hit... retrying in {wait_time}s (attempt {retries + 1}/{max_retries})")
                time.sleep(wait_time)
                retries += 1
            else:
                raise e

    raise RuntimeError("Max retries exceeded due to rate limiting")
