"""Run once to create tables and seed breeds + traits + default admin."""
import asyncio
from sqlalchemy import select
from app.database import engine, init_db, AsyncSessionLocal
from app.models import Base, Breed, BreedTrait, User
from app.seed_data import BREEDS, DERBY_TYPES, get_rating_list
from app.auth import get_password_hash
from app.config import settings


async def seed():
    await init_db()
    async with AsyncSessionLocal() as session:
        r = await session.execute(select(Breed).limit(1))
        if not r.scalar_one_or_none():
            for i, b in enumerate(BREEDS):
                breed = Breed(name=b["name"], image_filename=b["image"])
                session.add(breed)
                await session.flush()
                for d_idx, derby_type in enumerate(DERBY_TYPES):
                    p, s, iq, st, a = get_rating_list(d_idx, i)
                    session.add(BreedTrait(breed_id=breed.id, derby_type=derby_type, power=p, speed=s, intelligence=iq, stamina=st, accuracy=a))
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
