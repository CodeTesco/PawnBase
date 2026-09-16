import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DATABASE_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "database": os.getenv("POSTGRES_DATABASE", "pawnbase"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.environ["POSTGRES_PASSWORD"],
    "port": os.getenv("POSTGRES_PORT", "5432"),
}