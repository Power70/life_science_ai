import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy import delete

# Allow running this file directly via `python scripts/clear_database.py`.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import Base, engine
from models import ChatMessage, HCP, Interaction  # noqa: F401


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete all rows from all application tables."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt.",
    )
    return parser.parse_args()


async def clear_database() -> None:
    async with engine.begin() as conn:
        # Delete in reverse dependency order to satisfy foreign key constraints.
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(delete(table))


async def main() -> None:
    args = parse_args()

    if not args.yes:
        answer = input(
            "This will permanently delete all data from application tables. Continue? (yes/no): "
        ).strip().lower()
        if answer not in {"yes", "y"}:
            print("Aborted. No data was deleted.")
            return

    await clear_database()
    await engine.dispose()
    print("Database cleared successfully.")


if __name__ == "__main__":
    asyncio.run(main())
