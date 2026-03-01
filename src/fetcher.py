from __future__ import annotations

import requests

from src.config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL

_PLACEHOLDER = "https://placehold.co/500x750/1a1a2e/ffffff?text=No+Poster"
_TIMEOUT = 10


def _get(path: str, params: dict | None = None) -> dict:
    url = f"{TMDB_BASE_URL}{path}"
    merged_params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    if params:
        merged_params.update(params)
    resp = requests.get(url, params=merged_params, timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def fetch_movie_details(movie_id: int) -> dict:
    if not TMDB_API_KEY:
        return {
            "poster": _PLACEHOLDER,
            "overview": "",
            "rating": 0.0,
            "year": "",
            "genres": [],
        }
    try:
        data = _get(f"/movie/{movie_id}")
        poster_path = data.get("poster_path")
        release_date = data.get("release_date", "")
        return {
            "poster": (
                f"{TMDB_IMAGE_BASE_URL}{poster_path}"
                if poster_path
                else _PLACEHOLDER
            ),
            "overview": data.get("overview", ""),
            "rating": round(float(data.get("vote_average", 0)), 1),
            "year": release_date[:4] if release_date else "",
            "genres": [g["name"] for g in data.get("genres", [])],
        }
    except (requests.RequestException, ValueError, KeyError):
        return {
            "poster": _PLACEHOLDER,
            "overview": "",
            "rating": 0.0,
            "year": "",
            "genres": [],
        }


def fetch_trending(page: int = 1) -> list[dict]:
    if not TMDB_API_KEY:
        return []
    try:
        data = _get("/trending/movie/week", {"page": page})
        results = []
        for item in data.get("results", [])[:10]:
            poster_path = item.get("poster_path")
            release_date = item.get("release_date", "")
            results.append(
                {
                    "title": item.get("title", ""),
                    "movie_id": item.get("id"),
                    "poster": (
                        f"{TMDB_IMAGE_BASE_URL}{poster_path}"
                        if poster_path
                        else _PLACEHOLDER
                    ),
                    "rating": round(float(item.get("vote_average", 0)), 1),
                    "year": release_date[:4] if release_date else "",
                }
            )
        return results
    except (requests.RequestException, ValueError, KeyError):
        return []
