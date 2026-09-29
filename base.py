import os

import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
MODEL_KEY = os.getenv('MODEL_KEY')
MODEL_MODEL = os.getenv('MODEL_MODEL')
MODEL_URL = os.getenv('MODEL_URL')
model = ChatOpenAI(
    model=MODEL_MODEL,
    api_key=MODEL_KEY,
    base_url=MODEL_URL,
)