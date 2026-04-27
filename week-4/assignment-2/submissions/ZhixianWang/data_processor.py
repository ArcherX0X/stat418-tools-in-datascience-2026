import json
import logging
import os
from typing import Dict, List, Tuple

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="logs/data_processor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_raw_data(
    tmdb_path: str = "data/raw/tmdb/movies.json",
    imdb_path: str = "data/raw/imdb/ratings.json",
) -> Tuple[List[Dict], List[Dict]]:
    with open(tmdb_path) as f:
        tmdb_data = json.load(f)
    with open(imdb_path) as f:
        imdb_data = json.load(f)
    logger.info("Loaded %d TMDB and %d IMDb records", len(tmdb_data), len(imdb_data))
    return tmdb_data, imdb_data


def merge_data(tmdb_data: List[Dict], imdb_data: List[Dict]) -> pd.DataFrame:
    tmdb_df = pd.DataFrame(tmdb_data)
    imdb_df = pd.DataFrame(imdb_data)

    # Flatten list columns
    tmdb_df["genres"] = tmdb_df["genres"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else ""
    )
    tmdb_df["production_companies"] = tmdb_df["production_companies"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else ""
    )
    tmdb_df["cast"] = tmdb_df["cast"].apply(
        lambda x: ", ".join(m["name"] for m in x) if isinstance(x, list) else ""
    )
    tmdb_df["crew"] = tmdb_df["crew"].apply(
        lambda x: ", ".join(m["name"] for m in x) if isinstance(x, list) else ""
    )

    merged = tmdb_df.merge(imdb_df, on="imdb_id", how="left")
    logger.info("Merged dataframe: %d rows, %d columns", *merged.shape)
    return merged


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Standardise dates
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year

    # Numeric coercion
    for col in ["runtime", "budget", "revenue", "tmdb_rating", "tmdb_vote_count",
                "imdb_rating", "imdb_votes", "metascore"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Nullify zero budgets/revenues (TMDB uses 0 for unknown)
    df.loc[df["budget"] == 0, "budget"] = None
    df.loc[df["revenue"] == 0, "revenue"] = None

    # Profit column (only when both are available)
    mask = df["budget"].notna() & df["revenue"].notna()
    df["profit"] = None
    df.loc[mask, "profit"] = df.loc[mask, "revenue"] - df.loc[mask, "budget"]

    # Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["tmdb_id"])
    logger.info("Removed %d duplicate rows", before - len(df))

    # Drop rows with no title
    df = df.dropna(subset=["title"])

    logger.info("Clean dataframe: %d rows", len(df))
    return df.reset_index(drop=True)


def save_processed_data(df: pd.DataFrame, output_dir: str = "data/processed") -> None:
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "movies.csv")
    json_path = os.path.join(output_dir, "movies.json")

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2, date_format="iso")

    logger.info("Saved processed data to %s and %s", csv_path, json_path)
    print(f"Saved {len(df)} records to {csv_path}")


def main() -> pd.DataFrame:
    os.makedirs("logs", exist_ok=True)
    tmdb_data, imdb_data = load_raw_data()
    df = merge_data(tmdb_data, imdb_data)
    df = clean_data(df)
    save_processed_data(df)

    print("\nDataset overview:")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  IMDb ratings available: {df['imdb_rating'].notna().sum()}")
    print(f"  Metascores available:   {df['metascore'].notna().sum()}")
    print(f"  Budget/revenue known:   {df['profit'].notna().sum()}")
    return df


if __name__ == "__main__":
    main()
