import logging
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

logging.basicConfig(
    filename="logs/analyze_data.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

sns.set_theme(style="whitegrid", palette="muted")
ANALYSIS_DIR = "data/analysis"


def _save(fig: plt.Figure, name: str) -> str:
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    path = os.path.join(ANALYSIS_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved plot: %s", path)
    return path


def load_processed_data(path: str = "data/processed/movies.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["release_date"])
    logger.info("Loaded %d rows from %s", len(df), path)
    return df


# ── 1. Rating Analysis ──────────────────────────────────────────────────────

def analyze_ratings(df: pd.DataFrame) -> dict:
    rated = df.dropna(subset=["tmdb_rating", "imdb_rating"])
    corr = rated["tmdb_rating"].corr(rated["imdb_rating"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Rating Analysis: TMDB vs IMDb", fontsize=14, fontweight="bold")

    # Scatter with regression line
    ax = axes[0]
    sns.regplot(data=rated, x="tmdb_rating", y="imdb_rating", ax=ax,
                scatter_kws={"alpha": 0.7}, line_kws={"color": "red"})
    ax.set_title(f"TMDB vs IMDb Ratings (r = {corr:.2f})")
    ax.set_xlabel("TMDB Rating")
    ax.set_ylabel("IMDb Rating")

    # Distribution overlay
    ax = axes[1]
    sns.kdeplot(rated["tmdb_rating"], ax=ax, label="TMDB", fill=True, alpha=0.4)
    sns.kdeplot(rated["imdb_rating"], ax=ax, label="IMDb", fill=True, alpha=0.4)
    ax.set_title("Rating Distributions")
    ax.set_xlabel("Rating")
    ax.legend()

    _save(fig, "1_rating_analysis.png")
    logger.info("Rating correlation TMDB-IMDb: %.3f", corr)
    return {"tmdb_imdb_correlation": round(corr, 3), "n_rated": len(rated)}


# ── 2. Genre Analysis ───────────────────────────────────────────────────────

def analyze_genres(df: pd.DataFrame) -> dict:
    exploded = (
        df.assign(genre=df["genres"].str.split(", "))
        .explode("genre")
        .dropna(subset=["genre"])
    )
    exploded = exploded[exploded["genre"] != ""]

    genre_counts = exploded["genre"].value_counts()
    genre_ratings = (
        exploded.dropna(subset=["imdb_rating"])
        .groupby("genre")["imdb_rating"]
        .agg(["mean", "count"])
        .query("count >= 3")
        .sort_values("mean", ascending=False)
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Genre Analysis", fontsize=14, fontweight="bold")

    # Most common genres
    ax = axes[0]
    genre_counts.head(10).plot(kind="barh", ax=ax, color=sns.color_palette("muted")[0])
    ax.invert_yaxis()
    ax.set_title("Top 10 Most Common Genres")
    ax.set_xlabel("Number of Movies")

    # Average IMDb rating by genre
    ax = axes[1]
    genre_ratings["mean"].plot(kind="barh", ax=ax, color=sns.color_palette("muted")[2])
    ax.invert_yaxis()
    ax.set_title("Average IMDb Rating by Genre (≥3 movies)")
    ax.set_xlabel("Average IMDb Rating")
    ax.set_xlim(0, 10)

    _save(fig, "2_genre_analysis.png")
    return {
        "top_genre": genre_counts.index[0],
        "highest_rated_genre": genre_ratings["mean"].idxmax(),
    }


# ── 3. Financial Analysis ───────────────────────────────────────────────────

def analyze_financials(df: pd.DataFrame) -> dict:
    fin = df.dropna(subset=["budget", "revenue"]).copy()
    fin["roi"] = (fin["revenue"] - fin["budget"]) / fin["budget"] * 100
    corr = fin["budget"].corr(fin["revenue"])

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Financial Analysis", fontsize=14, fontweight="bold")

    # Budget vs Revenue scatter
    ax = axes[0]
    sc = ax.scatter(
        fin["budget"] / 1e6, fin["revenue"] / 1e6,
        c=fin["imdb_rating"], cmap="RdYlGn", alpha=0.8, s=80,
    )
    plt.colorbar(sc, ax=ax, label="IMDb Rating")
    ax.set_xlabel("Budget ($M)")
    ax.set_ylabel("Revenue ($M)")
    ax.set_title(f"Budget vs Revenue (r = {corr:.2f})")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))

    # Top 10 most profitable
    ax = axes[1]
    top10 = fin.nlargest(10, "profit")[["title", "profit"]].copy()
    top10["title"] = top10["title"].str[:25]
    top10["profit_m"] = top10["profit"] / 1e6
    sns.barplot(data=top10, y="title", x="profit_m", ax=ax,
                palette="Greens_r", orient="h")
    ax.set_title("Top 10 Most Profitable Movies")
    ax.set_xlabel("Profit ($M)")
    ax.set_ylabel("")

    _save(fig, "3_financial_analysis.png")
    logger.info("Budget-revenue correlation: %.3f over %d movies", corr, len(fin))
    return {
        "budget_revenue_correlation": round(corr, 3),
        "most_profitable": fin.loc[fin["profit"].idxmax(), "title"],
        "n_with_financials": len(fin),
    }


# ── 4. Temporal Analysis ────────────────────────────────────────────────────

def analyze_temporal(df: pd.DataFrame) -> dict:
    temp = df.dropna(subset=["release_year", "imdb_rating"]).copy()
    temp["release_year"] = temp["release_year"].astype(int)

    yearly = temp.groupby("release_year").agg(
        count=("title", "count"),
        avg_rating=("imdb_rating", "mean"),
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Temporal Analysis", fontsize=14, fontweight="bold")

    ax = axes[0]
    ax.bar(yearly["release_year"], yearly["count"],
           color=sns.color_palette("muted")[4], edgecolor="white")
    ax.set_title("Movies by Release Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Movies")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    ax = axes[1]
    ax.plot(yearly["release_year"], yearly["avg_rating"],
            marker="o", linewidth=2, color=sns.color_palette("muted")[1])
    ax.set_title("Average IMDb Rating by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average IMDb Rating")
    ax.set_ylim(0, 10)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    _save(fig, "4_temporal_analysis.png")
    best_year = yearly.loc[yearly["avg_rating"].idxmax(), "release_year"]
    return {"best_rated_year": int(best_year), "years_covered": sorted(yearly["release_year"].tolist())}


# ── Summary report ──────────────────────────────────────────────────────────

def generate_summary(df: pd.DataFrame, results: dict) -> str:
    lines = [
        "# Analysis Summary Report",
        "",
        f"**Total movies analysed:** {len(df)}",
        f"**Movies with IMDb ratings:** {df['imdb_rating'].notna().sum()}",
        f"**Movies with Metascores:** {df['metascore'].notna().sum()}",
        f"**Movies with financial data:** {df['profit'].notna().sum()}",
        "",
        "## Key Findings",
        "",
        f"- TMDB ↔ IMDb rating correlation: **{results['ratings']['tmdb_imdb_correlation']}**",
        f"- Most common genre: **{results['genres']['top_genre']}**",
        f"- Highest-rated genre (avg IMDb): **{results['genres']['highest_rated_genre']}**",
        f"- Budget ↔ Revenue correlation: **{results['financials']['budget_revenue_correlation']}**",
        f"- Most profitable movie: **{results['financials']['most_profitable']}**",
        f"- Best-rated release year: **{results['temporal']['best_rated_year']}**",
    ]
    report = "\n".join(lines)
    path = os.path.join(ANALYSIS_DIR, "summary.txt")
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    with open(path, "w") as f:
        f.write(report)
    print(report)
    return report


def main() -> dict:
    os.makedirs("logs", exist_ok=True)
    df = load_processed_data()

    print("Running analyses...")
    results = {
        "ratings": analyze_ratings(df),
        "genres": analyze_genres(df),
        "financials": analyze_financials(df),
        "temporal": analyze_temporal(df),
    }
    generate_summary(df, results)
    print(f"\nPlots saved to {ANALYSIS_DIR}/")
    return results


if __name__ == "__main__":
    main()
