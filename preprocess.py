from __future__ import annotations

import argparse
import ast
import pickle
from pathlib import Path

import nltk
import pandas as pd
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import ARTIFACTS_DIR, MOVIES_PKL, SIMILARITY_PKL, MAX_FEATURES, TOP_CAST_COUNT

nltk.download("punkt", quiet=True)

_stemmer = PorterStemmer()


def _parse_names(value: str) -> list[str]:
    return [item["name"] for item in ast.literal_eval(value)]


def _parse_cast(value: str) -> list[str]:
    return [item["name"] for item in ast.literal_eval(value)[:TOP_CAST_COUNT]]


def _parse_director(value: str) -> list[str]:
    return [
        item["name"]
        for item in ast.literal_eval(value)
        if item["job"] == "Director"
    ]


def _normalize(tokens: list[str]) -> list[str]:
    return [t.replace(" ", "") for t in tokens]


def _stem(text: str) -> str:
    return " ".join(_stemmer.stem(word) for word in text.split())


def build_movies_dataframe(movies_csv: Path, credits_csv: Path) -> pd.DataFrame:
    movies = pd.read_csv(movies_csv)
    credits = pd.read_csv(credits_csv)
    merged = movies.merge(credits, on="title")

    df = merged[
        [
            "movie_id",
            "title",
            "overview",
            "genres",
            "keywords",
            "cast",
            "crew",
            "original_language",
        ]
    ].copy()

    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    df["genres"] = df["genres"].apply(_parse_names)
    df["keywords"] = df["keywords"].apply(_parse_names)
    df["cast"] = df["cast"].apply(_parse_cast)
    df["crew"] = df["crew"].apply(_parse_director)
    df["overview"] = df["overview"].apply(str.split)
    df["original_language"] = df["original_language"].apply(lambda x: [x])

    for col in ("genres", "keywords", "cast", "crew"):
        df[col] = df[col].apply(_normalize)

    df["tags"] = (
        df["genres"]
        + df["cast"]
        + df["crew"]
        + df["keywords"]
        + df["original_language"]
        + df["overview"]
    )

    result = df[["movie_id", "title", "tags"]].copy()
    result["tags"] = result["tags"].apply(lambda x: " ".join(x).lower())
    result["tags"] = result["tags"].apply(_stem)
    return result


def build_similarity(movies_df: pd.DataFrame):
    cv = CountVectorizer(max_features=MAX_FEATURES, stop_words="english")
    vectors = cv.fit_transform(movies_df["tags"]).toarray()
    return cosine_similarity(vectors)


def run(movies_csv: Path, credits_csv: Path) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Reading data from {movies_csv} and {credits_csv} ...")
    movies_df = build_movies_dataframe(movies_csv, credits_csv)
    print(f"Processed {len(movies_df)} movies")

    print("Computing cosine similarity matrix ...")
    sim = build_similarity(movies_df)

    print("Saving artifacts ...")
    with open(MOVIES_PKL, "wb") as fh:
        pickle.dump(movies_df, fh)
    with open(SIMILARITY_PKL, "wb") as fh:
        pickle.dump(sim, fh)

    print(f"Done. Artifacts written to {ARTIFACTS_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build movie recommender artifacts from TMDB 5000 dataset"
    )
    parser.add_argument(
        "--movies",
        required=True,
        metavar="PATH",
        help="Path to tmdb_5000_movies.csv",
    )
    parser.add_argument(
        "--credits",
        required=True,
        metavar="PATH",
        help="Path to tmdb_5000_credits.csv",
    )
    args = parser.parse_args()
    run(Path(args.movies), Path(args.credits))


if __name__ == "__main__":
    main()
