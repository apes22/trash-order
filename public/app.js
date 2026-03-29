// ===== AUTH =====
let token = localStorage.getItem('tic-token');
let userRole = localStorage.getItem('tic-role') || 'crew';

function isManager() { return userRole === 'manager'; }

async function api(path, options = {}) {
  try {
    const res = await fetch(path, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
        ...options.headers,
      },
    });
    if (res.status === 401) {
      token = null;
      userRole = 'crew';
      localStorage.removeItem('tic-token');
      localStorage.removeItem('tic-role');
      showLogin();
      return null;
    }
    return res.json();
  } catch (err) {
    console.warn('API error:', err);
    return null;
  }
}

function updateRoleBanner() {
  const banner = document.getElementById('role-banner');
  const badge = document.getElementById('order-role-badge');
  if (token) {
    banner.style.display = '';
    banner.textContent = 'Logged in as: ' + (isManager() ? 'Manager' : 'Crew');
    if (badge) {
      badge.textContent = isManager() ? 'Manager' : 'Crew';
      badge.style.background = isManager() ? '#7c3aed' : '#6b7280';
    }
  } else {
    banner.style.display = 'none';
    if (badge) badge.textContent = '';
  }
}

function showLogin() {
  document.getElementById('login-screen').style.display = '';
  document.getElementById('dashboard-screen').style.display = 'none';
  document.getElementById('app-container').style.display = 'none';
  updateRoleBanner();
}

function showDashboard() {
  document.getElementById('login-screen').style.display = 'none';
  document.getElementById('dashboard-screen').style.display = '';
  document.getElementById('app-container').style.display = 'none';
  updateRoleBanner();
}

function hideLogin() {
  document.getElementById('login-screen').style.display = 'none';
}

async function openTool(tool) {
  if (tool === 'order') {
    document.getElementById('dashboard-screen').style.display = 'none';
    document.getElementById('app-container').style.display = '';
    document.getElementById('role-banner').style.display = 'none';
    try {
      await loadData();
      bindEvents();
      render();
    } catch (err) {
      console.warn('Load error:', err);
      document.getElementById('table-container').innerHTML =
        '<div class="empty-state"><p>Could not connect to server. Try again.</p></div>';
    }
  } else if (tool === 'schedule') {
    window.location.href = '/schedule/';
  } else if (tool === 'pricing') {
    window.location.href = '/pricing/';
  }
}

function backToDashboard() {
  document.getElementById('app-container').style.display = 'none';
  document.getElementById('dashboard-screen').style.display = '';
  updateRoleBanner();
}

async function login() {
  const pin = document.getElementById('login-pin').value;
  const errorEl = document.getElementById('login-error');
  errorEl.textContent = '';
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin }),
    });
    const data = await res.json();
    if (res.ok) {
      token = data.token;
      userRole = data.role;
      localStorage.setItem('tic-token', token);
      localStorage.setItem('tic-role', userRole);
      showDashboard();
    } else {
      errorEl.textContent = 'Wrong PIN. Try again.';
    }
  } catch {
    errorEl.textContent = 'Connection error. Try again.';
  }
}

function logout() {
  token = null;
  userRole = 'crew';
  localStorage.removeItem('tic-token');
  localStorage.removeItem('tic-role');
  showLogin();
}

// ===== STATE =====
let items = [];
let storeData = {};
let stores = [];
let currentStore = '';
let editingItemId = null;
let searchQuery = '';
let sortCol = 'item';
let sortDir = 'asc';
let collapsedCats = new Set();
let eventsBound = false;

const CATEGORY_ORDER = ['BEVERAGE', 'ICE CREAM', 'TRASH TOPPINGS', 'PAPERGOODS', 'JOB SUPPLIES', 'NOT FOR INVENTORY'];
const DEFAULT_STORES = ['Bentonville', 'Rogers'];

