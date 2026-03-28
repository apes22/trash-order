const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// Inline seed data (same as public/data.js INITIAL_DATA)
const STORES = ['Bentonville', 'Rogers'];

async function main() {
  console.log('Seeding stores...');
  for (const name of STORES) {
    await prisma.store.upsert({
      where: { name },
      create: { name },
      update: {},
    });
  }
  console.log(`  Created ${STORES.length} stores`);

  const existing = await prisma.item.count();
  if (existing > 0) {
    console.log(`  ${existing} items already exist, skipping item seed.`);
    return;
  }

  // Load INITIAL_DATA from the frontend data file
  // We eval it since it's a plain JS const declaration
  const fs = require('fs');
  const dataFile = fs.readFileSync(__dirname + '/public/data.js', 'utf-8');
  const match = dataFile.match(/const INITIAL_DATA = (\[[\s\S]*?\]);/);
  if (!match) {
    console.error('Could not parse INITIAL_DATA from public/data.js');
    process.exit(1);
  }
  const INITIAL_DATA = eval(match[1]);

  console.log(`Seeding ${INITIAL_DATA.length} items...`);
  for (const raw of INITIAL_DATA) {
    const { id, par, onHand, ...data } = raw;
    await prisma.item.create({ data });
  }
  console.log('  Done!');
}

main()
  .catch(e => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
