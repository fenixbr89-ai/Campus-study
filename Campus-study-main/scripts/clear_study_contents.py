"""One-time migration: remove all currently published study materials.

Run once against the Campus Study database before starting manual/AI curation.
It does not remove courses, periods, disciplines, topics, users, progress or settings.
"""
import asyncio
from lib.db import db

async def main():
    result = await db.contents.delete_many({})
    print(f"Conteúdos removidos: {result.deleted_count}")

if __name__ == "__main__":
    asyncio.run(main())
