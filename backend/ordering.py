"""Ordering Guide API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db, Item, Store, StoreInventory
from backend.auth import get_current_role, require_manager

router = APIRouter(prefix="/api", tags=["ordering"])


# ===== STORES =====

@router.get("/stores")
def list_stores(role: str = Depends(get_current_role), db: Session = Depends(get_db)):
    stores = db.query(Store).order_by(Store.name).all()
    return [s.name for s in stores]


@router.post("/stores")
def create_store(data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    name = data["name"]
    existing = db.query(Store).filter(Store.name == name).first()
    if not existing:
        db.add(Store(name=name))
        db.commit()
    return {"name": name}


# ===== ITEMS =====

@router.get("/items")
def list_items(role: str = Depends(get_current_role), db: Session = Depends(get_db)):
    items = db.query(Item).order_by(Item.id).all()
    return [i.to_dict() for i in items]


@router.post("/items")
def create_item(data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    data.pop("id", None)
    data.pop("par", None)
    data.pop("onHand", None)
    item = Item(
        category=data.get("category", ""),
        vendor=data.get("vendor", ""),
        pack_size=data.get("packSize", ""),
        brand=data.get("brand", ""),
        item=data.get("item", ""),
        unit=data.get("unit", "each"),
        total_weight_oz=data.get("totalWeightOz", 0),
        units_per_pack=data.get("unitsPerPack", 0),
        price_per_pkg=data.get("pricePerPkg", 0),
        last_price_per_pkg=data.get("lastPricePerPkg", 0),
        per_lb_pint=data.get("perLbPint", 0),
        per_oz_unit=data.get("perOzUnit", 0),
        notes=data.get("notes", ""),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item.to_dict()


@router.put("/items/{item_id}")
def update_item(item_id: int, data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return {"error": "Not found"}, 404

    # Track price changes
    if "pricePerPkg" in data and data["pricePerPkg"] != item.price_per_pkg:
        item.last_price_per_pkg = item.price_per_pkg

    field_map = {
        "category": "category", "vendor": "vendor", "packSize": "pack_size",
        "brand": "brand", "item": "item", "unit": "unit",
        "totalWeightOz": "total_weight_oz", "unitsPerPack": "units_per_pack",
        "pricePerPkg": "price_per_pkg",
        "perLbPint": "per_lb_pint", "perOzUnit": "per_oz_unit", "notes": "notes",
    }
    for js_key, py_key in field_map.items():
        if js_key in data:
            setattr(item, py_key, data[js_key])

    db.commit()
    db.refresh(item)
    return item.to_dict()


@router.delete("/items/{item_id}")
def delete_item(item_id: int, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return {"ok": True}


# ===== INVENTORY =====

@router.get("/inventory/{store_name}")
def get_inventory(store_name: str, role: str = Depends(get_current_role), db: Session = Depends(get_db)):
    rows = db.query(StoreInventory).filter(StoreInventory.store_id == store_name).all()
    return {str(r.item_id): {"par": r.par, "onHand": r.on_hand} for r in rows}


@router.put("/inventory/{store_name}/{item_id}")
def update_inventory(store_name: str, item_id: int, data: dict,
                     role: str = Depends(get_current_role), db: Session = Depends(get_db)):
    # Crew can only update onHand
    if role != "manager":
        if "onHand" not in data:
            return {"error": "Crew can only update on-hand counts"}, 403
        data = {"onHand": data["onHand"]}

    row = db.query(StoreInventory).filter(
        StoreInventory.store_id == store_name,
        StoreInventory.item_id == item_id,
    ).first()

    if row:
        if "par" in data:
            row.par = data["par"]
        if "onHand" in data:
            row.on_hand = data["onHand"]
    else:
        row = StoreInventory(
            store_id=store_name,
            item_id=item_id,
            par=data.get("par", 0),
            on_hand=data.get("onHand", 0),
        )
        db.add(row)

    db.commit()
    db.refresh(row)
    return {"storeId": row.store_id, "itemId": row.item_id, "par": row.par, "onHand": row.on_hand}


# ===== SEED & RESET =====

@router.post("/seed")
def seed_data(data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    seed_items = data.get("items", [])
    seed_stores = data.get("stores", [])

    for name in seed_stores:
        if not db.query(Store).filter(Store.name == name).first():
            db.add(Store(name=name))

    for raw in seed_items:
        item = Item(
            category=raw.get("category", ""),
            vendor=raw.get("vendor", ""),
            pack_size=raw.get("packSize", ""),
            brand=raw.get("brand", ""),
            item=raw.get("item", ""),
            unit=raw.get("unit", "each"),
            total_weight_oz=raw.get("totalWeightOz", 0),
            units_per_pack=raw.get("unitsPerPack", 0),
            price_per_pkg=raw.get("pricePerPkg", 0),
            per_lb_pint=raw.get("perLbPint", 0),
            per_oz_unit=raw.get("perOzUnit", 0),
            notes=raw.get("notes", ""),
        )
        db.add(item)

    db.commit()
    return {"ok": True, "count": len(seed_items)}


@router.post("/reset")
def reset_data(data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    db.query(StoreInventory).delete()
    db.query(Item).delete()
    db.query(Store).delete()
    db.commit()
    return seed_data(data, role, db)
