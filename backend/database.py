"""SQLAlchemy models and database setup."""

import os
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./tic_management.db")

# Render uses postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    sub_category = Column(String, default="")
    vendor = Column(String, default="")
    pack_size = Column(String, default="")
    brand = Column(String, default="")
    item = Column(String, nullable=False)
    unit = Column(String, default="each")
    total_weight_oz = Column(Float, default=0)
    units_per_pack = Column(Float, default=0)
    price_per_pkg = Column(Float, default=0)
    last_price_per_pkg = Column(Float, default=0)
    costing_unit = Column(String, default="")
    costing_units_per_pack = Column(Float, default=0)
    per_lb_pint = Column(Float, default=0)
    per_oz_unit = Column(Float, default=0)
    notes = Column(String, default="")

    inventory = relationship("StoreInventory", back_populates="item", cascade="all, delete-orphan")

    # Conversion factors: how many oz in one unit
    UNIT_TO_OZ = {
        "oz": 1,
        "lb": 16,
        "pint": 16,
        "gallon": 128,
        "gal": 128,
    }

    def _auto_costing_units(self):
        """Auto-calculate costing units per pack from buying unit → costing unit conversion."""
        # Need buying unit, units per pack, and costing unit to convert
        if not self.unit or not self.costing_unit or not self.units_per_pack:
            return 0
        buy = self.unit.lower().strip()
        cost = self.costing_unit.lower().strip()
        if buy == cost:
            return self.units_per_pack
        # Convert: buying units → oz → costing units
        buy_oz = self.UNIT_TO_OZ.get(buy)
        cost_oz = self.UNIT_TO_OZ.get(cost)
        if buy_oz and cost_oz:
            total_oz = self.units_per_pack * buy_oz
            return round(total_oz / cost_oz, 2)
        return 0

    def to_dict(self):
        costing_units = self._auto_costing_units()
        return {
            "id": self.id,
            "category": self.category,
            "subCategory": self.sub_category,
            "vendor": self.vendor,
            "packSize": self.pack_size,
            "brand": self.brand,
            "item": self.item,
            "unit": self.unit,
            "totalWeightOz": self.total_weight_oz,
            "unitsPerPack": self.units_per_pack,
            "pricePerPkg": self.price_per_pkg,
            "pricePerBuyingUnit": round(self.price_per_pkg / self.units_per_pack, 4) if self.units_per_pack else 0,
            "lastPricePerPkg": self.last_price_per_pkg,
            "costingUnit": self.costing_unit,
            "costingUnitsPerPack": costing_units,
            "pricePerCostingUnit": round(self.price_per_pkg / costing_units, 4) if costing_units else 0,
            "perLbPint": self.per_lb_pint,
            "perOzUnit": self.per_oz_unit,
            "notes": self.notes,
        }


class Store(Base):
    __tablename__ = "stores"

    name = Column(String, primary_key=True)
    inventory = relationship("StoreInventory", back_populates="store", cascade="all, delete-orphan")


class StoreInventory(Base):
    __tablename__ = "store_inventory"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, ForeignKey("stores.name", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    par = Column(Integer, default=0)
    on_hand = Column(Integer, default=0)

    store = relationship("Store", back_populates="inventory")
    item = relationship("Item", back_populates="inventory")

    __table_args__ = (UniqueConstraint("store_id", "item_id"),)


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    menu_type = Column(String, default="special")  # "special" or "cyo"
    price_tiny = Column(Float, default=0)
    price_small = Column(Float, default=0)
    price_regular = Column(Float, default=0)
    price_shake = Column(Float, default=0)
    # CYO fields
    cyo_base_tiny = Column(Float, default=0)
    cyo_base_small = Column(Float, default=0)
    cyo_base_regular = Column(Float, default=0)
    cyo_base_shake = Column(Float, default=0)
    cyo_per_topping = Column(Float, default=1.0)
    sort_order = Column(Integer, default=0)

    recipe_lines = relationship("RecipeLine", back_populates="menu_item", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "menuType": self.menu_type,
            "sortOrder": self.sort_order,
            "priceTiny": self.price_tiny,
            "priceSmall": self.price_small,
            "priceRegular": self.price_regular,
            "priceShake": self.price_shake,
            "cyoBaseTiny": self.cyo_base_tiny,
            "cyoBaseSmall": self.cyo_base_small,
            "cyoBaseRegular": self.cyo_base_regular,
            "cyoBaseShake": self.cyo_base_shake,
            "cyoPerTopping": self.cyo_per_topping,
        }


class RecipeLine(Base):
    __tablename__ = "recipe_lines"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, default="toppings")  # creamy base, toppings, packaging, liquid modifier
    qty_tiny = Column(Float, default=0)
    qty_small = Column(Float, default=0)
    qty_regular = Column(Float, default=0)
    qty_shake = Column(Float, default=0)

    menu_item = relationship("MenuItem", back_populates="recipe_lines")
    item = relationship("Item")

    def to_dict(self):
        return {
            "id": self.id,
            "menuItemId": self.menu_item_id,
            "itemId": self.item_id,
            "category": self.category,
            "qtyTiny": self.qty_tiny,
            "qtySmall": self.qty_small,
            "qtyRegular": self.qty_regular,
            "qtyShake": self.qty_shake,
        }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
    _run_migrations()


def _run_migrations():
    """Add columns that don't exist yet (SQLAlchemy create_all doesn't alter existing tables)."""
    from sqlalchemy import text, inspect
    insp = inspect(engine)

    migrations = [
        ("items", "units_per_pack", "ALTER TABLE items ADD COLUMN units_per_pack FLOAT DEFAULT 0"),
        ("items", "costing_unit", "ALTER TABLE items ADD COLUMN costing_unit VARCHAR DEFAULT ''"),
        ("items", "costing_units_per_pack", "ALTER TABLE items ADD COLUMN costing_units_per_pack FLOAT DEFAULT 0"),
        ("items", "sub_category", "ALTER TABLE items ADD COLUMN sub_category VARCHAR DEFAULT ''"),
        ("menu_items", "sort_order", "ALTER TABLE menu_items ADD COLUMN sort_order INTEGER DEFAULT 0"),
        ("menu_items", "id", None),
        ("recipe_lines", "id", None),
    ]

    existing_tables = insp.get_table_names()
    for table, column, sql in migrations:
        if table not in existing_tables:
            continue
        if sql is None:
            continue
        cols = [c["name"] for c in insp.get_columns(table)]
        if column not in cols:
            with engine.begin() as conn:
                conn.execute(text(sql))
                print(f"Migration: added {column} to {table}")

    # Data migration: parse sub_category from item names
    if "items" in existing_tables:
        with engine.begin() as conn:
            rows = conn.execute(text("SELECT id, item, sub_category FROM items WHERE sub_category = '' OR sub_category IS NULL")).fetchall()
            count = 0
            for row in rows:
                item_name = row[1]
                if ',' in item_name:
                    parts = item_name.split(',', 1)
                    sub_cat = parts[0].strip()
                    clean_name = parts[1].strip()
                    conn.execute(text("UPDATE items SET sub_category = :sub, item = :name WHERE id = :id"),
                                 {"sub": sub_cat, "name": clean_name, "id": row[0]})
                    count += 1
            if count > 0:
                print(f"Migration: parsed sub_category from {count} item names")
