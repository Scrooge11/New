/* JEMCO Contracting & Electrical Services — site behaviour (no dependencies) */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  // Mobile menu: opens as a sheet under the header, closes on Escape, on a tap outside, or when the window widens
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  var setNav = function (open) {
    header.classList.toggle('is-open', open);
    document.documentElement.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Menu');
  };
  if (header && toggle) {
    toggle.addEventListener('click', function () { setNav(!header.classList.contains('is-open')); });
    document.addEventListener('click', function (e) {
      if (header.classList.contains('is-open') && !e.target.closest('.site-nav, .nav-toggle')) setNav(false);
    });
    if (window.matchMedia) {
      var wide = window.matchMedia('(min-width: 1001px)');
      var onWide = function () { if (wide.matches) setNav(false); };
      if (wide.addEventListener) wide.addEventListener('change', onWide);
    }
  }

  // Services menu: the button beside "Services" shows and hides the list (a mouse can also hover)
  var menuItem = document.querySelector('.has-menu');
  var menuBtn = menuItem && menuItem.querySelector('.submenu-toggle');
  var setMenu = function (open) {
    menuItem.classList.toggle('is-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', open ? 'Hide the list of services' : 'Show the list of services');
  };
  if (menuBtn) {
    menuBtn.addEventListener('click', function () { setMenu(!menuItem.classList.contains('is-open')); });
    document.addEventListener('click', function (e) {
      if (menuItem.classList.contains('is-open') && !menuItem.contains(e.target)) setMenu(false);
    });
    menuItem.addEventListener('focusout', function (e) {
      if (e.relatedTarget && !menuItem.contains(e.relatedTarget)) setMenu(false);
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (menuBtn && menuItem.classList.contains('is-open')) { setMenu(false); menuBtn.focus(); }
    else if (header && toggle && header.classList.contains('is-open')) { setNav(false); toggle.focus(); }
  });

  // Theme button. The choice is stored, and js/theme-init.js applies it before the next page paints.
  var themeBtn = document.querySelector('.theme-toggle');
  if (themeBtn) {
    var root = document.documentElement;
    var themeText = themeBtn.querySelector('.theme-toggle-text');
    var systemDark = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
    var currentTheme = function () {
      return root.getAttribute('data-theme') || (systemDark && systemDark.matches ? 'dark' : 'light');
    };
    var describe = function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      themeBtn.setAttribute('aria-label', 'Switch to ' + next + ' theme');
      if (themeText) themeText.textContent = next === 'dark' ? 'Dark theme' : 'Light theme';
    };
    themeBtn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      var apply = function () { root.setAttribute('data-theme', next); describe(); };
      var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      // Cross-fade between the themes where the browser can; switch at once where it cannot.
      if (document.startViewTransition && !calm) document.startViewTransition(apply); else apply();
      try { localStorage.setItem('jemco-theme', next); } catch (e) { /* choice lasts for this page only */ }
    });
    if (systemDark && systemDark.addEventListener) systemDark.addEventListener('change', describe);
    describe();
  }

  // Current year in the footer
  var yearEls = document.querySelectorAll('[data-year]');
  for (var i = 0; i < yearEls.length; i++) yearEls[i].textContent = String(new Date().getFullYear());

  // Quote form. Without JavaScript the browser checks the required fields itself, submits the
  // form and lands on thanks.html. With it, problems are explained under each field, the request
  // is sent in the background and the confirmation replaces the form on the same page.
  var form = document.querySelector('form.quote-form');
  if (form) {
    var status = form.querySelector('.form-status');
    var button = form.querySelector('button[type="submit"]');
    var done = form.querySelector('.form-done');
    var fallback = form.getAttribute('data-fallback') || 'Please call or email us instead.';
    var checked = form.querySelectorAll('input[required], textarea[required], input[type="email"], input[type="tel"]');
    var digits = function (value) { return value.replace(/\D/g, ''); };

    form.noValidate = true;   // our messages replace the browser's pop-up bubbles

    // Arriving from a service page (contact.html?type=EV%20charger) selects that type of work
    var typeSelect = form.querySelector('select[name="type"]');
    var asked = null;
    try { asked = new URLSearchParams(window.location.search).get('type'); } catch (e) { /* older browser: leave the default */ }
    if (typeSelect && asked) {
      for (var t = 0; t < typeSelect.options.length; t++) {
        if (typeSelect.options[t].value === asked) typeSelect.selectedIndex = t;
      }
    }

    var problemWith = function (el) {
      var value = el.value.trim();
      if (el.required && !value) return el.getAttribute('data-required') || 'This one is needed.';
      if (el.type === 'tel' && value && digits(value).length < 10) return 'Please include the area code, 10 digits in all.';
      if (el.type === 'email' && value && el.validity && el.validity.typeMismatch) return 'That email address looks incomplete.';
      return '';
    };

    var review = function (el) {
      var field = el.closest('.field');
      var note = field.querySelector('.field-error');
      var problem = problemWith(el);
      if (problem) {
        if (!note) {
          note = document.createElement('p');
          note.className = 'field-error';
          note.id = el.id + '-error';
          field.appendChild(note);
        }
        note.textContent = problem;
        el.setAttribute('aria-invalid', 'true');
        el.setAttribute('aria-describedby', note.id);
      } else if (note) {
        field.removeChild(note);
        el.removeAttribute('aria-invalid');
        el.removeAttribute('aria-describedby');
      }
      field.classList.toggle('has-error', !!problem);
      return !problem;
    };

    for (var c = 0; c < checked.length; c++) {
      // A field is only judged once the visitor has left it, and is cleared as soon as they fix it
      checked[c].addEventListener('blur', function () {
        if (this.type === 'tel') {
          var d = digits(this.value);
          if (d.length === 11 && d.charAt(0) === '1') d = d.slice(1);
          if (d.length === 10) this.value = '(' + d.slice(0, 3) + ') ' + d.slice(3, 6) + '-' + d.slice(6);
        }
        if (this.value.trim() || this.getAttribute('aria-invalid')) review(this);
      });
      checked[c].addEventListener('input', function () {
        if (this.getAttribute('aria-invalid')) review(this);
      });
    }

    var show = function (message) {
      if (!status) return;
      status.className = 'form-status' + (message ? ' is-err' : '');
      status.textContent = message;
      if (message) status.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    };

    var busy = function (on) {
      if (!button) return;
      if (on) button.dataset.label = button.textContent;
      button.disabled = on;
      button.classList.toggle('is-busy', on);
      button.textContent = on ? 'Sending…' : (button.dataset.label || 'Send request');
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var honeypot = form.querySelector('input[name="bot-field"]');
      if (honeypot && honeypot.value) return; // silently drop bots

      var firstBad = null;
      for (var i = 0; i < checked.length; i++) {
        if (!review(checked[i]) && !firstBad) firstBad = checked[i];
      }
      if (firstBad) { firstBad.focus(); return; }

      var data = new FormData(form);
      var body = new URLSearchParams();
      data.forEach(function (value, key) { body.append(key, value); });

      show('');
      busy(true);
      fetch(form.getAttribute('action') || window.location.pathname, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString()
      }).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        form.reset();
        if (done) {
          form.classList.add('is-sent');
          done.hidden = false;
          done.focus();
          done.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
      }).catch(function () {
        show('The form could not be sent from this page. ' + fallback);
      }).then(function () { busy(false); });
    });

    var again = form.querySelector('.form-again');
    if (again && done) {
      again.addEventListener('click', function () {
        form.classList.remove('is-sent');
        done.hidden = true;
        var first = form.querySelector('input:not([type="hidden"]):not([name="bot-field"])');
        if (first) first.focus();
      });
    }
  }

  // Header firms up after a short scroll
  if (header) {
    var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 12); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Reveal sections and cards as they enter the viewport (skipped without IntersectionObserver)
  if ('IntersectionObserver' in window) {
    var targets = document.querySelectorAll('.section-head, .service-card, .why-item, .process li, .work-tile, .faq details, .price-box, .hours-card, .qq-copy, .qq-form');
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

  var qq = document.getElementById('quote');
  var barQuote = document.querySelector('.callbar-quote');
  if (qq && barQuote) barQuote.setAttribute('href', '#quote');
})();