const COLUMNS = [
  { key: 'vendor',      label: 'Vendor',    cls: 'col-vendor' },
  { key: 'item',        label: 'Item',      cls: 'col-item' },
  { key: 'packSize',    label: 'Pack Size', cls: 'col-pack' },
  { key: 'brand',       label: 'Brand',     cls: 'col-brand' },
  { key: 'unit',        label: 'Buying Unit', cls: 'col-unit' },
  { key: 'unitsPerPack',    label: 'Units/Pack', cls: 'col-units desktop-only' },
  { key: 'pricePerPkg',     label: 'Price/Pkg',  cls: 'col-price' },
  { key: 'pricePerBuyingUnit', label: 'Price/Buy Unit', cls: 'col-perunit desktop-only' },
  { key: 'costingUnit',           label: 'Costing Unit',    cls: 'col-costunit desktop-only' },
  { key: 'costingUnitsPerPack',  label: 'Cost Units/Pack', cls: 'col-costqty desktop-only' },
  { key: 'pricePerCostingUnit',  label: 'Price/Cost Unit', cls: 'col-percost desktop-only' },
  { key: 'lastPricePerPkg', label: 'Last Price', cls: 'col-lastprice desktop-only' },
  { key: 'priceChange',     label: 'Change',     cls: 'col-pricechange desktop-only' },
  { key: 'par',              label: 'PAR',        cls: 'col-par' },
  { key: 'onHand',      label: 'On Hand',   cls: 'col-onhand' },
  { key: 'order',       label: 'Order',     cls: 'col-order' },
];

// ===== INIT =====
document.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('login-btn').addEventListener('click', login);
  document.getElementById('login-pin').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') login();
  });

  if (token) {
    showDashboard();
  } else {
    showLogin();
  }
});

// ===== DATA (API) =====
async function loadData() {
  stores = await api('/api/stores') || [];

  if (stores.length === 0) {
    await api('/api/seed', {
      method: 'POST',
      body: JSON.stringify({ items: INITIAL_DATA, stores: DEFAULT_STORES }),
    });
    stores = await api('/api/stores') || [];
  }

  if (!currentStore || !stores.includes(currentStore)) {
    currentStore = stores[0] || 'Bentonville';
  }
  updateStoreDropdown();

  items = await api('/api/items') || [];
  storeData = await api('/api/inventory/' + encodeURIComponent(currentStore)) || {};
}

async function switchStore(storeName) {
  currentStore = storeName;
  storeData = await api('/api/inventory/' + encodeURIComponent(storeName)) || {};
  render();
}

function updateStoreDropdown() {
  const select = document.getElementById('store-select');
  select.innerHTML = stores.map(s =>
    `<option value="${s}" ${s === currentStore ? 'selected' : ''}>${s}</option>`
  ).join('');
}

function getStoreVal(itemId, field) {
  const entry = storeData[itemId];
  return (entry && entry[field]) || 0;
}

function getOrder(item) {
  return Math.max(0, getStoreVal(item.id, 'par') - getStoreVal(item.id, 'onHand'));
}

// ===== SEARCH & SORT =====
function filterItems(list) {
  if (!searchQuery) return list;
  const q = searchQuery.toLowerCase();
  return list.filter(i =>
    i.item.toLowerCase().includes(q) ||
    i.vendor.toLowerCase().includes(q) ||
    i.brand.toLowerCase().includes(q) ||
    i.packSize.toLowerCase().includes(q)
  );
}

