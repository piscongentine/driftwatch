/* Light and dark theme, shared by every page. Follows the system until the button is used, then remembers the choice.
   Needs render.js (for the icons). Classic script, shared namespace DW. */
(function (DW) {
  var root = document.documentElement;
  var dark = matchMedia('(prefers-color-scheme: dark)');
  var button = document.getElementById('theme');
  var effective = function () { return root.dataset.theme || (dark.matches ? 'dark' : 'light'); };
  var paint = function () {
    var to = effective() === 'dark' ? 'light' : 'dark';
    button.innerHTML = DW.icon(to === 'light' ? 'sun' : 'moon');
    button.setAttribute('aria-label', 'Switch to ' + to + ' theme');
  };

  try { var saved = localStorage.getItem('dw-theme'); if (saved) root.dataset.theme = saved; } catch (e) { /* private mode: no memory, still works */ }
  var asked = new URLSearchParams(location.search).get('theme'); // index.html?theme=dark: for links and screenshots
  if (asked === 'dark' || asked === 'light') root.dataset.theme = asked;
  button.addEventListener('click', function () {
    var next = effective() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('dw-theme', next); } catch (e) { /* see above */ }
    paint();
  });
  dark.addEventListener('change', paint);
  paint();
})(window.DW);
