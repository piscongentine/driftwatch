/* Helpers, summary cards and the per-feature charts. Every function returns an HTML string.
   Data comes from out/summary.json and out/alerts.json (see app.js). Classic script, shared namespace DW. */
(function (DW) {
  var CAP = 8; // charts stop at p = 1e-8; anything stronger is drawn at the top edge
  var ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  var PATHS = {
    alert: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    check: '<circle cx="12" cy="12" r="10"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/>',
    db: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>'
  };

  DW.esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return ESC[c]; }); };
  DW.icon = function (n) { return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">' + PATHS[n] + '</svg>'; };
  DW.pill = function (kind, text) { return '<span class="pill ' + kind + '">' + DW.esc(text) + '</span>'; };
  DW.fmtP = function (p) { return p === null || p === undefined ? 'n/a' : p < 0.001 ? p.toExponential(1) : p.toFixed(3); };
  DW.empty = function (title, body, cmd) {
    return '<div class="empty">' + DW.icon('db') + '<h3>' + DW.esc(title) + '</h3><p>' + DW.esc(body) + '</p>' +
      (cmd ? '<p><code>' + DW.esc(cmd) + '</code></p>' : '') + '</div>';
  };

  var pct = function (v) { return Math.round(v * 100) + '%'; };
  var tested = function (s) { return s.batches.filter(function (b) { return b.status === 'ok'; }); };
  var card = function (i, label, value, sub, extra) {
    return '<article class="card fade" style="--i:' + i + '"><p class="label">' + label + '</p><p class="big">' + value +
      '</p><p class="sub">' + sub + '</p>' + (extra || '') + '</article>';
  };
  DW.tested = tested;

  DW.cards = function (s, a) {
    var ok = tested(s), last = ok[ok.length - 1];
    var lim = (a && a.limits) || { warn: 0.2, alert: 0.4 };
    var names = s.columns.map(function (c) { return c.name; });
    var c1, c2;
    if (!last) {
      c1 = card(0, 'Drifted share', 'n/a', 'No batch was large enough to test');
      c2 = card(1, 'Worst feature', 'n/a', 'No batch was large enough to test');
    } else {
      var hit = names.filter(function (n) { return last.columns[n].drifted; });
      var kind = last.share >= lim.alert ? 'alert' : last.share >= lim.warn ? 'warn' : 'ok';
      var word = { alert: 'Over alert limit', warn: 'Over warning limit', ok: 'Within limits' }[kind];
      var trend = s.batches.map(function (b) { return b.status === 'ok' ? b.share : null; });
      c1 = card(0, 'Drifted share', pct(last.share), hit.length + ' of ' + names.length + ' columns, batch ' + last.index,
        DW.pill(kind, word) + DW.spark(trend, lim.alert));
      var worst = names.slice().sort(function (x, y) { return (last.columns[y].level || 0) - (last.columns[x].level || 0); })[0];
      var w = last.columns[worst], meta = s.columns.filter(function (c) { return c.name === worst; })[0];
      c2 = card(1, 'Worst feature', w.drifted ? DW.esc(worst) : 'None drifting',
        'p = ' + DW.fmtP(w.p) + ' on ' + DW.esc(worst) + ', ' + DW.esc(meta.method),
        DW.pill(w.drifted ? 'alert' : 'ok', w.drifted ? 'Drifted' : 'Stable'));
    }
    var stale = s.freshness.filter(function (f) { return f.stale; });
    var c3 = card(2, 'Freshness', (s.freshness.length - stale.length) + ' of ' + s.freshness.length + ' fresh',
      stale.length ? stale.map(function (f) { return DW.esc(f.view) + ' is ' + Math.round(f.age_hours) + ' h old (ttl ' + Math.round(f.ttl_hours) + ' h)'; }).join('; ')
        : 'Every feature view is inside its ttl', DW.pill(stale.length ? 'warn' : 'ok', stale.length ? 'Stale data' : 'Fresh'));
    var c4 = a ? card(3, 'Alerts', a.counts.alert, a.counts.warn + ' warning(s) on top',
      DW.pill(a.counts.alert ? 'alert' : a.counts.warn ? 'warn' : 'ok', a.counts.alert ? 'Action needed' : a.counts.warn ? 'Review' : 'All clear'))
      : card(3, 'Alerts', 'n/a', 'Run make drift to create out/alerts.json');
    return c1 + c2 + c3 + c4;
  };

  DW.charts = function (s) {
    return s.columns.map(function (c, k) {
      var pts = s.batches.map(function (b) {
        if (b.status !== 'ok') {
          var why = b.status === 'empty' ? 'empty, not tested' : b.rows + ' rows, too few to test';
          return { i: b.index, v: null, note: DW.esc('Batch ' + b.index + ': ' + why) };
        }
        var col = b.columns[c.name];
        return { i: b.index, v: col.level, hot: col.drifted, note: DW.esc('Batch ' + b.index + ': p = ' + DW.fmtP(col.p) + (col.drifted ? ', drift' : '')) };
      });
      var n = pts.filter(function (p) { return p.hot; }).length, last = pts.filter(function (p) { return p.v !== null; }).pop();
      var label = DW.esc(c.name) + ': drift strength per batch. Points above the dashed line mean drift. ' + n + ' batches drifted.';
      var state = c.constant ? DW.pill('idle', 'Constant') : last && last.hot ? DW.pill('alert', 'Drifted') : DW.pill('ok', 'Stable');
      return '<article class="card chart fade" style="--i:' + (k + 4) + '"><header><h3>' + DW.esc(c.name) + '</h3>' + state + '</header>' +
        '<p class="sub">' + DW.esc(c.method) + '</p>' + DW.lineChart({ label: label, points: pts, limit: c.limit, cap: CAP }) + '</article>';
    }).join('');
  };

  DW.strip = function (s) {
    var m = s.model, d = s.detection, f = function (v) { return v === null ? 'n/a' : v.toFixed(2); };
    return '<span><b>Failure model</b> holdout accuracy ' + pct(m.accuracy) + ' (never-fails baseline ' + pct(m.baseline_accuracy) + ')</span>' +
      '<span>precision ' + f(m.precision) + '</span><span>recall ' + f(m.recall) + '</span><span>AUC ' + f(m.auc) + '</span>' +
      '<span><b>Drift detector</b> vs planted drift: precision ' + f(d.precision) + ', recall ' + f(d.recall) + '</span>';
  };
})(window.DW = window.DW || {});