function sortItems(list) {
  const dir = sortDir === 'asc' ? 1 : -1;
  return [...list].sort((a, b) => {
    let av, bv;
    if (sortCol === 'order') { av = getOrder(a); bv = getOrder(b); }
    else if (sortCol === 'par' || sortCol === 'onHand') { av = getStoreVal(a.id, sortCol); bv = getStoreVal(b.id, sortCol); }
    else if (sortCol === 'priceChange') { av = (a.pricePerPkg||0) - (a.lastPricePerPkg||0); bv = (b.pricePerPkg||0) - (b.lastPricePerPkg||0); }
    else if (['pricePerPkg', 'lastPricePerPkg', 'unitsPerPack', 'pricePerBuyingUnit', 'costingUnitsPerPack', 'pricePerCostingUnit'].includes(sortCol)) { av = a[sortCol] || 0; bv = b[sortCol] || 0; }
    else { av = (a[sortCol] || '').toString().toLowerCase(); bv = (b[sortCol] || '').toString().toLowerCase(); }
    if (av < bv) return -1 * dir;
    if (av > bv) return 1 * dir;
    return 0;
  });
}

function toggleSort(col) {
  if (sortCol === col) { sortDir = sortDir === 'asc' ? 'desc' : 'asc'; }
  else { sortCol = col; sortDir = 'asc'; }
  render();
}

function getCategories() {
  const present = new Set(items.map(i => i.category));
  const ordered = CATEGORY_ORDER.filter(c => present.has(c));
  const extra = [...present].filter(c => !CATEGORY_ORDER.includes(c));
  return [...ordered, ...extra];
}

// ===== EVENTS =====
function bindEvents() {
  if (eventsBound) return;
  eventsBound = true;

  document.getElementById('add-item-btn').addEventListener('click', () => openModal());
  document.getElementById('logout-btn').addEventListener('click', logout);
  document.getElementById('store-select').addEventListener('change', (e) => switchStore(e.target.value));
  document.getElementById('search-input').addEventListener('input', (e) => { searchQuery = e.target.value.trim(); render(); });
  document.getElementById('print-par-btn').addEventListener('click', () => printWithMode('print-par', 'PAR Levels -- ' + currentStore));
  document.getElementById('print-order-btn').addEventListener('click', () => printWithMode('print-order', 'Suggested Order -- ' + currentStore));

  document.getElementById('reset-btn').addEventListener('click', async () => {
    if (confirm('Reset ALL data? Clears everything for all stores. Cannot be undone.')) {
      await api('/api/reset', { method: 'POST', body: JSON.stringify({ items: INITIAL_DATA, stores: DEFAULT_STORES }) });
      await loadData();
      render();
    }
  });

  document.querySelectorAll('.col-toggles input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', () => {
      document.querySelectorAll('.' + cb.dataset.col).forEach(el => { el.style.display = cb.checked ? '' : 'none'; });
    });
  });

  document.getElementById('modal-cancel').addEventListener('click', closeModal);
  document.querySelector('.modal-overlay').addEventListener('click', closeModal);
  document.getElementById('item-form').addEventListener('submit', (e) => { e.preventDefault(); saveItemFromForm(); });
  document.getElementById('modal-delete').addEventListener('click', () => { if (editingItemId) deleteItem(editingItemId, true); });
}

// ===== RENDER =====
function render() {
  const container = document.getElementById('table-container');
  document.body.classList.toggle('role-manager', isManager());
  document.body.classList.toggle('role-crew', !isManager());
  if (items.length === 0) { container.innerHTML = '<div class="empty-state"><p>Loading...</p></div>'; return; }

  let html = '';
  for (const cat of getCategories()) { const h = renderCategory(cat); if (h) html += h; }
  if (!html) { container.innerHTML = '<div class="empty-state"><p>No items match your search.</p></div>'; return; }

  container.innerHTML = html;
  attachInlineListeners();
  applyColumnToggles();
}

function toggleCategory(category) {
  collapsedCats.has(category) ? collapsedCats.delete(category) : collapsedCats.add(category);
  render();
}

