from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"

MOVIES_PKL = ARTIFACTS_DIR / "movies.pkl"
SIMILARITY_PKL = ARTIFACTS_DIR / "similarity.pkl"

TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

SIMILARITY_DRIVE_URL = (
    "https://drive.google.com/uc?export=download"
    "&id=1HCNOOnP4NgsKPb6qGqfbr-ekjx08VsvI"
)

MAX_RECOMMENDATIONS = 15
MAX_FEATURES = 5000
TOP_CAST_COUNT = 6
