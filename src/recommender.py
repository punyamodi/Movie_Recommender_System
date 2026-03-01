from __future__ import annotations

import pickle

import pandas as pd
import requests

from src.config import (
    MOVIES_PKL,
    SIMILARITY_PKL,
    SIMILARITY_DRIVE_URL,
    MAX_RECOMMENDATIONS,
)


def _download_similarity() -> None:
    SIMILARITY_PKL.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(SIMILARITY_DRIVE_URL, timeout=180)
    resp.raise_for_status()
    SIMILARITY_PKL.write_bytes(resp.content)


def load_artifacts() -> tuple[pd.DataFrame, object]:
    with open(MOVIES_PKL, "rb") as fh:
        movies = pickle.load(fh)

    if not SIMILARITY_PKL.exists():
        _download_similarity()

    with open(SIMILARITY_PKL, "rb") as fh:
        similarity = pickle.load(fh)

    return movies, similarity


def get_recommendations(
    title: str,
    movies: pd.DataFrame,
    similarity,
    n: int = MAX_RECOMMENDATIONS,
) -> list[dict]:
    matches = movies[movies["title"] == title]
    if matches.empty:
        return []

    idx = int(matches.index[0])
    scores = sorted(
        enumerate(similarity[idx]),
        key=lambda x: x[1],
        reverse=True,
    )

    return [
        {
            "title": movies.iloc[i]["title"],
            "movie_id": int(movies.iloc[i]["movie_id"]),
        }
        for i, _ in scores[1 : n + 1]
    ]
