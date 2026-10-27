import {
  docsHash,
  escapeHtml,
  parseRoute,
  renderMarkdown,
  splitDocument,
  uniqueIcons,
} from './reader.js';

const DOCS = [
  ['readme', 'README', 'README.md'],
  ['app-specs', 'APP SPECS', 'docs/APP-SPECS.md'],
  ['basic-specs', 'BASIC SPECS', 'docs/BASIC-SPECS.md'],
  ['release-notes', 'RELEASE NOTES', 'RELEASE-NOTES.md'],
];

const ICONS = {
  book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v18H6.5A2.5 2.5 0 0 1 4 18.5v-13Z"/><path d="M8 8h8M8 12h8"/>',
  dot: '<circle cx="12" cy="12" r="3"/>',
  play: '<path d="m9 7 8 5-8 5Z"/>',
  install: '<path d="M12 3v12m0 0 4-4m-4 4-4-4M4 21h16"/>',
  sparkle: '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/>',
  bookmark: '<path d="M6 3h12v18l-6-4-6 4V3Z"/>',
  sync: '<path d="M4 9a8 8 0 0 1 14-3l2 2M20 5v5h-5M20 15a8 8 0 0 1-14 3l-2-2M4 19v-5h5"/>',
  shield: '<path d="M12 3 20 6v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3Z"/>',
  sliders: '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
  server: '<rect x="4" y="4" width="16" height="6" rx="1"/><rect x="4" y="14" width="16" height="6" rx="1"/><path d="M8 7h.01M8 17h.01"/>',
  pages: '<path d="M6 3h9l4 4v14H6V3Z"/><path d="M15 3v5h5M9 12h6M9 16h6"/>',
  home: '<path d="m3 11 9-8 9 8v10H3V11Z"/><path d="M9 21v-6h6v6"/>',
  flask: '<path d="M9 3h6M10 3v6L5 19a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3L14 9V3"/><path d="M8 15h8"/>',
  pen: '<path d="m4 20 4-1 11-11-3-3L5 16l-1 4Z"/>',
  scale: '<path d="M12 3v18M5 7h14M7 7l-3 6h6L7 7Zm10 0-3 6h6l-3-6Z"/>',
  layers: '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/>',
  terminal: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3M13 15h4"/>',
  plug: '<path d="M9 3v5M15 3v5M7 8h10v3a5 5 0 0 1-10 0V8ZM12 16v5"/>',
  tree: '<path d="M5 4v16M5 8h6M5 16h6M11 5v6M11 13v6"/>',
  gamepad: '<rect x="3" y="8" width="18" height="9" rx="4"/><path d="M8 10v4M6 12h4M16 11h.01M18 13h.01"/>',
};

const state = { docs: [], byslug: {}, current: null };

const elements = {
  home: document.querySelector('#home'),
  reader: document.querySelector('#reader'),
  tabs: document.querySelector('#reader-tabs'),
  sections: document.querySelector('#reader-sections'),
  title: document.querySelector('#reader-title'),
  sectionTitle: document.querySelector('#reader-section-title'),
  body: document.querySelector('#reader-body'),
  tooltip: document.querySelector('#tooltip'),
};

function icon(name, size = 16) {
  const path = ICONS[name] ?? ICONS.dot;
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${path}</svg>`;
}

async function loadDocs() {
  state.docs = await Promise.all(DOCS.map(async ([slug, title, file]) => {
    const response = await fetch(file);
    return splitDocument({ slug, title, markdown: await response.text() });
  }));
  for (const doc of state.docs) state.byslug[doc.slug] = doc;
}

function showHome() {
  elements.home.hidden = false;
  elements.reader.hidden = true;
  if (location.hash) history.replaceState(null, '', location.pathname);
}

function openDoc(slug, section = null) {
  const doc = state.byslug[slug] ?? state.byslug.readme;
  state.current = doc;
  elements.home.hidden = true;
  elements.reader.hidden = false;
  elements.title.textContent = doc.title;
  elements.tabs.innerHTML = '';
  for (const item of state.docs) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `reader-tab${item.slug === doc.slug ? ' active' : ''}`;
    button.textContent = item.title;
    button.addEventListener('click', () => openDoc(item.slug));
    elements.tabs.append(button);
  }
  const pages = doc.pages;
  const icons = uniqueIcons(pages.map((page) => page.title));
  elements.sections.innerHTML = '';
  pages.forEach((page, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'reader-section';
    button.dataset.tip = page.title;
    button.setAttribute('aria-label', page.title);
    button.innerHTML = icon(icons[index]);
    button.addEventListener('click', () => {
      history.pushState(null, '', docsHash(doc.slug, page.slug));
      openDoc(doc.slug, page.slug);
    });
    elements.sections.append(button);
  });
  const active = pages.find((page) => page.slug === section) ?? pages[0];
  for (const [index, button] of [...elements.sections.children].entries()) {
    button.classList.toggle('active', pages[index].slug === active.slug);
  }
  elements.sectionTitle.textContent = active.title;
  elements.body.innerHTML = renderMarkdown(active.markdown);
  document.title = `${doc.title} — Basic Specs`;
}

function route() {
  const parsed = parseRoute(location.hash);
  if (parsed.view === 'docs') openDoc(parsed.doc, parsed.section);
  else showHome();
}

function tooltipFor(target) {
  const text = target.dataset.tip;
  if (!text) return;
  elements.tooltip.textContent = text;
  elements.tooltip.hidden = false;
  elements.tooltip.toggleAttribute('data-wide', target.hasAttribute('data-tip-wide'));
  const box = target.getBoundingClientRect();
  const width = elements.tooltip.offsetWidth;
  const left = Math.min(Math.max(8, box.left + box.width / 2 - width / 2), innerWidth - width - 8);
  elements.tooltip.style.left = `${left}px`;
  elements.tooltip.style.top = `${Math.max(8, box.top - elements.tooltip.offsetHeight - 10)}px`;
  elements.tooltip.style.setProperty('--arrow', `${box.left + box.width / 2 - left}px`);
}

document.addEventListener('mouseover', (event) => {
  const target = event.target.closest?.('[data-tip]');
  if (target) tooltipFor(target);
});
document.addEventListener('mouseout', (event) => {
  if (event.target.closest?.('[data-tip]')) elements.tooltip.hidden = true;
});
document.addEventListener('focusin', (event) => {
  const target = event.target.closest?.('[data-tip]');
  if (target) tooltipFor(target);
});
document.addEventListener('focusout', () => { elements.tooltip.hidden = true; });

document.querySelector('#readme').addEventListener('click', () => {
  location.hash = docsHash('readme');
});
document.querySelector('#reader-close').addEventListener('click', () => {
  location.hash = '';
});
document.querySelector('#theme').addEventListener('click', () => {
  document.documentElement.style.colorScheme =
    document.documentElement.style.colorScheme === 'dark' ? 'light' : 'dark';
});
document.querySelector('#zoom').addEventListener('click', () => {
  document.body.classList.toggle('zoomed');
});
window.addEventListener('hashchange', route);
window.addEventListener('popstate', route);

await loadDocs();
route();