function renderCategory(category) {
  const catItems = sortItems(filterItems(items.filter(i => i.category === category)));
  if (catItems.length === 0) return '';
  const cssClass = category.replace(/\s+/g, '_');
  const collapsed = collapsedCats.has(category);
  let html = `<div class="category-section cat-${cssClass}${collapsed ? ' collapsed' : ''}">`;
  html += `<div class="category-header" onclick="toggleCategory('${category}')">
    <span><span class="chevron">${collapsed ? '&#9654;' : '&#9660;'}</span> ${category} (${catItems.length})</span>
    <button class="add-to-cat no-print" onclick="event.stopPropagation(); openModal('${category}')">+ Add</button>
  </div>`;
  if (!collapsed) {
    html += '<table class="order-table"><thead><tr>';
    for (const col of COLUMNS) {
      const active = sortCol === col.key;
      html += `<th class="${col.cls} sortable${active ? ' sort-active' : ''}" onclick="event.stopPropagation(); toggleSort('${col.key}')">${col.label}${active ? (sortDir === 'asc' ? ' ▲' : ' ▼') : ''}</th>`;
    }
    html += '<th class="row-actions no-print"></th></tr></thead><tbody>';
    for (const item of catItems) html += renderRow(item);
    html += '</tbody></table>';
  }
  html += '</div>';
  return html;
}

function textCell(cls, id, field, value) {
  if (isManager()) {
    return `<td class="${cls}"><input type="text" class="inline-input inline-text" data-id="${id}" data-field="${field}" value="${esc(value)}"></td>`;
  }
  return `<td class="${cls}">${esc(value)}</td>`;
}

function renderRow(item) {
  const par = getStoreVal(item.id, 'par');
  const onHand = getStoreVal(item.id, 'onHand');
  const order = Math.max(0, par - onHand);
  const needsOrder = par > 0 && order > 0;
  let html = `<tr class="${needsOrder ? 'needs-order' : ''}" data-id="${item.id}">`;
  html += textCell('col-vendor', item.id, 'vendor', item.vendor);
  html += textCell('col-item', item.id, 'item', item.item);
  html += textCell('col-pack', item.id, 'packSize', item.packSize);
  html += textCell('col-brand', item.id, 'brand', item.brand);
  html += textCell('col-unit', item.id, 'unit', item.unit);
  // Units per pack
  if (isManager()) {
    html += `<td class="col-units desktop-only"><input type="number" class="inline-input inline-text inline-num" data-id="${item.id}" data-field="unitsPerPack" value="${item.unitsPerPack || ''}" min="0" step="1" placeholder="0"></td>`;
  } else {
    html += `<td class="col-units desktop-only">${item.unitsPerPack || '-'}</td>`;
  }

  // Price per pkg
  if (isManager()) {
    html += `<td class="col-price"><input type="number" class="inline-input inline-text inline-price" data-id="${item.id}" data-field="pricePerPkg" value="${item.pricePerPkg || ''}" min="0" step="0.01" placeholder="0.00"></td>`;
  } else {
    html += `<td class="col-price">${item.pricePerPkg ? '$' + item.pricePerPkg.toFixed(2) : ''}</td>`;
  }

  // Price per buying unit (calculated, read-only)
  const pricePerBuyingUnit = item.pricePerBuyingUnit || 0;
  html += `<td class="col-perunit desktop-only">${pricePerBuyingUnit ? '$' + pricePerBuyingUnit.toFixed(2) : '-'}</td>`;

  // Costing unit (editable)
  if (isManager()) {
    html += textCell('col-costunit desktop-only', item.id, 'costingUnit', item.costingUnit);
  } else {
    html += `<td class="col-costunit desktop-only">${esc(item.costingUnit) || '-'}</td>`;
  }

  // Costing units per pack (editable)
  if (isManager()) {
    html += `<td class="col-costqty desktop-only"><input type="number" class="inline-input inline-text inline-num" data-id="${item.id}" data-field="costingUnitsPerPack" value="${item.costingUnitsPerPack || ''}" min="0" step="1" placeholder="0"></td>`;
  } else {
    html += `<td class="col-costqty desktop-only">${item.costingUnitsPerPack || '-'}</td>`;
  }

  // Price per costing unit (calculated, read-only)
  const pricePerCostingUnit = item.pricePerCostingUnit || 0;
  html += `<td class="col-percost desktop-only">${pricePerCostingUnit ? '$' + pricePerCostingUnit.toFixed(4) : '-'}</td>`;

  // Last Price
  const lastPrice = item.lastPricePerPkg || 0;
  html += `<td class="col-lastprice desktop-only">${lastPrice ? '$' + lastPrice.toFixed(2) : '-'}</td>`;

  // Price Change
  const change = (item.pricePerPkg || 0) - lastPrice;
  let changeHtml = '-';
  let changeCls = 'col-pricechange desktop-only';
  if (lastPrice > 0 && change !== 0) {
    const sign = change > 0 ? '+' : '';
    changeHtml = sign + '$' + change.toFixed(2);
    changeCls += change > 0 ? ' price-up' : ' price-down';
  }
  html += `<td class="${changeCls}">${changeHtml}</td>`;

  // PAR -- manager can edit, crew sees read-only
  if (isManager()) {
    html += `<td class="col-par"><input type="number" class="inline-input inline-text inline-num" data-id="${item.id}" data-field="par" data-store="1" value="${par || ''}" min="0" step="1" placeholder="0"></td>`;
  } else {
    html += `<td class="col-par">${par || '-'}</td>`;
  }

  // On Hand -- always editable
  html += `<td class="col-onhand"><input type="number" class="inline-input input-onhand" data-id="${item.id}" data-field="onHand" data-store="1" value="${onHand || ''}" min="0" step="1" placeholder="0"></td>`;
  html += `<td class="col-order ${par > 0 ? (order > 0 ? 'order-positive' : 'order-zero') : 'order-zero'}">${par > 0 ? order : '-'}</td>`;

  // Delete -- manager only
  if (isManager()) {
    html += `<td class="row-actions no-print"><button class="delete-btn" onclick="deleteItem(${item.id})" title="Delete">X</button></td>`;
  } else {
    html += `<td class="row-actions no-print"></td>`;
  }
  html += '</tr>';
  return html;
}

