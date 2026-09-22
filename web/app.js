/* Loads out/summary.json, out/alerts.json and out/issues.json, then fills the page.
   Only summary.json is required: alerts and the Issue Lab show their own empty state without their file. */
(function (DW) {
  var $ = function (id) { return document.getElementById(id); };

  var get = function (url) {
    return fetch(url, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) return { err: r.status === 404 ? 'missing' : 'HTTP ' + r.status };
      return r.json().then(function (d) { return { data: d }; });
    }).catch(function (e) { return { err: e.message }; });
  };

  var showState = function (err) {
    $('state').innerHTML = err === 'missing'
      ? DW.empty('No results yet', 'DriftWatch has nothing to show until the pipeline has run. Run these, then reload this page.', 'make data train live drift')
      : DW.empty('Could not read out/summary.json', err + '. Serve the repo with make ui; opening index.html straight from disk blocks fetch.', 'make ui');
    $('lastrun').textContent = 'No run yet';
  };

  var render = function (s, a, l) {
    var when = new Date(s.generated_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
    $('lastrun').textContent = 'Last run ' + when;
    $('cards').innerHTML = DW.cards(s, a);
    $('strip').innerHTML = DW.strip(s);
    $('charts').innerHTML = DW.charts(s);
    $('features').innerHTML = DW.features(s);
    $('alerts').innerHTML = DW.alerts(a);
    $('lab').innerHTML = DW.lab(l);
    $('foot').textContent = 'Feast ' + s.versions.feast + ', Evidently ' + s.versions.evidently +
      ', reference of ' + s.reference_rows.toLocaleString() + ' rows. Charts show -log10(p): higher means stronger evidence of drift.';
    $('state').hidden = true;
    $('content').hidden = false;
  };

  Promise.all([get('../out/summary.json'), get('../out/alerts.json'), get('../out/issues.json')]).then(function (r) {
    if (!r[0].data) { showState(r[0].err); return; }
    try { render(r[0].data, r[1].data || null, r[2].data || null); }
    catch (e) { showState('The file has an unexpected shape (' + e.message + ')'); }
  });
})(window.DW);
