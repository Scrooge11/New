/* JEMCO Contracting & Electrical Services — site behaviour (no dependencies) */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  // Mobile navigation toggle
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (header && toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('is-open')) {
        header.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  // Current year in the footer
  var yearEls = document.querySelectorAll('[data-year]');
  for (var i = 0; i < yearEls.length; i++) yearEls[i].textContent = String(new Date().getFullYear());

  // Quote form: posts to the form's action (Netlify Forms by default) and shows the result inline
  var form = document.querySelector('form.quote-form');
  if (form) {
    var status = form.querySelector('.form-status');
    var button = form.querySelector('button[type="submit"]');
    var fallback = form.getAttribute('data-fallback') || 'Please call or email us instead.';

    function show(kind, message) {
      if (!status) return;
      status.className = 'form-status ' + (kind === 'ok' ? 'is-ok' : 'is-err');
      status.textContent = message;
      status.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var honeypot = form.querySelector('input[name="bot-field"]');
      if (honeypot && honeypot.value) return; // silently drop bots
      if (!form.checkValidity()) { form.reportValidity(); return; }

      var data = new FormData(form);
      var body = new URLSearchParams();
      data.forEach(function (value, key) { body.append(key, value); });

      if (button) { button.disabled = true; button.dataset.label = button.textContent; button.textContent = 'Sending…'; }

      fetch(form.getAttribute('action') || window.location.pathname, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString()
      }).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        form.reset();
        show('ok', 'Thanks. Your request is in. We reply within one business day, usually sooner.');
      }).catch(function () {
        show('err', 'The form could not be sent from this page. ' + fallback);
      }).finally(function () {
        if (button) { button.disabled = false; button.textContent = button.dataset.label || 'Send request'; }
      });
    });
  }

  // Header firms up after a short scroll
  if (header) {
    var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 12); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Reveal sections and cards as they enter the viewport (skipped without IntersectionObserver)
  if ('IntersectionObserver' in window) {
    var targets = document.querySelectorAll('.section-head, .service-card, .why-item, .process li, .work-tile, .faq-item, .price-box, .hours-card');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    for (var k = 0; k < targets.length; k++) {
      targets[k].classList.add('rv');
      targets[k].style.transitionDelay = ((k % 3) * 60) + 'ms';
      io.observe(targets[k]);
    }
    // Safety net: anything the reader has already scrolled to or past is shown, even after a jump
    var pending = false;
    var sweep = function () {
      pending = false;
      var left = document.querySelectorAll('.rv:not(.in)');
      for (var m = 0; m < left.length; m++) {
        if (left[m].getBoundingClientRect().top < window.innerHeight) left[m].classList.add('in');
      }
    };
    window.addEventListener('scroll', function () { if (!pending) { pending = true; window.requestAnimationFrame(sweep); } }, { passive: true });
    window.addEventListener('beforeprint', function () {
      var all = document.querySelectorAll('.rv');
      for (var n = 0; n < all.length; n++) all[n].classList.add('in');
    });
  }
})();