// ===== INLINE EDITING =====
function attachInlineListeners() {
  const numericFields = new Set(['par', 'onHand', 'pricePerPkg', 'unitsPerPack', 'costingUnitsPerPack']);
  document.querySelectorAll('.inline-input').forEach(input => {
    input.addEventListener('change', (e) => {
      const id = parseInt(e.target.dataset.id);
      const field = e.target.dataset.field;
      const isStore = e.target.dataset.store === '1';
      const isNumeric = numericFields.has(field);
      const value = isNumeric ? (parseFloat(e.target.value) || 0) : e.target.value.trim();
      if (isStore) {
        if (!storeData[id]) storeData[id] = { par: 0, onHand: 0 };
        storeData[id][field] = value;
        api(`/api/inventory/${encodeURIComponent(currentStore)}/${id}`, { method: 'PUT', body: JSON.stringify({ [field]: value }) });
        render();
        const next = document.querySelector(`.inline-input[data-id="${id}"][data-field="${field}"]`);
        if (next) next.focus();
      } else {
        const item = items.find(i => i.id === id);
        if (item) {
          if (field === 'pricePerPkg' && item.pricePerPkg !== value) {
            item.lastPricePerPkg = item.pricePerPkg;
          }
          item[field] = value;
          api(`/api/items/${id}`, { method: 'PUT', body: JSON.stringify({ [field]: value }) })
            .then(updated => { if (updated) Object.assign(item, updated); render(); });
        }
      }
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault(); e.target.blur();
        const inputs = [...document.querySelectorAll(`.inline-input[data-field="${e.target.dataset.field}"]`)];
        const idx = inputs.indexOf(e.target);
        if (idx < inputs.length - 1) { inputs[idx + 1].focus(); inputs[idx + 1].select(); }
      }
    });
  });
}

