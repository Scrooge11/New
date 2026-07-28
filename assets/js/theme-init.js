// Runs before first paint (loaded in <head>) to prevent theme flash.
(function () {
  document.documentElement.classList.add('js');
  try {
    var t = localStorage.getItem('bwp-theme');
    if (t === 'light' || t === 'dark') {
      document.documentElement.setAttribute('data-theme', t);
    }
  } catch (e) { /* storage unavailable — fall back to prefers-color-scheme */ }
})();
