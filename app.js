// ===== STATE =====
let items = [];
let editingItemId = null;
let searchQuery = '';
let sortCol = 'item';
let sortDir = 'asc'; // 'asc' | 'desc'
let collapsedCats = new Set();

const CATEGORY_ORDER = ['BEVERAGE', 'ICE CREAM', 'TRASH TOPPINGS', 'PAPERGOODS', 'JOB SUPPLIES', 'NOT FOR INVENTORY'];

const COLUMNS = [
  { key: 'vendor',      label: 'Vendor',    cls: 'col-vendor',  type: 'text' },
  { key: 'item',        label: 'Item',      cls: 'col-item',    type: 'text' },
  { key: 'packSize',    label: 'Pack Size', cls: 'col-pack',    type: 'text' },
  { key: 'brand',       label: 'Brand',     cls: 'col-brand',   type: 'text' },
  { key: 'unit',        label: 'Unit',      cls: 'col-unit',    type: 'text' },
  { key: 'pricePerPkg', label: 'Price/Pkg', cls: 'col-price',   type: 'money' },
  { key: 'par',         label: 'PAR',       cls: 'col-par',     type: 'par' },
  { key: 'onHand',      label: 'On Hand',   cls: 'col-onhand',  type: 'onhand' },
  { key: 'order',       label: 'Order',     cls: 'col-order',   type: 'calc' },
];

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  loadData();
  bindEvents();
  render();
});

// ===== DATA =====
function loadData() {
  const saved = localStorage.getItem('tic-order-guide');
  if (saved) {
    items = JSON.parse(saved);
  } else {
    items = JSON.parse(JSON.stringify(INITIAL_DATA));
  }
}

function saveData() {
  localStorage.setItem('tic-order-guide', JSON.stringify(items));
}

function getNextId() {
  return items.length ? Math.max(...items.map(i => i.id)) + 1 : 1;
}

function getCategories() {
  const present = new Set(items.map(i => i.category));
  const ordered = CATEGORY_ORDER.filter(c => present.has(c));
  const extra = [...present].filter(c => !CATEGORY_ORDER.includes(c));
  return [...ordered, ...extra];
}

function getOrder(item) {
  return Math.max(0, (item.par || 0) - (item.onHand || 0));
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
    if (sortCol === 'order') {
      av = getOrder(a);
      bv = getOrder(b);
    } else if (sortCol === 'pricePerPkg' || sortCol === 'par' || sortCol === 'onHand') {
      av = a[sortCol] || 0;
      bv = b[sortCol] || 0;
    } else {
      av = (a[sortCol] || '').toString().toLowerCase();
      bv = (b[sortCol] || '').toString().toLowerCase();
    }
    if (av < bv) return -1 * dir;
    if (av > bv) return 1 * dir;
    return 0;
  });
}

function toggleSort(col) {
  if (sortCol === col) {
    sortDir = sortDir === 'asc' ? 'desc' : 'asc';
  } else {
    sortCol = col;
    sortDir = 'asc';
  }
  render();
}

// ===== EVENTS =====
function bindEvents() {
  document.getElementById('add-item-btn').addEventListener('click', () => openModal());

  // Search
  document.getElementById('search-input').addEventListener('input', (e) => {
    searchQuery = e.target.value.trim();
    render();
  });

  // Print PAR sheet
  document.getElementById('print-par-btn').addEventListener('click', () => {
    printWithMode('print-par', 'PAR Levels');
  });

  // Print Order sheet
  document.getElementById('print-order-btn').addEventListener('click', () => {
    printWithMode('print-order', 'Suggested Order');
  });

  // Reset
  document.getElementById('reset-btn').addEventListener('click', () => {
    if (confirm('Reset all data to defaults? This will clear all PAR levels, inventory counts, and any items you added.')) {
      localStorage.removeItem('tic-order-guide');
      items = JSON.parse(JSON.stringify(INITIAL_DATA));
      render();
    }
  });

  // Column toggles
  document.querySelectorAll('.col-toggles input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', () => {
      const col = cb.dataset.col;
      document.querySelectorAll('.' + col).forEach(el => {
        el.style.display = cb.checked ? '' : 'none';
      });
    });
  });

  // Modal
  document.getElementById('modal-cancel').addEventListener('click', closeModal);
  document.querySelector('.modal-overlay').addEventListener('click', closeModal);
  document.getElementById('item-form').addEventListener('submit', (e) => {
    e.preventDefault();
    saveItemFromForm();
  });
  document.getElementById('modal-delete').addEventListener('click', () => {
    if (editingItemId && confirm('Delete this item?')) {
      items = items.filter(i => i.id !== editingItemId);
      saveData();
      closeModal();
      render();
    }
  });
}

