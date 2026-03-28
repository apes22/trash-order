-- CreateTable
CREATE TABLE "Item" (
    "id" SERIAL NOT NULL,
    "category" TEXT NOT NULL,
    "vendor" TEXT NOT NULL DEFAULT '',
    "packSize" TEXT NOT NULL DEFAULT '',
    "brand" TEXT NOT NULL DEFAULT '',
    "item" TEXT NOT NULL,
    "unit" TEXT NOT NULL DEFAULT 'each',
    "totalWeightOz" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "pricePerPkg" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "perLbPint" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "perOzUnit" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "notes" TEXT NOT NULL DEFAULT '',

    CONSTRAINT "Item_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Store" (
    "name" TEXT NOT NULL,

    CONSTRAINT "Store_pkey" PRIMARY KEY ("name")
);

-- CreateTable
CREATE TABLE "StoreInventory" (
    "id" SERIAL NOT NULL,
    "storeId" TEXT NOT NULL,
    "itemId" INTEGER NOT NULL,
    "par" INTEGER NOT NULL DEFAULT 0,
    "onHand" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "StoreInventory_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "StoreInventory_storeId_itemId_key" ON "StoreInventory"("storeId", "itemId");

-- AddForeignKey
ALTER TABLE "StoreInventory" ADD CONSTRAINT "StoreInventory_storeId_fkey" FOREIGN KEY ("storeId") REFERENCES "Store"("name") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StoreInventory" ADD CONSTRAINT "StoreInventory_itemId_fkey" FOREIGN KEY ("itemId") REFERENCES "Item"("id") ON DELETE CASCADE ON UPDATE CASCADE;
