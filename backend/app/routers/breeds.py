from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Breed
from app.schemas import BreedResponse, BreedTraitResponse

router = APIRouter(prefix="/api/breeds", tags=["breeds"])


@router.get("", response_model=list[BreedResponse])
async def list_breeds(db=Depends(get_db)):
    r = await db.execute(select(Breed).options(selectinload(Breed.traits)))
    breeds = r.scalars().all()
    out = []
    for b in breeds:
        out.append(BreedResponse(
            id=b.id,
            name=b.name,
            image_filename=b.image_filename,
            description=getattr(b, "description", None),
            traits=[BreedTraitResponse(derby_type=t.derby_type, power=t.power, speed=t.speed, intelligence=t.intelligence, stamina=t.stamina, accuracy=t.accuracy) for t in b.traits],
        ))
    return out