// ===== RENDER =====
function render() {
  const container = document.getElementById('table-container');
  const categories = getCategories();

  if (items.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>No items yet. Click "+ Add Item" to get started.</p></div>';
    return;
  }

  let html = '';
  for (const cat of categories) {
    const catHtml = renderCategory(cat);
    if (catHtml) html += catHtml;
  }

  if (!html) {
    container.innerHTML = '<div class="empty-state"><p>No items match your search.</p></div>';
    return;
  }

  container.innerHTML = html;
  attachInlineListeners();
  applyColumnToggles();
}

function toggleCategory(category) {
  if (collapsedCats.has(category)) {
    collapsedCats.delete(category);
  } else {
    collapsedCats.add(category);
  }
  render();
}

function renderCategory(category) {
  const catItems = sortItems(filterItems(items.filter(i => i.category === category)));
  if (catItems.length === 0) return '';

  const cssClass = category.replace(/\s+/g, '_');
  const collapsed = collapsedCats.has(category);
  const chevron = collapsed ? '&#9654;' : '&#9660;';

  let html = `<div class="category-section cat-${cssClass}${collapsed ? ' collapsed' : ''}">`;
  html += `<div class="category-header" onclick="toggleCategory('${category}')">
    <span><span class="chevron">${chevron}</span> ${category} (${catItems.length})</span>
    <button class="add-to-cat no-print" onclick="event.stopPropagation(); openModal('${category}')">+ Add</button>
  </div>`;

  if (!collapsed) {
    html += '<table class="order-table"><thead><tr>';
    for (const col of COLUMNS) {
      const active = sortCol === col.key;
      const arrow = active ? (sortDir === 'asc' ? ' ▲' : ' ▼') : '';
      html += `<th class="${col.cls} sortable${active ? ' sort-active' : ''}" onclick="event.stopPropagation(); toggleSort('${col.key}')">${col.label}${arrow}</th>`;
    }
    html += '<th class="row-actions no-print"></th>';
    html += '</tr></thead><tbody>';

    for (const item of catItems) {
      html += renderRow(item);
    }

    html += '</tbody></table>';
  }

  html += '</div>';
  return html;
}

function textCell(cls, id, field, value) {
  return `<td class="${cls}"><input type="text" class="inline-input inline-text" data-id="${id}" data-field="${field}" value="${esc(value)}"></td>`;
}

function renderRow(item) {
  const suggestedOrder = getOrder(item);
  const needsOrder = item.par > 0 && suggestedOrder > 0;

  let html = `<tr class="${needsOrder ? 'needs-order' : ''}" data-id="${item.id}">`;
  html += textCell('col-vendor', item.id, 'vendor', item.vendor);
  html += textCell('col-item', item.id, 'item', item.item);
  html += textCell('col-pack', item.id, 'packSize', item.packSize);
  html += textCell('col-brand', item.id, 'brand', item.brand);
  html += textCell('col-unit', item.id, 'unit', item.unit);
  html += `<td class="col-price"><input type="number" class="inline-input inline-text inline-price" data-id="${item.id}" data-field="pricePerPkg" value="${item.pricePerPkg || ''}" min="0" step="0.01" placeholder="0.00"></td>`;

  // PAR
  html += `<td class="col-par"><input type="number" class="inline-input input-par" data-id="${item.id}" data-field="par" value="${item.par || ''}" min="0" step="1" placeholder="0"></td>`;

  // On Hand
  html += `<td class="col-onhand"><input type="number" class="inline-input input-onhand" data-id="${item.id}" data-field="onHand" value="${item.onHand || ''}" min="0" step="1" placeholder="0"></td>`;

  // Suggested Order
  if (item.par > 0) {
    html += `<td class="col-order ${suggestedOrder > 0 ? 'order-positive' : 'order-zero'}">${suggestedOrder}</td>`;
  } else {
    html += `<td class="col-order order-zero">-</td>`;
  }

  html += `<td class="row-actions no-print">
    <button class="delete-btn" onclick="deleteItem(${item.id})" title="Delete">X</button>
  </td>`;
  html += '</tr>';
  return html;
}

