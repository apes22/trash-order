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
    vendor = Column(String, default="")
    pack_size = Column(String, default="")
    brand = Column(String, default="")
    item = Column(String, nullable=False)
    unit = Column(String, default="each")
    total_weight_oz = Column(Float, default=0)
    units_per_pack = Column(Float, default=0)
    price_per_pkg = Column(Float, default=0)
    last_price_per_pkg = Column(Float, default=0)
    per_lb_pint = Column(Float, default=0)
    per_oz_unit = Column(Float, default=0)
    notes = Column(String, default="")

    inventory = relationship("StoreInventory", back_populates="item", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "vendor": self.vendor,
            "packSize": self.pack_size,
            "brand": self.brand,
            "item": self.item,
            "unit": self.unit,
            "totalWeightOz": self.total_weight_oz,
            "unitsPerPack": self.units_per_pack,
            "pricePerPkg": self.price_per_pkg,
            "pricePerUnit": round(self.price_per_pkg / self.units_per_pack, 4) if self.units_per_pack else 0,
            "lastPricePerPkg": self.last_price_per_pkg,
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

    recipe_lines = relationship("RecipeLine", back_populates="menu_item", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "menuType": self.menu_type,
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
