"""Run once to create tables and seed breeds + traits + default admin."""
import asyncio
from sqlalchemy import select, text
from app.database import engine, init_db, AsyncSessionLocal
from app.models import Base, Breed, BreedTrait, User
from app.seed_data import BREEDS, DERBY_TYPES, get_rating_list
from app.auth import get_password_hash
from app.config import settings


async def migrate_schema():
    """Add new columns/tables if missing (for existing DBs)."""
    async with engine.begin() as conn:
        is_sqlite = "sqlite" in str(engine.url)
        if is_sqlite:
            for table, col, col_def in [
                ("entries", "keep_type", "VARCHAR(32) DEFAULT 'bench'"),
                ("breeds", "description", "TEXT"),
                ("tournaments", "prize_tier", "VARCHAR(32) DEFAULT 'standard'"),
                ("users", "google_id", "VARCHAR(255)"),
            ]:
                try:
                    r = await conn.execute(text(
                        f"SELECT name FROM pragma_table_info('{table}') WHERE name=:name"
                    ), {"name": col})
                    if r.fetchone() is None:
                        await conn.execute(text(
                            f"ALTER TABLE {table} ADD COLUMN {col} {col_def}"
                        ))
                except Exception:
                    pass
    # Create new tables (e.g. entry_roosters) via metadata
    await init_db()


async def seed():
    await init_db()
    try:
        await migrate_schema()
    except Exception as e:
        print(f"Migration note: {e}")
    async with AsyncSessionLocal() as session:
        r = await session.execute(select(Breed).limit(1))
        if not r.scalar_one_or_none():
            for i, b in enumerate(BREEDS):
                desc = b.get("description")
                breed = Breed(name=b["name"], image_filename=b["image"], description=desc)
                session.add(breed)
                await session.flush()
                for d_idx, derby_type in enumerate(DERBY_TYPES):
                    p, s, iq, st, a = get_rating_list(d_idx, i)
                    session.add(BreedTrait(breed_id=breed.id, derby_type=derby_type, power=p, speed=s, intelligence=iq, stamina=st, accuracy=a))
        else:
            # Update existing breeds with descriptions if missing
            for i, b in enumerate(BREEDS):
                r2 = await session.execute(select(Breed).where(Breed.name == b["name"]))
                existing = r2.scalar_one_or_none()
                if existing and not existing.description and "description" in b:
                    existing.description = b["description"]
        ru = await session.execute(select(User).where(User.email == "admin@example.com"))
        if not ru.scalar_one_or_none():
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                token_balance=settings.starting_tokens,
            )
            session.add(admin_user)
        await session.commit()
    print("Seeded breeds, traits, and admin (admin@example.com / admin123).")


if __name__ == "__main__":
    asyncio.run(seed())