// ===== INLINE EDITING =====
function attachInlineListeners() {
  const numericFields = new Set(['par', 'onHand', 'pricePerPkg', 'perOzUnit']);

  document.querySelectorAll('.inline-input').forEach(input => {
    input.addEventListener('change', (e) => {
      const id = parseInt(e.target.dataset.id);
      const field = e.target.dataset.field;
      const isNumeric = numericFields.has(field);
      const value = isNumeric ? (parseFloat(e.target.value) || 0) : e.target.value.trim();
      const item = items.find(i => i.id === id);
      if (item) {
        item[field] = value;
        saveData();
        if (field === 'par' || field === 'onHand') {
          const focusField = e.target.dataset.field;
          render();
          const nextInput = document.querySelector(`.inline-input[data-id="${id}"][data-field="${focusField}"]`);
          if (nextInput) nextInput.focus();
        }
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        e.target.blur();
        const field = e.target.dataset.field;
        const sameFieldInputs = [...document.querySelectorAll(`.inline-input[data-field="${field}"]`)];
        const idx = sameFieldInputs.indexOf(e.target);
        if (idx < sameFieldInputs.length - 1) {
          sameFieldInputs[idx + 1].focus();
          sameFieldInputs[idx + 1].select();
        }
      }
    });
  });
}

// ===== MODAL =====
function openModal(category, itemId) {
  const modal = document.getElementById('item-modal');
  const title = document.getElementById('modal-title');
  const deleteBtn = document.getElementById('modal-delete');

  if (itemId) {
    editingItemId = itemId;
    const item = items.find(i => i.id === itemId);
    title.textContent = 'Edit Item';
    deleteBtn.style.display = 'block';
    fillForm(item);
  } else {
    editingItemId = null;
    title.textContent = 'Add New Item';
    deleteBtn.style.display = 'none';
    clearForm();
    if (category) {
      document.getElementById('f-category').value = category;
    }
  }

  modal.classList.remove('hidden');
  document.getElementById('f-item').focus();
}

function closeModal() {
  document.getElementById('item-modal').classList.add('hidden');
  editingItemId = null;
}

function fillForm(item) {
  document.getElementById('f-category').value = item.category;
  document.getElementById('f-vendor').value = item.vendor;
  document.getElementById('f-packSize').value = item.packSize;
  document.getElementById('f-brand').value = item.brand;
  document.getElementById('f-item').value = item.item;
  document.getElementById('f-unit').value = item.unit;
  document.getElementById('f-pricePerPkg').value = item.pricePerPkg || '';
  document.getElementById('f-perOzUnit').value = item.perOzUnit || '';
  document.getElementById('f-notes').value = item.notes;
}

function clearForm() {
  document.getElementById('f-category').value = 'TRASH TOPPINGS';
  document.getElementById('f-vendor').value = '';
  document.getElementById('f-packSize').value = '';
  document.getElementById('f-brand').value = '';
  document.getElementById('f-item').value = '';
  document.getElementById('f-unit').value = 'each';
  document.getElementById('f-pricePerPkg').value = '';
  document.getElementById('f-perOzUnit').value = '';
  document.getElementById('f-notes').value = '';
}

function saveItemFromForm() {
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
  };

  if (editingItemId) {
    const item = items.find(i => i.id === editingItemId);
    Object.assign(item, data);
  } else {
    items.push({
      id: getNextId(),
      ...data,
      totalWeightOz: 0,
      perLbPint: 0,
      par: 0,
      onHand: 0,
    });
  }

  saveData();
  closeModal();
  render();
}

// ===== DELETE =====
function deleteItem(id) {
  const item = items.find(i => i.id === id);
  if (item && confirm(`Delete "${item.item}"?`)) {
    items = items.filter(i => i.id !== id);
    saveData();
    render();
  }
}

// ===== PRINT =====
function printWithMode(cls, label) {
  // Expand all categories for print, restore after
  const savedCollapsed = new Set(collapsedCats);
  if (collapsedCats.size > 0) {
    collapsedCats.clear();
    render();
  }
  document.getElementById('print-date').textContent = 'Date: ' + new Date().toLocaleDateString();
  document.getElementById('print-mode').textContent = label;
  document.body.classList.add(cls);
  window.print();
  document.body.classList.remove(cls);
  // Restore collapsed state
  if (savedCollapsed.size > 0) {
    collapsedCats = savedCollapsed;
    render();
  }
}

// ===== COLUMN TOGGLES =====
function applyColumnToggles() {
  document.querySelectorAll('.col-toggles input[type="checkbox"]').forEach(cb => {
    const col = cb.dataset.col;
    document.querySelectorAll('.' + col).forEach(el => {
      el.style.display = cb.checked ? '' : 'none';
    });
  });
}

// ===== UTIL =====
function esc(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
