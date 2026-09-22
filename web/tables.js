/* The feature table, the alert list and the Issue Lab table. Every function returns an HTML string.
   Classic script, shared namespace DW (render.js loads first). */
(function (DW) {
  var esc = DW.esc, pill = DW.pill;
  var LAB = { Reproduced: 'warn', Fixed: 'ok', Error: 'alert' };

  DW.features = function (s) {
    var ok = DW.tested(s), last = ok[ok.length - 1];
    var rows = s.columns.map(function (c) {
      var col = last ? last.columns[c.name] : null;
      var n = ok.filter(function (b) { return b.columns[c.name].drifted; }).length;
      return { c: c, col: col, n: n };
    }).sort(function (a, b) { return ((b.col && b.col.level) || 0) - ((a.col && a.col.level) || 0); });
    var body = rows.map(function (r) {
      var state = r.c.constant ? pill('idle', 'Constant') : r.col && r.col.drifted ? pill('alert', 'Drifted') : pill('ok', 'Stable');
      return '<tr><td><b>' + esc(r.c.name) + '</b></td><td class="hide-sm">' + esc(r.c.method) + '</td>' +
        '<td class="num">' + (r.col ? DW.fmtP(r.col.p) : 'n/a') + '</td><td class="num">' + r.n + ' of ' + ok.length + '</td><td>' + state + '</td></tr>';
    }).join('');
    return '<div class="scroll" role="region" aria-label="Monitored features" tabindex="0"><table><caption class="sr-only">Monitored features, latest batch</caption><thead><tr><th>Feature</th>' +
      '<th class="hide-sm">Test</th><th class="num">p-value</th><th class="num">Batches drifted</th><th>Status</th></tr></thead><tbody>' + body + '</tbody></table></div>';
  };

  DW.alerts = function (a) {
    if (!a) return DW.empty('No alerts file yet', 'Alerts are written by the drift step.', 'make drift');
    if (!a.alerts.length) return '<div class="empty small">' + DW.icon('check') + '<p>No alerts. Every batch is inside its limits.</p></div>';
    return '<ul class="alerts" tabindex="0" aria-label="Alerts, newest first">' + a.alerts.map(function (x) {
      var when = x.batch === null ? 'Feast' : 'Batch ' + x.batch;
      return '<li class="' + x.level + '"><span class="ico">' + DW.icon(x.level === 'alert' ? 'alert' : 'info') + '</span>' +
        '<div><p class="t">' + esc(x.title) + '</p><p class="d">' + esc(x.detail) + '</p></div><span class="when">' + when + '</span></li>';
    }).join('') + '</ul>';
  };

  DW.lab = function (l) {
    if (!l) return DW.empty('The Issue Lab has not run yet', 'It reproduces one upstream bug per folder and reports the result.', 'make issues');
    var count = function (k) { return l.results.filter(function (r) { return r.status === k; }).length; };
    var body = l.results.map(function (r) {
      return '<tr><td>' + esc(r.repo) + '</td><td><a href="' + esc(r.url) + '" target="_blank" rel="noopener">#' + r.number + '</a></td>' +
        '<td>' + esc(r.title) + '</td><td class="hide-sm">' + esc(r.level) + '</td><td class="hide-sm">' + esc(r.upstream) +
        '</td><td>' + pill(LAB[r.status] || 'idle', r.status) + '</td></tr>';
    }).join('');
    return '<p class="panel-note">' + l.results.length + ' issues: ' + count('Reproduced') + ' reproduced, ' + count('Fixed') + ' fixed, ' +
      count('Error') + ' error. Reproduced means the bug is still there in the installed version.</p>' +
      '<div class="scroll" role="region" aria-label="Issue Lab results" tabindex="0"><table><caption class="sr-only">Upstream issues and their Issue Lab result</caption><thead><tr><th>Repo</th><th>Issue</th>' +
      '<th>Title</th><th class="hide-sm">Level</th><th class="hide-sm">Upstream</th><th>Lab result</th></tr></thead><tbody>' + body + '</tbody></table></div>';
  };
})(window.DW = window.DW || {});
