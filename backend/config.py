import os
from dotenv import load_dotenv


load_dotenv()


DATA_BACKEND = os.getenv(
    "DATA_BACKEND",
    "json"
)

JSON_SERVER_URL = os.getenv(
    "JSON_SERVER_URL",
    "http://localhost:3000"
)

DB_API_URL = os.getenv(
    "DB_API_URL",
    "http://localhost:9000"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)