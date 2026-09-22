/* Hand-written SVG charts, no library. Each function returns an SVG string.
   Colours come from CSS classes, so both themes work without any code here.
   Classic script (not a module): Python's http.server can serve .js as text/plain on Windows. */
(function (DW) {
  var W = 320, H = 150, L = 34, R = 10, T = 12, B = 24;

  // points: [{i, v, hot, note}]; v is null for a batch that was not tested.
  DW.lineChart = function (o) {
    var pts = o.points, n = pts.length;
    var top = Math.min(o.cap, Math.max.apply(null, pts.map(function (p) { return p.v || 0; })));
    var max = Math.max(o.limit * 1.6, top * 1.1);
    var x = function (i) { return L + (n < 2 ? 0 : (i / (n - 1)) * (W - L - R)); };
    var y = function (v) { return T + (1 - Math.min(v, max) / max) * (H - T - B); };

    var out = ['<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + o.label + '">'];
    out.push('<rect class="zone" x="' + L + '" y="' + T + '" width="' + (W - L - R) + '" height="' + (y(o.limit) - T) + '"/>');
    [0, max].forEach(function (v) {
      out.push('<line class="grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + y(v) + '" y2="' + y(v) + '"/>');
      out.push('<text class="tick" x="' + (L - 6) + '" y="' + (y(v) + 3) + '" text-anchor="end">' + (v ? v.toFixed(0) : 0) + '</text>');
    });
    out.push('<line class="limit" x1="' + L + '" x2="' + (W - R) + '" y1="' + y(o.limit) + '" y2="' + y(o.limit) + '"/>');
    out.push('<text class="tick limit-label" x="' + (W - R) + '" y="' + (y(o.limit) - 4) + '" text-anchor="end">limit</text>');

    var run = [];
    var flush = function () {
      if (run.length > 1) out.push('<path class="line" pathLength="1" d="M' + run.join(' L') + '"/>');
      run = [];
    };
    pts.forEach(function (p, k) {
      if (k % 2 === 0) out.push('<text class="tick" x="' + x(k) + '" y="' + (H - 6) + '" text-anchor="middle">' + p.i + '</text>');
      if (p.v === null) {
        flush();
        out.push('<path class="skip" d="M' + (x(k) - 3) + ' ' + (H - B - 10) + ' l6 6 m0 -6 l-6 6"><title>' + p.note + '</title></path>');
        return;
      }
      run.push(x(k).toFixed(1) + ' ' + y(p.v).toFixed(1));
      out.push('<circle class="pt' + (p.hot ? ' hot' : '') + '" cx="' + x(k).toFixed(1) + '" cy="' + y(p.v).toFixed(1) + '" r="3.5"><title>' + p.note + '</title></circle>');
    });
    flush();
    return out.join('') + '</svg>';
  };

  // A tiny trend line for a card: values are 0..1 shares, null for untested batches.
  DW.spark = function (values, limit) {
    var w = 120, h = 32, n = values.length, run = [], d = [];
    var x = function (i) { return 2 + (i / Math.max(1, n - 1)) * (w - 4); };
    var y = function (v) { return h - 3 - Math.min(v, 1) * (h - 6); };
    values.forEach(function (v, i) {
      if (v === null) { if (run.length) d.push('M' + run.join(' L')); run = []; return; }
      run.push(x(i).toFixed(1) + ' ' + y(v).toFixed(1));
    });
    if (run.length) d.push('M' + run.join(' L'));
    return '<svg class="spark" viewBox="0 0 ' + w + ' ' + h + '" aria-hidden="true">' +
      '<line class="limit" x1="2" x2="' + (w - 2) + '" y1="' + y(limit) + '" y2="' + y(limit) + '"/>' +
      '<path class="line" pathLength="1" d="' + d.join(' ') + '"/></svg>';
  };
})(window.DW = window.DW || {});
