const express = require('express');
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('@prisma/client');
const path = require('path');

const app = express();
const prisma = new PrismaClient();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-change-in-production';
const APP_PIN = process.env.APP_PIN || '1234';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ===== AUTH =====
function auth(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Not authenticated' });
  try {
    jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}

app.post('/api/login', (req, res) => {
  if (req.body.pin === APP_PIN) {
    const token = jwt.sign({ auth: true }, JWT_SECRET, { expiresIn: '90d' });
    res.json({ token });
  } else {
    res.status(401).json({ error: 'Wrong PIN' });
  }
});

// ===== STORES =====
app.get('/api/stores', auth, async (req, res) => {
  const stores = await prisma.store.findMany({ orderBy: { name: 'asc' } });
  res.json(stores.map(s => s.name));
});

app.post('/api/stores', auth, async (req, res) => {
  const store = await prisma.store.upsert({
    where: { name: req.body.name },
    create: { name: req.body.name },
    update: {},
  });
  res.json(store);
});

// ===== ITEMS =====
app.get('/api/items', auth, async (req, res) => {
  const items = await prisma.item.findMany({ orderBy: { id: 'asc' } });
  res.json(items);
});

app.post('/api/items', auth, async (req, res) => {
  const { id, ...data } = req.body;
  const item = await prisma.item.create({ data });
  res.json(item);
});

app.put('/api/items/:id', auth, async (req, res) => {
  const { id, inventory, ...data } = req.body;
  const itemId = parseInt(req.params.id);

  // If price is changing, save the old price as lastPricePerPkg
  if (data.pricePerPkg !== undefined) {
    const current = await prisma.item.findUnique({ where: { id: itemId } });
    if (current && current.pricePerPkg !== data.pricePerPkg) {
      data.lastPricePerPkg = current.pricePerPkg;
    }
  }

  const item = await prisma.item.update({
    where: { id: itemId },
    data,
  });
  res.json(item);
});

app.delete('/api/items/:id', auth, async (req, res) => {
  await prisma.item.delete({ where: { id: parseInt(req.params.id) } });
  res.json({ ok: true });
});

// ===== INVENTORY =====
app.get('/api/inventory/:store', auth, async (req, res) => {
  const rows = await prisma.storeInventory.findMany({
    where: { storeId: req.params.store },
  });
  const data = {};
  rows.forEach(r => { data[r.itemId] = { par: r.par, onHand: r.onHand }; });
  res.json(data);
});

app.put('/api/inventory/:store/:itemId', auth, async (req, res) => {
  const storeId = req.params.store;
  const itemId = parseInt(req.params.itemId);
  const row = await prisma.storeInventory.upsert({
    where: { storeId_itemId: { storeId, itemId } },
    create: { storeId, itemId, ...req.body },
    update: req.body,
  });
  res.json(row);
});

// ===== SEED =====
app.post('/api/seed', auth, async (req, res) => {
  const { items: seedItems, stores: seedStores } = req.body;

  for (const name of seedStores) {
    await prisma.store.upsert({
      where: { name },
      create: { name },
      update: {},
    });
  }

  for (const raw of seedItems) {
    const { id, par, onHand, ...data } = raw;
    await prisma.item.create({ data });
  }

  res.json({ ok: true, count: seedItems.length });
});

// ===== RESET =====
app.post('/api/reset', auth, async (req, res) => {
  await prisma.storeInventory.deleteMany();
  await prisma.item.deleteMany();
  await prisma.store.deleteMany();

  const { items: seedItems, stores: seedStores } = req.body;

  for (const name of seedStores) {
    await prisma.store.create({ data: { name } });
  }

  for (const raw of seedItems) {
    const { id, par, onHand, ...data } = raw;
    await prisma.item.create({ data });
  }

  res.json({ ok: true, count: seedItems.length });
});

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => console.log(`TIC Ordering Guide running on port ${PORT}`));