// ===== MODAL =====
function openModal(category, itemId) {
  const modal = document.getElementById('item-modal');
  if (itemId) {
    editingItemId = itemId;
    document.getElementById('modal-title').textContent = 'Edit Item';
    document.getElementById('modal-delete').style.display = 'block';
    fillForm(items.find(i => i.id === itemId));
  } else {
    editingItemId = null;
    document.getElementById('modal-title').textContent = 'Add New Item';
    document.getElementById('modal-delete').style.display = 'none';
    clearForm();
    if (category) document.getElementById('f-category').value = category;
  }
  modal.classList.remove('hidden');
  document.getElementById('f-item').focus();
}
function closeModal() { document.getElementById('item-modal').classList.add('hidden'); editingItemId = null; }
function fillForm(i) {
  document.getElementById('f-category').value = i.category;
  document.getElementById('f-vendor').value = i.vendor;
  document.getElementById('f-packSize').value = i.packSize;
  document.getElementById('f-brand').value = i.brand;
  document.getElementById('f-item').value = i.item;
  document.getElementById('f-unit').value = i.unit;
  document.getElementById('f-pricePerPkg').value = i.pricePerPkg || '';
  document.getElementById('f-perOzUnit').value = i.perOzUnit || '';
  document.getElementById('f-notes').value = i.notes;
}
function clearForm() {
  document.getElementById('f-category').value = 'TRASH TOPPINGS';
  ['f-vendor','f-packSize','f-brand','f-item','f-pricePerPkg','f-perOzUnit','f-notes'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('f-unit').value = 'each';
}
async function saveItemFromForm() {
  const data = {
    category: document.getElementById('f-category').value,
    vendor: document.getElementById('f-vendor').value.trim(),
    packSize: document.getElementById('f-packSize').value.trim(),
    brand: document.getElementById('f-brand').value.trim(),
    item: document.getElementById('f-item').value.trim(),
    unit: document.getElementById('f-unit').value.trim(),
    pricePerPkg: parseFloat(document.getElementById('f-pricePerPkg').value) || 0,
    perOzUnit: parseFloat(document.getElementById('f-perOzUnit').value) || 0,
    notes: document.getElementById('f-notes').value.trim(),
    totalWeightOz: 0, perLbPint: 0,
  };
  if (editingItemId) {
    const updated = await api(`/api/items/${editingItemId}`, { method: 'PUT', body: JSON.stringify(data) });
    if (updated) { const idx = items.findIndex(i => i.id === editingItemId); if (idx >= 0) items[idx] = updated; }
  } else {
    const created = await api('/api/items', { method: 'POST', body: JSON.stringify(data) });
    if (created) items.push(created);
  }
  closeModal(); render();
}

// ===== DELETE =====
async function deleteItem(id, fromModal) {
  const item = items.find(i => i.id === id);
  if (item && confirm(`Delete "${item.item}"?`)) {
    await api(`/api/items/${id}`, { method: 'DELETE' });
    items = items.filter(i => i.id !== id);
    if (fromModal) closeModal();
    render();
  }
}

// ===== PRINT =====
function printWithMode(cls, label) {
  const saved = new Set(collapsedCats);
  if (collapsedCats.size > 0) { collapsedCats.clear(); render(); }
  document.getElementById('print-date').textContent = 'Date: ' + new Date().toLocaleDateString();
  document.getElementById('print-mode').textContent = label;
  document.body.classList.add(cls);
  window.print();
  document.body.classList.remove(cls);
  if (saved.size > 0) { collapsedCats = saved; render(); }
}

function applyColumnToggles() {
  document.querySelectorAll('.col-toggles input[type="checkbox"]').forEach(cb => {
    document.querySelectorAll('.' + cb.dataset.col).forEach(el => { el.style.display = cb.checked ? '' : 'none'; });
  });
}

function esc(str) { if (!str) return ''; const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }
