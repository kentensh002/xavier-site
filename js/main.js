/* ============================================
   XAVIER YOU-CHIRPAZ — Interactions
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // --- Navbar scroll effect ---
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY;
      if (scrollY > 60) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
      lastScroll = scrollY;
    }, { passive: true });
  }

  // --- Mobile menu toggle ---
  const toggle = document.querySelector('.navbar-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  if (toggle && mobileMenu) {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('open');
      mobileMenu.classList.toggle('open');
      document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
    });

    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        toggle.classList.remove('open');
        mobileMenu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  // --- Scroll reveal ---
  const reveals = document.querySelectorAll('.reveal, .reveal-stagger');
  if (reveals.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -40px 0px'
    });

    reveals.forEach(el => observer.observe(el));
  }

  // --- Hero image load ---
  const hero = document.querySelector('.hero');
  if (hero) {
    window.addEventListener('load', () => {
      hero.classList.add('loaded');
    });
  }

  // --- Visionneuse (clic sur une photo d'une série) ---
  const items = Array.from(document.querySelectorAll('[data-lb]'));
  if (items.length) {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.hidden = true;
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    // textes de la visionneuse selon la langue de la page (<html lang>)
    const LABELS = {
      fr: { viewer: 'Visionneuse photo', close: 'Fermer', prev: 'Photo précédente', next: 'Photo suivante' },
      en: { viewer: 'Photo viewer', close: 'Close', prev: 'Previous photo', next: 'Next photo' },
      it: { viewer: 'Visualizzatore foto', close: 'Chiudi', prev: 'Foto precedente', next: 'Foto successiva' }
    };
    const L = LABELS[(document.documentElement.lang || 'fr').slice(0, 2)] || LABELS.fr;
    box.setAttribute('aria-label', L.viewer);
    box.innerHTML =
      '<button class="lb-btn lb-close" type="button" aria-label="' + L.close + '">&times;</button>' +
      '<button class="lb-btn lb-prev" type="button" aria-label="' + L.prev + '">&#8249;</button>' +
      '<figure class="lb-stage"><img alt=""><figcaption class="lb-caption"></figcaption></figure>' +
      '<button class="lb-btn lb-next" type="button" aria-label="' + L.next + '">&#8250;</button>';
    document.body.appendChild(box);

    const img = box.querySelector('img');
    const caption = box.querySelector('.lb-caption');
    const btnClose = box.querySelector('.lb-close');
    const btnPrev = box.querySelector('.lb-prev');
    const btnNext = box.querySelector('.lb-next');
    const buttons = [btnClose, btnPrev, btnNext];
    const n = items.length;
    let idx = 0;
    let lastFocus = null;
    let touchX = null;

    if (n < 2) { btnPrev.hidden = true; btnNext.hidden = true; }

    const show = (i) => {
      idx = (i + n) % n;
      const a = items[idx];
      const thumb = a.querySelector('img');
      // image déjà chargée tout de suite, puis version haute définition
      img.src = thumb.currentSrc || thumb.src;
      img.alt = thumb.alt;
      caption.textContent = a.dataset.caption || '';
      const big = new Image();
      big.onload = () => { if (items[idx] === a) img.src = big.src; };
      big.src = a.href;
      if (n > 1) {
        new Image().src = items[(idx + 1) % n].href;
        new Image().src = items[(idx - 1 + n) % n].href;
      }
    };

    const open = (i) => {
      lastFocus = document.activeElement;
      show(i);
      box.hidden = false;
      document.body.style.overflow = 'hidden';
      btnClose.focus();
    };

    const close = () => {
      box.hidden = true;
      document.body.style.overflow = '';
      img.removeAttribute('src');
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    };

    items.forEach((a, i) => {
      a.addEventListener('click', (e) => { e.preventDefault(); open(i); });
    });

    btnClose.addEventListener('click', close);
    btnPrev.addEventListener('click', () => show(idx - 1));
    btnNext.addEventListener('click', () => show(idx + 1));
    box.addEventListener('click', (e) => {
      if (e.target === box || e.target.classList.contains('lb-stage')) close();
    });

    document.addEventListener('keydown', (e) => {
      if (box.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(idx - 1);
      else if (e.key === 'ArrowRight') show(idx + 1);
      else if (e.key === 'Tab') {
        const vis = buttons.filter(b => !b.hidden);
        const first = vis[0], last = vis[vis.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });

    box.addEventListener('touchstart', (e) => { touchX = e.changedTouches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', (e) => {
      if (touchX === null) return;
      const dx = e.changedTouches[0].clientX - touchX;
      touchX = null;
      if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
    }, { passive: true });
  }

  // --- Active nav link ---
  const currentPath = window.location.pathname.replace(/\/$/, '') || '/';
  document.querySelectorAll('.navbar-links a, .mobile-menu a').forEach(link => {
    if (link.hasAttribute('hreflang')) return; // sélecteur de langue
    const href = link.getAttribute('href').replace(/\/$/, '') || '/';
    const linkPath = href.startsWith('/') ? href : '/' + href;
    if (linkPath === currentPath || (currentPath.endsWith(href) && href !== '/')) {
      link.classList.add('active');
    }
  });

});
