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

  // --- Active nav link ---
  const currentPath = window.location.pathname.replace(/\/$/, '') || '/';
  document.querySelectorAll('.navbar-links a, .mobile-menu a').forEach(link => {
    const href = link.getAttribute('href').replace(/\/$/, '') || '/';
    const linkPath = href.startsWith('/') ? href : '/' + href;
    if (linkPath === currentPath || (currentPath.endsWith(href) && href !== '/')) {
      link.classList.add('active');
    }
  });

});
