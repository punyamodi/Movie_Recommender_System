from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from src.config import MAX_RECOMMENDATIONS, TMDB_API_KEY
from src.fetcher import fetch_movie_details, fetch_trending
from src.recommender import get_recommendations, load_artifacts

st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="https://www.themoviedb.org/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; }
    .movie-title {
        font-weight: 600;
        font-size: 0.88rem;
        text-align: center;
        margin-top: 0.5rem;
        min-height: 2.4rem;
        line-height: 1.3;
    }
    .movie-meta {
        font-size: 0.78rem;
        color: #9ca3af;
        text-align: center;
        margin-top: 0.15rem;
    }
    .rating {
        display: inline-block;
        background: #e50914;
        color: #fff;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    div[data-testid="stImage"] img {
        border-radius: 6px;
        object-fit: cover;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading recommendation engine...")
def _load_artifacts():
    return load_artifacts()


@st.cache_data(ttl=86400, show_spinner=False)
def _movie_details(movie_id: int) -> dict:
    return fetch_movie_details(movie_id)


@st.cache_data(ttl=3600, show_spinner=False)
def _trending() -> list[dict]:
    return fetch_trending()


def _render_card(col, title: str, details: dict) -> None:
    with col:
        st.image(details["poster"], use_container_width=True)
        st.markdown(
            f'<div class="movie-title">{title}</div>',
            unsafe_allow_html=True,
        )
        parts = []
        if details.get("year"):
            parts.append(details["year"])
        if details.get("rating"):
            parts.append(
                f'<span class="rating">{details["rating"]}</span>'
            )
        if parts:
            st.markdown(
                f'<div class="movie-meta">{" &nbsp;·&nbsp; ".join(parts)}</div>',
                unsafe_allow_html=True,
            )


def _render_grid(recs: list[dict], details_list: list[dict]) -> None:
    cols_per_row = 5
    for row_start in range(0, len(recs), cols_per_row):
        row_recs = recs[row_start : row_start + cols_per_row]
        row_details = details_list[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, rec, details in zip(cols, row_recs, row_details):
            _render_card(col, rec["title"], details)
        st.markdown("<br>", unsafe_allow_html=True)


def main() -> None:
    movies, similarity = _load_artifacts()

    st.markdown("## Movie Recommender System")
    st.markdown(
        "Discover movies similar to your favorites using "
        "content-based filtering on the TMDB 5000 dataset."
    )
    st.divider()

    col_select, col_count = st.columns([4, 1])
    with col_select:
        selected_movie: str = st.selectbox(
            "Select a movie",
            options=movies["title"].values,
        )
    with col_count:
        n_recs: int = st.number_input(
            "Recommendations",
            min_value=5,
            max_value=MAX_RECOMMENDATIONS,
            value=10,
            step=1,
        )

    recommend_clicked = st.button("Get Recommendations", type="primary")

    if recommend_clicked:
        recs = get_recommendations(selected_movie, movies, similarity, n=n_recs)
        if not recs:
            st.error("No recommendations found for the selected movie.")
            return

        with st.spinner("Fetching movie details..."):
            with ThreadPoolExecutor(max_workers=10) as executor:
                details_list = list(
                    executor.map(
                        lambda r: _movie_details(r["movie_id"]), recs
                    )
                )

        st.markdown(
            f'<div class="section-header">Movies similar to {selected_movie}</div>',
            unsafe_allow_html=True,
        )
        _render_grid(recs, details_list)
    else:
        if TMDB_API_KEY:
            trending = _trending()
            if trending:
                st.markdown(
                    '<div class="section-header">Trending This Week</div>',
                    unsafe_allow_html=True,
                )
                cols_per_row = 5
                for row_start in range(0, len(trending), cols_per_row):
                    row_items = trending[row_start : row_start + cols_per_row]
                    cols = st.columns(cols_per_row)
                    for col, item in zip(cols, row_items):
                        _render_card(
                            col,
                            item["title"],
                            {
                                "poster": item["poster"],
                                "rating": item["rating"],
                                "year": item["year"],
                            },
                        )
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info(
                "Set TMDB_API_KEY in your .env file to enable movie posters "
                "and trending movies. See .env.example for details."
            )


if __name__ == "__main__":
    main()
