"""Pricing Matrix API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db, Item, MenuItem, RecipeLine
from backend.auth import get_current_role, require_manager

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


def _calc_unit_cost(item: Item) -> float:
    """Calculate cost per unit (oz or each) from ordering guide data."""
    if item.per_oz_unit and item.per_oz_unit > 0:
        return item.per_oz_unit
    if item.total_weight_oz and item.total_weight_oz > 0 and item.price_per_pkg > 0:
        return item.price_per_pkg / item.total_weight_oz
    if item.price_per_pkg > 0:
        return item.price_per_pkg
    return 0


def _build_menu_item_response(menu_item: MenuItem, db: Session) -> dict:
    """Build full menu item response with recipe lines and calculated costs."""
    result = menu_item.to_dict()

    lines = db.query(RecipeLine).filter(RecipeLine.menu_item_id == menu_item.id).all()
    recipe = []
    cogs = {"tiny": 0, "small": 0, "regular": 0, "shake": 0}

    for line in lines:
        item = db.query(Item).filter(Item.id == line.item_id).first()
        unit_cost = _calc_unit_cost(item) if item else 0

        cost_tiny = line.qty_tiny * unit_cost
        cost_small = line.qty_small * unit_cost
        cost_regular = line.qty_regular * unit_cost
        cost_shake = line.qty_shake * unit_cost

        cogs["tiny"] += cost_tiny
        cogs["small"] += cost_small
        cogs["regular"] += cost_regular
        cogs["shake"] += cost_shake

        recipe.append({
            **line.to_dict(),
            "itemName": item.item if item else "",
            "itemCategory": item.category if item else "",
            "unitCost": round(unit_cost, 4),
            "costTiny": round(cost_tiny, 2),
            "costSmall": round(cost_small, 2),
            "costRegular": round(cost_regular, 2),
            "costShake": round(cost_shake, 2),
        })

    result["recipeLines"] = recipe
    result["cogs"] = {k: round(v, 2) for k, v in cogs.items()}

    # Calculate profit and margin per size
    prices = {
        "tiny": menu_item.price_tiny,
        "small": menu_item.price_small,
        "regular": menu_item.price_regular,
        "shake": menu_item.price_shake,
    }
    profit = {}
    margin = {}
    for size in ["tiny", "small", "regular", "shake"]:
        p = prices[size]
        c = cogs[size]
        profit[size] = round(p - c, 2) if p else 0
        margin[size] = round(((p - c) / p) * 100, 1) if p and p > 0 else 0

    result["profit"] = profit
    result["margin"] = margin

    return result


# ===== MENU ITEMS =====

@router.get("/menu-items")
def list_menu_items(role: str = Depends(get_current_role), db: Session = Depends(get_db)):
    items = db.query(MenuItem).order_by(MenuItem.name).all()
    return [_build_menu_item_response(m, db) for m in items]


@router.get("/menu-items/{item_id}")
def get_menu_item(item_id: int, role: str = Depends(get_current_role), db: Session = Depends(get_db)):
    m = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not m:
        return {"error": "Not found"}
    return _build_menu_item_response(m, db)


@router.post("/menu-items")
def create_menu_item(data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    m = MenuItem(
        name=data.get("name", "New Item"),
        menu_type=data.get("menuType", "special"),
        price_tiny=data.get("priceTiny", 4.00),
        price_small=data.get("priceSmall", 6.00),
        price_regular=data.get("priceRegular", 8.00),
        price_shake=data.get("priceShake", 9.50),
        cyo_base_tiny=data.get("cyoBaseTiny", 2.00),
        cyo_base_small=data.get("cyoBaseSmall", 3.00),
        cyo_base_regular=data.get("cyoBaseRegular", 5.00),
        cyo_base_shake=data.get("cyoBaseShake", 6.50),
        cyo_per_topping=data.get("cyoPerTopping", 1.00),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _build_menu_item_response(m, db)


@router.put("/menu-items/{item_id}")
def update_menu_item(item_id: int, data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    m = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not m:
        return {"error": "Not found"}

    field_map = {
        "name": "name", "menuType": "menu_type",
        "priceTiny": "price_tiny", "priceSmall": "price_small",
        "priceRegular": "price_regular", "priceShake": "price_shake",
        "cyoBaseTiny": "cyo_base_tiny", "cyoBaseSmall": "cyo_base_small",
        "cyoBaseRegular": "cyo_base_regular", "cyoBaseShake": "cyo_base_shake",
        "cyoPerTopping": "cyo_per_topping",
    }
    for js_key, py_key in field_map.items():
        if js_key in data:
            setattr(m, py_key, data[js_key])

    db.commit()
    db.refresh(m)
    return _build_menu_item_response(m, db)


@router.delete("/menu-items/{item_id}")
def delete_menu_item(item_id: int, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    m = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if m:
        db.delete(m)
        db.commit()
    return {"ok": True}


# ===== RECIPE LINES =====

@router.post("/menu-items/{item_id}/lines")
def add_recipe_line(item_id: int, data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    line = RecipeLine(
        menu_item_id=item_id,
        item_id=data.get("itemId"),
        category=data.get("category", "toppings"),
        qty_tiny=data.get("qtyTiny", 0),
        qty_small=data.get("qtySmall", 0),
        qty_regular=data.get("qtyRegular", 0),
        qty_shake=data.get("qtyShake", 0),
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    # Return the full menu item so costs recalculate
    m = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    return _build_menu_item_response(m, db)


@router.put("/recipe-lines/{line_id}")
def update_recipe_line(line_id: int, data: dict, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    line = db.query(RecipeLine).filter(RecipeLine.id == line_id).first()
    if not line:
        return {"error": "Not found"}

    for js_key, py_key in {"itemId": "item_id", "category": "category",
                            "qtyTiny": "qty_tiny", "qtySmall": "qty_small",
                            "qtyRegular": "qty_regular", "qtyShake": "qty_shake"}.items():
        if js_key in data:
            setattr(line, py_key, data[js_key])

    db.commit()
    m = db.query(MenuItem).filter(MenuItem.id == line.menu_item_id).first()
    return _build_menu_item_response(m, db)


@router.delete("/recipe-lines/{line_id}")
def delete_recipe_line(line_id: int, role: str = Depends(require_manager), db: Session = Depends(get_db)):
    line = db.query(RecipeLine).filter(RecipeLine.id == line_id).first()
    if not line:
        return {"ok": True}
    menu_item_id = line.menu_item_id
    db.delete(line)
    db.commit()
    m = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    return _build_menu_item_response(m, db)
