/* Loaded in <head> so it runs before the page paints: a visitor who picked light or dark with
   the theme button gets that theme straight away, with no flash of the other one.
   With no stored choice the page follows the system setting (see the top of css/styles.css). */
(function () {
  var root = document.documentElement;
  root.classList.add('js');
  try {
    var choice = localStorage.getItem('jemco-theme');
    if (choice === 'light' || choice === 'dark') root.setAttribute('data-theme', choice);
  } catch (e) { /* storage blocked: keep following the system setting */ }
})();
