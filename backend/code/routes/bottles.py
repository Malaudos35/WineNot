# routes/bottles.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# from database import session_local
# import traceback

import models
import schemas
from dependencies import API_PATH_ROOT, get_db, get_current_user
from database import logger
# from Playwright_vinvino import scrape_vivino_info

router = APIRouter(prefix=API_PATH_ROOT , tags=["Wine Bottles"])


# @router.post("/cellars/{cellar_id}/bottles", response_model=schemas.WineBottleOut,
#       status_code=status.HTTP_201_CREATED)
# def add_bottle(cellar_id: str, payload: schemas.WineBottleCreate, db: Session = Depends(get_db),
#       current_user: models.User = Depends(get_current_user)):
#     cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
#     if not cellar:
#         raise HTTPException(status_code=404, detail="Cave à vin non trouvée")
#     if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
#         raise HTTPException(status_code=403, detail="Forbidden")
#     bottle = models.WineBottle(
#         cellar_id=cellar_id,
#         name=payload.name,
#         vintage=payload.vintage,
#         wine_type=payload.wine_type,
#         region=payload.region,
#         country=payload.country,
#         price=payload.price,
#         quantity=payload.quantity or 1,
#         image_url=payload.image_url,
#         notes=payload.notes
#     )
#     db.add(bottle)
#     db.commit()
#     db.refresh(bottle)
#     return bottle

@router.post("/cellars/{cellar_id}/bottles",
    response_model=schemas.WineBottleOut,
    status_code=status.HTTP_201_CREATED)
def add_bottle(
    cellar_id: str,
    payload: schemas.WineBottleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    logger.info("---- ADD BOTTLE START ----")
    logger.info(f"Received payload: {payload.model_dump()}")
    logger.info(f"scrape flag received = {payload.scrape} (type: {type(payload.scrape)})")

    # Vérification cave
    logger.info(f"Checking cellar_id: {cellar_id}")
    cellar = (
        db.query(models.WineCellar)
        .filter(models.WineCellar.id == cellar_id)
        .first()
    )
    if not cellar:
        logger.error("❌ Cave à vin non trouvée.")
        raise HTTPException(status_code=404, detail="Cave à vin non trouvée")

    # Vérification utilisateur
    if cellar.user_id != current_user.id and not current_user.is_admin:  # type: ignore
        logger.warning(f"User {current_user.id} is not owner of cellar {cellar_id}")
        raise HTTPException(status_code=403, detail="Forbidden")

    scraped = None

    # LOG : vérifier si scrape vaut False
    # if not payload.scrape:
    #     logger.warning("⚠️ scrape=False → skipping Vivino scraping.")
    # else:
    #     logger.info(f"Scrape=True → Starting Vivino scraping for:
    #           {payload.name} ({payload.vintage})")
    #     query = f"{payload.name} {payload.vintage or ''}".strip()
    #     logger.info(f"Vivino query used: '{query}'")

    #     try:
    #         scraped = scrape_vivino_info(query)
    #         logger.info(f"Scraped result received: {scraped}")
    #     except Exception as e:
    #         logger.error("❌ Error during scrape_vivino_info execution:")
    #         logger.error(str(e))
    #         logger.error(traceback.format_exc())
    #         scraped = None

    # helper
    def get_field(field, fallback):
        chosen = field if field not in [None, ""] else fallback
        logger.debug(f"get_field() → field='{field}', fallback='{fallback}', chosen='{chosen}'")
        return chosen

    # LOG avant création bouteille
    logger.info("Creating WineBottle model instance...")

    country_fallback = None
    # if scraped and scraped.get("wine_facts") and scraped["wine_facts"].get("Région"):
    #     region_raw = scraped["wine_facts"].get("Région")
    #     country_fallback = region_raw.split("/")[0].strip()
    #     logger.info(f"Extracted country fallback from region:
    #           '{region_raw}' → '{country_fallback}'")

    price_fallback = None
    # if scraped and scraped.get("price"):
    #     try:
    #         logger.warning(scraped.get("price"))
    #         with open("log_scraped_price.txt", "a") as f:
    #             f.write(f"{scraped}\n")
    #         price_fallback = float(scraped["price"])
    #         logger.info(f"Parsed price fallback: {scraped['price']} → {price_fallback}")
    #     except:
    #         logger.error("❌ Failed to convert scraped price to float")

    bottle = models.WineBottle(
        cellar_id=cellar_id,
        name=payload.name,
        vintage=payload.vintage,
        wine_type=get_field(payload.wine_type, scraped["wine_facts"].get("Style de vin")
                            if scraped else None),
        region=get_field(payload.region, scraped["wine_facts"].get("Région") if scraped else None),
        country=get_field(payload.country, country_fallback),
        price=get_field(payload.price, price_fallback),
        quantity=payload.quantity or 1,
        image_url=get_field(payload.image_url, scraped.get("image_url") if scraped else None),
        notes=get_field(payload.notes, scraped.get("description") if scraped else None),
    )

    logger.info(f"Final bottle object: {bottle}")

    db.add(bottle)
    logger.info("Bottle added to session, committing...")
    db.commit()

    logger.info("Commit OK. Refreshing bottle...")
    db.refresh(bottle)

    logger.info("---- ADD BOTTLE END ----")

    return bottle



@router.get("/cellars/{cellar_id}/bottles", response_model=List[schemas.WineBottleOut])
def list_bottles(cellar_id: str, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
    if not cellar:
        raise HTTPException(status_code=404, detail="Cave à vin non trouvée")
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    bottles = db.query(models.WineBottle).filter(models.WineBottle.cellar_id == cellar_id).all()
    return bottles


@router.get("/bottles/{bottle_id}", response_model=schemas.WineBottleOut)
def get_bottle(bottle_id: str, db: Session = Depends(get_db),
               current_user: models.User = Depends(get_current_user)):
    bottle = db.query(models.WineBottle).filter(models.WineBottle.id == bottle_id).first()
    if not bottle:
        raise HTTPException(status_code=404, detail="Bouteille non trouvée")
    cellar = bottle.cellar
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    return bottle


@router.put("/bottles/{bottle_id}", response_model=schemas.WineBottleOut)
def update_bottle(
    bottle_id: str,
    payload: schemas.WineBottleUpdate,  # tous les champs optionnels
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    bottle = db.query(models.WineBottle).filter(models.WineBottle.id == bottle_id).first()
    if not bottle:
        raise HTTPException(status_code=404, detail="Bouteille non trouvée")

    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == bottle.cellar_id).first()
    if not cellar or (cellar.user_id != current_user.id and
                      not current_user.is_admin): # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")

    # Mets à jour uniquement les champs fournis
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bottle, field, value)

    db.commit()
    db.refresh(bottle)
    return bottle


@router.delete("/bottles/{bottle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bottle(bottle_id: str, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
    bottle = db.query(models.WineBottle).filter(models.WineBottle.id == bottle_id).first()
    if not bottle:
        raise HTTPException(status_code=404, detail="Bouteille non trouvée")
    cellar = bottle.cellar
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(bottle)
    db.commit()
    # return None
