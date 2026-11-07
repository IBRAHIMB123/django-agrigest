document.addEventListener('DOMContentLoaded', function () {
  const shell = document.querySelector('.shell');
  const sidebar = document.querySelector('.sidebar');
  const menuToggle = document.querySelector('[data-mobile-menu]');
  const closeMenu = document.querySelector('[data-close-menu]');
  const search = document.querySelector('[data-global-search]');
  const shortcutLabel = document.querySelector('[data-search-shortcut]');
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const themeLabel = document.querySelector('[data-theme-label]');
  const themeIcon = document.querySelector('[data-theme-icon]');
  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    const dark = theme === 'dark';
    themeToggle?.setAttribute('aria-pressed', String(dark));
    themeToggle?.setAttribute('aria-label', dark ? 'Activer le theme clair' : 'Activer le theme sombre');
    if (themeLabel) themeLabel.textContent = dark ? 'Clair' : 'Sombre';
    if (themeIcon) themeIcon.textContent = dark ? '☼' : '◐';
  };
  applyTheme(document.documentElement.dataset.theme || 'light');
  themeToggle?.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem('agrigest-theme', next); } catch (_) {}
  });

  const isMobile = () => window.matchMedia('(max-width: 900px)').matches;
  const setMenuOpen = (open) => {
    if (!shell || !menuToggle) return;
    shell.classList.toggle('sidebar-open', open);
    menuToggle.setAttribute('aria-expanded', String(open));
    if (sidebar) sidebar.inert = isMobile() && !open;
  };

  setMenuOpen(false);
  if (menuToggle) menuToggle.addEventListener('click', () => setMenuOpen(!shell.classList.contains('sidebar-open')));
  if (closeMenu) closeMenu.addEventListener('click', () => { setMenuOpen(false); menuToggle?.focus(); });
  if (sidebar) {
    sidebar.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => { if (isMobile()) setMenuOpen(false); });
    });
  }
  window.addEventListener('resize', () => {
    if (shell) setMenuOpen(isMobile() && shell.classList.contains('sidebar-open'));
  });

  if (shortcutLabel && /Mac|iPhone|iPad/.test(navigator.platform)) shortcutLabel.textContent = '⌘ K';
  document.addEventListener('keydown', (event) => {
    const isTyping = event.target.matches('input, textarea, select, [contenteditable="true"]');
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      search?.focus();
    } else if (event.key === '/' && !isTyping) {
      event.preventDefault();
      search?.focus();
    } else if (event.key === 'Escape') {
      if (shell?.classList.contains('sidebar-open')) setMenuOpen(false);
      if (document.activeElement === search) search.blur();
    }
  });

  document.querySelectorAll('.message').forEach((message) => {
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'message-close';
    close.setAttribute('aria-label', 'Fermer le message');
    close.textContent = '×';
    close.addEventListener('click', () => message.remove());
    message.append(close);
  });

  document.querySelectorAll('[data-view-set]').forEach((group) => {
    const key = `agrigest-view-${group.dataset.viewSet}`;
    const setView = (view) => {
      group.querySelectorAll('[data-view-target]').forEach((button) => {
        const active = button.dataset.viewTarget === view;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
      });
      document.querySelectorAll(`[data-view-panel]`).forEach((panel) => {
        if (panel.closest('.page-card') !== group.closest('.page-card')) return;
        panel.hidden = panel.dataset.viewPanel !== view;
      });
      try { localStorage.setItem(key, view); } catch (_) {}
    };
    let initial = 'cards';
    try { initial = localStorage.getItem(key) || initial; } catch (_) {}
    setView(initial);
    group.querySelectorAll('[data-view-target]').forEach((button) => button.addEventListener('click', () => setView(button.dataset.viewTarget)));
  });

  const confirmDialog = document.querySelector('[data-confirm-dialog]');
  let pendingForm = null;
  document.querySelectorAll('form[data-confirm]').forEach((form) => form.addEventListener('submit', (event) => {
    if (form.dataset.confirmed === 'true') { form.dataset.confirmed = 'false'; return; }
    if (!confirmDialog?.showModal) return;
    event.preventDefault();
    pendingForm = form;
    const copy = confirmDialog.querySelector('[data-confirm-copy]');
    if (copy) copy.textContent = form.dataset.confirm || 'Cette action ne peut pas etre annulee.';
    confirmDialog.showModal();
  }));
  confirmDialog?.querySelector('[data-confirm-accept]')?.addEventListener('click', () => {
    if (pendingForm) { pendingForm.dataset.confirmed = 'true'; confirmDialog.close(); pendingForm.requestSubmit(); pendingForm = null; }
  });

  document.querySelectorAll('[data-password-toggle]').forEach((button) => button.addEventListener('click', () => {
    const input = document.getElementById(button.dataset.passwordToggle);
    if (!input) return;
    const visible = input.type === 'password';
    input.type = visible ? 'text' : 'password';
    button.textContent = visible ? 'Masquer' : 'Afficher';
    button.setAttribute('aria-label', visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe');
  }));
});
