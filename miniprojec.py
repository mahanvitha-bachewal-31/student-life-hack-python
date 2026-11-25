from pathlib import Path
import zipfile, textwrap, json, re, os
root = Path("/mnt/data/sleep_routine_analyzer_web")
root.mkdir(exist_ok=True)

html = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0b1220">
  <title>Sleep Routine Analyzer</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">◉</span><div><strong>REST / ROUTINE</strong><small>STUDENTLIFE HACK</small></div></div>
      <div class="side-caption">WORKSPACE</div>
      <nav class="nav">
        <button class="nav-link active" data-view="overview"><span>▦</span> Overview</button>
        <button class="nav-link" data-view="log"><span>＋</span> Log sleep</button>
        <button class="nav-link" data-view="records"><span>▤</span> Records</button>
        <button class="nav-link" data-view="insights"><span>⌁</span> Insights & exports</button>
      </nav>
      <div class="sidebar-bottom">
        <div class="target-box"><span class="target-icon">✦</span><div><b>Daily sleep target</b><strong>8 hours</strong><small>Personal tracking benchmark</small></div></div>
        <small class="privacy-note">🔒 Your data stays in this browser on this device.</small>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div><div class="eyebrow">HEALTH & WELLBEING <span> / </span> PROJECT #32</div><h1 id="page-title">Your sleep overview</h1><p id="page-subtitle">A clearer view of your rest, one night at a time.</p></div>
        <div class="top-actions"><span class="today-pill" id="today-label"></span><button class="button primary" id="quick-log">＋ Log sleep</button></div>
      </header>

      <section class="view active" id="view-overview">
        <div class="metric-grid">
          <article class="metric-card"><div class="metric-label">LOGGED NIGHTS <span>◷</span></div><div class="metric-value" id="metric-total">0</div><div class="metric-foot">Your tracked sleep history</div></article>
          <article class="metric-card"><div class="metric-label">AVERAGE SLEEP <span>⌁</span></div><div class="metric-value teal" id="metric-average">0.0<span class="unit">h</span></div><div class="metric-foot">Across all recorded nights</div></article>
          <article class="metric-card"><div class="metric-label">TARGET ACHIEVED <span>↗</span></div><div class="metric-value blue" id="metric-target">0</div><div class="metric-foot">Nights at or above 8 hours</div></article>
          <article class="metric-card"><div class="metric-label">CURRENT STREAK <span>✧</span></div><div class="metric-value amber" id="metric-streak">0</div><div class="metric-foot">Consecutive logged days</div></article>
        </div>

        <div class="content-grid">
          <article class="panel chart-panel">
            <div class="panel-heading"><div><h2>Sleep duration trend</h2><p>Your recent sleep patterns against the 8-hour target</p></div><span class="legend"><i></i> Sleep duration <b></b> Target</span></div>
            <div class="chart-wrap"><canvas id="trend-chart" aria-label="Sleep duration chart"></canvas><div class="empty-chart" id="chart-empty">Your sleep trend will appear here after you add records.</div></div>
          </article>
          <article class="panel alerts-panel">
            <div class="panel-heading"><div><h2>Routine check</h2><p>Automated threshold indicators</p></div><span class="status-dot"></span></div>
            <div id="alerts-list" class="alerts-list"></div>
          </article>
        </div>
        <article class="panel recent-panel">
          <div class="panel-heading"><div><h2>Recent activity</h2><p>Your latest logged nights</p></div><button class="text-button" data-go="records">View all records →</button></div>
          <div class="table-scroll"><table><thead><tr><th>DATE</th><th>BEDTIME</th><th>WAKE TIME</th><th>DURATION</th><th>QUALITY</th><th>STATUS</th></tr></thead><tbody id="recent-body"></tbody></table></div>
          <div class="table-empty hidden" id="recent-empty">No sleep records yet. Start by logging last night's sleep.</div>
        </article>
      </section>

      <section class="view" id="view-log">
        <div class="section-intro"><div><span class="eyebrow">NEW ENTRY</span><h2>Log a night of sleep</h2><p>Enter your bedtime and wake time. Duration is calculated automatically.</p></div><div class="date-chip">◷ &nbsp; One entry per sleep date</div></div>
        <div class="form-layout">
          <form class="panel sleep-form" id="sleep-form" novalidate>
            <div class="form-grid">
              <label>Sleep date <span>YYYY-MM-DD</span><input id="sleep-date" type="date" required></label>
              <label>Bedtime <span>24-hour time</span><input id="bedtime" type="time" value="22:30" required></label>
              <label>Wake time <span>24-hour time</span><input id="wake-time" type="time" value="06:30" required></label>
              <label>Sleep quality <span>1 = poor · 5 = excellent</span><select id="quality"><option value="1">1 — Very poor</option><option value="2">2 — Poor</option><option value="3" selected>3 — Fair</option><option value="4">4 — Good</option><option value="5">5 — Excellent</option></select></label>
              <label class="full">Notes <span>Optional</span><textarea id="notes" rows="4" placeholder="Anything that affected your sleep? e.g. late study session, exercise, caffeine..."></textarea></label>
            </div>
            <div class="duration-preview"><div><span>CALCULATED SLEEP DURATION</span><strong id="duration-preview">8h 00m</strong></div><span id="duration-hint">Based on your bedtime and wake time</span></div>
            <div class="form-actions"><button type="reset" class="button secondary">Clear form</button><button type="submit" class="button primary">Save sleep record <span>→</span></button></div>
            <p class="form-message" id="form-message" role="status"></p>
          </form>
          <aside class="panel info-panel"><div class="info-icon">✦</div><h3>How it works</h3><p>If your wake time is earlier than your bedtime, the app treats it as the next day.</p><div class="rule"></div><div class="info-stat"><span>Valid sleep duration</span><b>0.5–18 hours</b></div><div class="info-stat"><span>Time format</span><b>24-hour clock</b></div><div class="info-stat"><span>Daily target</span><b>8 hours</b></div><div class="tip">Tip: Log your sleep consistently to build a more useful picture of your routine.</div></aside>
        </div>
      </section>

      <section class="view" id="view-records">
        <div class="section-intro"><div><span class="eyebrow">YOUR HISTORY</span><h2>Sleep records</h2><p>Search, filter, edit, or remove your saved entries.</p></div><button class="button primary" data-go="log">＋ Add record</button></div>
        <article class="panel records-panel">
          <div class="toolbar"><div class="search-box"><span>⌕</span><input id="search-input" type="search" placeholder="Search date, notes or time..."></div><select id="filter-select"><option>All records</option><option>Below target</option><option>Target met</option><option>Poor quality</option></select><button class="button secondary small" id="import-csv">↑ Import CSV</button></div>
          <div class="table-scroll"><table><thead><tr><th>DATE</th><th>BEDTIME</th><th>WAKE TIME</th><th>DURATION</th><th>QUALITY</th><th>NOTES</th><th>ACTIONS</th></tr></thead><tbody id="records-body"></tbody></table></div>
          <div class="table-empty hidden" id="records-empty">No matching records found.</div>
          <div class="table-footer"><span id="record-count">0 records</span><button class="text-button" id="download-json">Download JSON backup ↓</button></div>
        </article>
        <input id="csv-file" type="file" accept=".csv,text/csv" hidden>
      </section>

      <section class="view" id="view-insights">
        <div class="section-intro"><div><span class="eyebrow">YOUR PROGRESS</span><h2>Insights & exports</h2><p>A summary of your sleep patterns and downloadable reports.</p></div></div>
        <div class="insight-grid">
          <article class="panel insight-card"><span class="insight-icon">◷</span><span class="muted">AVERAGE SLEEP</span><strong id="ins-average">0.0h</strong><small>Across all logged nights</small></article>
          <article class="panel insight-card"><span class="insight-icon blue-bg">✓</span><span class="muted">TARGET MET</span><strong id="ins-target">0</strong><small>Nights with 8 hours or more</small></article>
          <article class="panel insight-card"><span class="insight-icon amber-bg">★</span><span class="muted">AVERAGE QUALITY</span><strong id="ins-quality">0/5</strong><small>Your self-reported rating</small></article>
          <article class="panel insight-card"><span class="insight-icon pink-bg">⌁</span><span class="muted">BEST NIGHT</span><strong id="ins-best">0.0h</strong><small>Longest logged duration</small></article>
        </div>
        <div class="content-grid export-grid">
          <article class="panel"><div class="panel-heading"><div><h2>Export your reports</h2><p>Save your sleep data for review or sharing.</p></div></div>
            <div class="export-option"><div class="file-icon">MD</div><div><b>Markdown summary</b><small>Executive overview, records and warnings</small></div><button class="button secondary small" id="export-md">Download</button></div>
            <div class="export-option"><div class="file-icon">TXT</div><div><b>Plain-text audit log</b><small>Chronological record and alert history</small></div><button class="button secondary small" id="export-txt">Download</button></div>
            <div class="export-option"><div class="file-icon">CSV</div><div><b>Standard CSV report</b><small>Structured spreadsheet-compatible data</small></div><button class="button secondary small" id="export-csv">Download</button></div>
            <div class="export-option"><div class="file-icon">PNG</div><div><b>Sleep trend chart</b><small>Visual sleep duration chart</small></div><button class="button secondary small" id="export-png">Download</button></div>
          </article>
          <article class="panel"><div class="panel-heading"><div><h2>Sleep distribution</h2><p>How your logged nights are distributed</p></div></div><div class="distribution" id="distribution"></div><div class="disclaimer">This tool is for personal awareness and educational use. It is not a medical diagnostic tool.</div></article>
        </div>
      </section>
      <footer>Sleep Routine Analyzer <span>•</span> Local-first student project <span>•</span> Your data stays on this device</footer>
    </main>
  </div>
  <div class="toast" id="toast" role="status"></div>
  <dialog id="edit-dialog"><form method="dialog" id="edit-form"><div class="dialog-head"><div><span class="eyebrow">UPDATE ENTRY</span><h2>Edit sleep record</h2></div><button class="icon-button" value="cancel" aria-label="Close">×</button></div><input type="hidden" id="edit-id"><div class="form-grid compact"><label>Sleep date<input id="edit-date" type="date" required></label><label>Bedtime<input id="edit-bed" type="time" required></label><label>Wake time<input id="edit-wake" type="time" required></label><label>Quality<select id="edit-quality"><option value="1">1 — Very poor</option><option value="2">2 — Poor</option><option value="3">3 — Fair</option><option value="4">4 — Good</option><option value="5">5 — Excellent</option></select></label><label class="full">Notes<textarea id="edit-notes" rows="3"></textarea></label></div><div class="form-actions"><button class="button secondary" value="cancel">Cancel</button><button class="button primary" id="save-edit" value="default">Save changes</button></div></form></dialog>
  <script src="app.js"></script>
</body>
</html>'''

css = r'''@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--bg:#0b1220;--panel:#121d30;--panel2:#18263d;--line:#263650;--text:#edf3ff;--muted:#91a2bd;--teal:#69e0c1;--blue:#83aaff;--amber:#ffbd69;--red:#ff7d91;--font:'DM Sans',sans-serif;--head:'Manrope',sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);font-size:14px}.app-shell{min-height:100vh;display:flex}.sidebar{width:245px;flex-shrink:0;background:#0e192a;border-right:1px solid #1d2a40;padding:27px 18px 20px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:11px;padding:0 8px 42px}.brand-mark{width:38px;height:38px;border-radius:12px;background:rgba(105,224,193,.13);color:var(--teal);display:grid;place-items:center;font-size:24px}.brand strong{display:block;font:800 12px var(--head);letter-spacing:1.2px}.brand small{display:block;color:var(--muted);font-size:9px;letter-spacing:1.5px;margin-top:4px}.side-caption,.eyebrow{font-size:10px;font-weight:700;letter-spacing:1.5px;color:#7185a5}.side-caption{padding:0 12px 12px}.nav{display:grid;gap:6px}.nav-link{width:100%;border:0;background:transparent;color:#9babc4;text-align:left;padding:13px 14px;border-radius:9px;font:600 13px var(--font);cursor:pointer;display:flex;gap:13px;align-items:center}.nav-link span{font-size:18px;width:18px;text-align:center}.nav-link:hover,.nav-link.active{background:#1a3041;color:var(--teal)}.sidebar-bottom{margin-top:auto}.target-box{display:flex;gap:12px;background:#172b3a;border:1px solid #244a50;border-radius:12px;padding:14px}.target-icon{color:var(--teal);font-size:21px}.target-box b,.target-box strong,.target-box small{display:block}.target-box b{font-size:11px;color:#b9c8da}.target-box strong{font:800 20px var(--head);color:var(--teal);margin:3px 0}.target-box small,.privacy-note{font-size:10px;color:var(--muted)}.privacy-note{display:block;line-height:1.6;padding:15px 5px 0}.main{max-width:1600px;width:calc(100% - 245px);padding:28px 38px 18px;margin:0 auto}.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}.eyebrow span{color:#40516d}.topbar h1{font:800 27px var(--head);margin:7px 0 3px;letter-spacing:-.8px}.topbar p,.section-intro p,.panel-heading p{margin:0;color:var(--muted);font-size:12px}.top-actions{display:flex;align-items:center;gap:14px}.today-pill,.date-chip{border:1px solid var(--line);padding:9px 12px;border-radius:8px;color:#b7c5d8;font-size:11px}.button{border:0;border-radius:8px;padding:11px 16px;font:700 12px var(--font);cursor:pointer;transition:.18s}.button:hover{transform:translateY(-1px);filter:brightness(1.08)}.primary{background:var(--teal);color:#09201f}.secondary{background:#22324b;color:#dce7f6;border:1px solid #31445f}.small{padding:9px 12px;font-size:11px}.view{display:none}.view.active{display:block}.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}.metric-card,.panel{background:var(--panel);border:1px solid #22324a;border-radius:13px}.metric-card{padding:18px 19px}.metric-label{display:flex;justify-content:space-between;color:var(--muted);font-size:9px;font-weight:700;letter-spacing:1.2px}.metric-label span{font-size:16px;color:#7891ae}.metric-value{font:800 29px var(--head);margin:13px 0 4px}.metric-value.teal{color:var(--teal)}.metric-value.blue{color:var(--blue)}.metric-value.amber{color:var(--amber)}.unit{font-size:15px;margin-left:3px}.metric-foot{font-size:10px;color:var(--muted)}.content-grid{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(280px,.85fr);gap:15px;margin-bottom:15px}.panel{padding:19px}.panel-heading{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:16px}.panel-heading h2,.section-intro h2{font:700 15px var(--head);margin:0 0 5px}.panel-heading p{font-size:10px}.legend{font-size:9px;color:var(--muted);white-space:nowrap}.legend i{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--teal);margin-right:5px}.legend b{display:inline-block;width:13px;border-top:2px dashed var(--amber);margin:0 5px 2px 9px}.chart-wrap{height:215px;position:relative}.chart-wrap canvas{width:100%;height:100%}.empty-chart{position:absolute;inset:0;display:grid;place-items:center;color:#70829f;font-size:11px;text-align:center;pointer-events:none}.status-dot{width:8px;height:8px;background:var(--teal);border-radius:50%;box-shadow:0 0 0 4px #69e0c11a;margin:5px}.alerts-list{display:grid;gap:9px;max-height:210px;overflow:auto}.alert-item{display:flex;gap:9px;padding:10px;border-radius:8px;background:#1a2a40;color:#c6d2e3;font-size:10px;line-height:1.5}.alert-item .alert-symbol{color:var(--amber);font-size:14px}.alert-item.good .alert-symbol{color:var(--teal)}.recent-panel{padding-bottom:10px}.text-button{border:0;background:none;color:var(--teal);font:700 10px var(--font);cursor:pointer}.table-scroll{overflow:auto}table{border-collapse:collapse;width:100%;white-space:nowrap}th{text-align:left;color:#778aa8;font-size:9px;letter-spacing:1px;font-weight:700;padding:11px 12px;border-bottom:1px solid #2a3a52}td{padding:13px 12px;border-bottom:1px solid #202f45;color:#cbd6e6;font-size:11px}tbody tr:last-child td{border-bottom:0}.duration{font-weight:700;color:var(--teal)}.pill{padding:5px 8px;border-radius:20px;font-size:9px;font-weight:700}.pill.met{background:#173c38;color:var(--teal)}.pill.low{background:#403426;color:var(--amber)}.pill.poor{background:#422b3a;color:var(--red)}.table-empty{padding:28px;text-align:center;color:var(--muted);font-size:11px}.hidden{display:none!important}footer{padding:22px 0 5px;color:#647895;font-size:10px}footer span{padding:0 6px;color:#40516d}.section-intro{display:flex;justify-content:space-between;align-items:center;margin:12px 0 20px}.section-intro h2{font-size:22px;margin:5px 0}.date-chip{font-size:10px}.form-layout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(260px,.75fr);gap:16px}.sleep-form{padding:25px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px 16px}.form-grid label{font-size:11px;font-weight:700;color:#cbd7e7;display:flex;flex-direction:column;gap:7px}.form-grid label span{font-size:9px;color:var(--muted);font-weight:400}.form-grid .full{grid-column:1/-1}input,select,textarea{font:12px var(--font);color:var(--text);background:#1a2940;border:1px solid #30425d;border-radius:7px;padding:11px 12px;outline:none;width:100%;color-scheme:dark}input:focus,select:focus,textarea:focus{border-color:var(--teal);box-shadow:0 0 0 2px #69e0c11a}textarea{resize:vertical}.duration-preview{margin-top:22px;padding:16px;background:#173a39;border:1px solid #245953;border-radius:9px;display:flex;justify-content:space-between;align-items:center}.duration-preview span{font-size:9px;color:#a0c8c1}.duration-preview strong{display:block;color:var(--teal);font:800 23px var(--head);margin-top:4px}.duration-preview>span{font-size:10px}.form-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:18px}.form-message{font-size:11px;color:var(--red);min-height:14px;margin-bottom:0}.info-panel{padding:24px}.info-icon{width:38px;height:38px;background:#173a39;color:var(--teal);border-radius:10px;display:grid;place-items:center;font-size:19px}.info-panel h3{font:700 16px var(--head);margin:15px 0 7px}.info-panel p{font-size:11px;color:var(--muted);line-height:1.7;margin:0}.rule{border-top:1px solid var(--line);margin:19px 0}.info-stat{display:flex;justify-content:space-between;gap:10px;font-size:10px;margin:13px 0;color:var(--muted)}.info-stat b{color:#dce7f6}.tip{margin-top:21px;padding:12px;border-radius:8px;background:#1b3041;color:#9fc9c2;font-size:10px;line-height:1.6}.records-panel{padding:16px}.toolbar{display:flex;gap:10px;align-items:center;margin-bottom:15px}.search-box{display:flex;align-items:center;gap:8px;background:#1a2940;border:1px solid #30425d;border-radius:7px;padding-left:11px;flex:1;color:var(--muted)}.search-box input{border:0;background:transparent;box-shadow:none}.toolbar select{width:155px}.table-footer{display:flex;justify-content:space-between;align-items:center;border-top:1px solid #263650;padding:13px 4px 0;color:var(--muted);font-size:10px}.row-actions{display:flex;gap:6px}.mini-action{border:1px solid #34465f;background:#1b2b43;color:#cbd7e7;border-radius:5px;padding:5px 8px;cursor:pointer;font-size:10px}.mini-action.delete{color:var(--red)}.insight-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin-bottom:15px}.insight-card{display:grid;grid-template-columns:38px 1fr;column-gap:10px;align-items:center;padding:16px}.insight-icon{grid-row:span 3;width:35px;height:35px;border-radius:9px;background:#173a39;color:var(--teal);display:grid;place-items:center;font-size:16px}.blue-bg{background:#1c3150;color:var(--blue)}.amber-bg{background:#403426;color:var(--amber)}.pink-bg{background:#422b3a;color:var(--red)}.insight-card .muted{font-size:9px;color:var(--muted);letter-spacing:.8px}.insight-card strong{font:800 21px var(--head);margin:3px 0}.insight-card small{font-size:9px;color:var(--muted)}.export-grid{grid-template-columns:1.15fr .85fr}.export-option{display:flex;align-items:center;gap:11px;padding:13px 0;border-bottom:1px solid #263650}.export-option:last-child{border:0}.file-icon{width:35px;height:35px;border-radius:8px;background:#1b3042;color:var(--teal);display:grid;place-items:center;font-size:9px;font-weight:800}.export-option div:nth-child(2){flex:1}.export-option b,.export-option small{display:block}.export-option b{font-size:11px}.export-option small{font-size:9px;color:var(--muted);margin-top:4px}.distribution{display:grid;gap:13px;margin:20px 0}.dist-row{display:grid;grid-template-columns:95px 1fr 28px;gap:9px;align-items:center;font-size:10px;color:var(--muted)}.dist-track{height:7px;border-radius:10px;background:#263650;overflow:hidden}.dist-fill{height:100%;border-radius:10px;background:var(--teal)}.disclaimer{border-top:1px solid var(--line);padding-top:13px;font-size:9px;line-height:1.6;color:var(--muted)}dialog{background:var(--panel);color:var(--text);border:1px solid #354863;border-radius:14px;width:min(560px,calc(100% - 30px));padding:23px;box-shadow:0 24px 90px #0009}dialog::backdrop{background:#050b15cc;backdrop-filter:blur(3px)}.dialog-head{display:flex;justify-content:space-between;margin-bottom:20px}.dialog-head h2{font:700 20px var(--head);margin:5px 0}.icon-button{border:0;background:#263650;color:white;border-radius:7px;width:30px;height:30px;font-size:20px;cursor:pointer}.compact{gap:14px}.toast{position:fixed;right:24px;bottom:22px;background:#173a39;color:var(--teal);border:1px solid #28665b;padding:12px 17px;border-radius:8px;font-size:11px;opacity:0;transform:translateY(10px);transition:.2s;pointer-events:none}.toast.show{opacity:1;transform:translateY(0)}
@media(max-width:1050px){.sidebar{width:205px}.main{width:calc(100% - 205px);padding:24px}.metric-grid,.insight-grid{grid-template-columns:repeat(2,1fr)}.content-grid,.form-layout{grid-template-columns:1fr}.alerts-list{max-height:none}}
@media(max-width:700px){.app-shell{display:block}.sidebar{width:100%;padding:14px 15px;border-right:0;border-bottom:1px solid var(--line)}.brand{padding:0 5px 13px}.side-caption,.sidebar-bottom{display:none}.nav{display:flex;overflow:auto}.nav-link{white-space:nowrap;padding:10px}.nav-link span{display:none}.main{width:100%;padding:20px 14px}.topbar{align-items:flex-start;gap:12px}.topbar h1{font-size:21px}.top-actions{flex-direction:column;align-items:flex-end;gap:8px}.today-pill{display:none}.metric-grid{gap:9px}.metric-card{padding:14px}.metric-value{font-size:24px}.content-grid,.export-grid{grid-template-columns:1fr}.section-intro{align-items:flex-start;gap:10px}.date-chip{display:none}.toolbar{flex-wrap:wrap}.search-box{flex-basis:100%}.toolbar select{flex:1}.form-grid{grid-template-columns:1fr}.form-grid .full{grid-column:auto}.duration-preview{align-items:flex-start;gap:8px;flex-direction:column}.insight-grid{gap:8px}.insight-card{padding:11px;grid-template-columns:30px 1fr}.insight-icon{width:28px;height:28px}.panel{padding:14px}}
'''

js = r'''const TARGET = 8;
const STORE = "sleepRoutineAnalyzer.records.v1";
let records = loadRecords();
let editingId = null;
const $ = id => document.getElementById(id);
const todayISO = () => new Date().toLocaleDateString("en-CA");
const safe = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function loadRecords(){
  try { const data = JSON.parse(localStorage.getItem(STORE) || "[]"); return Array.isArray(data) ? data : []; }
  catch { return []; }
}
function persist(){ localStorage.setItem(STORE, JSON.stringify(records)); }
function duration(bed, wake){
  if(!bed || !wake) throw new Error("Please enter both bedtime and wake time.");
  const [bh,bm]=bed.split(":").map(Number), [wh,wm]=wake.split(":").map(Number);
  if([bh,bm,wh,wm].some(Number.isNaN)) throw new Error("Use valid 24-hour times.");
  let mins=(wh*60+wm)-(bh*60+bm); if(mins<=0) mins+=1440;
  const hours=mins/60;
  if(hours<.5 || hours>18) throw new Error("Sleep duration must be between 0.5 and 18 hours. Please check the times.");
  return Math.round(hours*100)/100;
}
function validateDate(d){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(d)) throw new Error("Date must use YYYY-MM-DD format.");
  const parsed=new Date(d+"T00:00:00");
  if(Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0,10)!==d) throw new Error("Enter a valid date.");
  if(d>todayISO()) throw new Error("Sleep date cannot be in the future.");
  return d;
}
function formatHours(h){const mins=Math.round(h*60);return `${Math.floor(mins/60)}h ${String(mins%60).padStart(2,"0")}m`;}
function sorted(){return [...records].sort((a,b)=>b.sleep_date.localeCompare(a.sleep_date));}
function summary(){
  const n=records.length, total=records.reduce((s,r)=>s+r.duration_hours,0);
  const dates=new Set(records.map(r=>r.sleep_date));let cursor=todayISO(),streak=0;
  if(!dates.has(cursor)){const y=new Date();y.setDate(y.getDate()-1);cursor=y.toLocaleDateString("en-CA");}
  while(dates.has(cursor)){streak++;const d=new Date(cursor+"T00:00:00");d.setDate(d.getDate()-1);cursor=d.toLocaleDateString("en-CA");}
  return {total:n,average:n?total/n:0,target:records.filter(r=>r.duration_hours>=TARGET).length,
    below:records.filter(r=>r.duration_hours<TARGET).length,quality:n?records.reduce((s,r)=>s+r.quality,0)/n:0,
    best:n?Math.max(...records.map(r=>r.duration_hours)):0,streak};
}
function alerts(){
  const a=[];const latest=sorted().slice(0,7);
  latest.forEach(r=>{if(r.duration_hours<6)a.push({text:`${r.sleep_date}: Very short sleep (${r.duration_hours.toFixed(1)}h). Review your routine.`,kind:"warn"});
    else if(r.duration_hours<TARGET)a.push({text:`${r.sleep_date}: Below the 8-hour tracking target (${r.duration_hours.toFixed(1)}h).`,kind:"warn"});
    if(r.quality<=2)a.push({text:`${r.sleep_date}: Low sleep-quality rating (${r.quality}/5).`,kind:"poor"});});
  if(latest.length>=3 && latest.slice(0,3).every(r=>r.duration_hours<6))a.unshift({text:"Pattern alert: your latest three logged nights are each below 6 hours.",kind:"poor"});
  return a;
}
function toast(msg){const el=$("toast");el.textContent=msg;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2600);}
function go(view){
  document.querySelectorAll(".view").forEach(v=>v.classList.toggle("active",v.id===`view-${view}`));
  document.querySelectorAll(".nav-link").forEach(b=>b.classList.toggle("active",b.dataset.view===view));
  const titles={overview:["Your sleep overview","A clearer view of your rest, one night at a time."],log:["Log your sleep","Capture your bedtime, wake time and how rested you felt."],records:["Sleep records","Search, filter, edit, or remove your saved entries."],insights:["Insights & exports","A summary of your sleep patterns and downloadable reports."]};
  $("page-title").textContent=titles[view][0];$("page-subtitle").textContent=titles[view][1];
  if(view==="log"){$("sleep-date").value=$("sleep-date").value||todayISO();updatePreview();}
  if(view==="records")renderRecords();
  window.scrollTo({top:0,behavior:"smooth"});
}
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.view)));
document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.go)));
$("quick-log").addEventListener("click",()=>go("log"));

function render(){
  const s=summary();
  $("metric-total").textContent=s.total;$("metric-average").innerHTML=`${s.average.toFixed(1)}<span class="unit">h</span>`;
  $("metric-target").textContent=s.target;$("metric-streak").textContent=s.streak;
  $("ins-average").textContent=s.average.toFixed(1)+"h";$("ins-target").textContent=s.target;
  $("ins-quality").textContent=s.quality.toFixed(1)+"/5";$("ins-best").textContent=s.best.toFixed(1)+"h";
  renderAlerts();renderRecent();renderRecords();renderChart();renderDistribution();
}
function renderAlerts(){
  const a=alerts();$("alerts-list").innerHTML=a.length?a.map(x=>`<div class="alert-item"><span class="alert-symbol">${x.kind==="poor"?"!":"◆"}</span><span>${safe(x.text)}</span></div>`).join(""):`<div class="alert-item good"><span class="alert-symbol">✓</span><span>No threshold warnings. Keep logging your sleep to build a useful trend.</span></div>`;
}
function statusPill(r){return r.duration_hours>=TARGET?'<span class="pill met">Target met</span>':'<span class="pill low">Below target</span>';}
function renderRecent(){
  const arr=sorted().slice(0,5);$("recent-body").innerHTML=arr.map(r=>`<tr><td>${safe(r.sleep_date)}</td><td>${safe(r.bedtime)}</td><td>${safe(r.wake_time)}</td><td class="duration">${r.duration_hours.toFixed(1)}h</td><td>${r.quality}/5</td><td>${statusPill(r)}</td></tr>`).join("");
  $("recent-empty").classList.toggle("hidden",arr.length>0);
}
function renderRecords(){
  if(!$("records-body"))return;
  const q=($("search-input")?.value||"").toLowerCase(),filter=$("filter-select")?.value||"All records";
  const arr=sorted().filter(r=>{
    const text=[r.sleep_date,r.bedtime,r.wake_time,r.notes,String(r.quality)].join(" ").toLowerCase();
    return (!q||text.includes(q))&&(filter==="All records"||(filter==="Below target"&&r.duration_hours<TARGET)||(filter==="Target met"&&r.duration_hours>=TARGET)||(filter==="Poor quality"&&r.quality<=2));
  });
  $("records-body").innerHTML=arr.map(r=>`<tr><td>${safe(r.sleep_date)}</td><td>${safe(r.bedtime)}</td><td>${safe(r.wake_time)}</td><td class="duration">${r.duration_hours.toFixed(2)}h</td><td>${r.quality}/5</td><td>${safe(r.notes||"—")}</td><td><div class="row-actions"><button class="mini-action" data-edit="${r.id}">Edit</button><button class="mini-action delete" data-delete="${r.id}">Delete</button></div></td></tr>`).join("");
  $("records-empty").classList.toggle("hidden",arr.length>0);$("record-count").textContent=`${arr.length} of ${records.length} record(s)`;
  document.querySelectorAll("[data-edit]").forEach(b=>b.addEventListener("click",()=>openEdit(b.dataset.edit)));
  document.querySelectorAll("[data-delete]").forEach(b=>b.addEventListener("click",()=>deleteRecord(b.dataset.delete)));
}
function renderChart(){
  const canvas=$("trend-chart"),ctx=canvas.getContext("2d"),arr=[...records].sort((a,b)=>a.sleep_date.localeCompare(b.sleep_date)).slice(-14);
  const rect=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;canvas.width=rect.width*dpr;canvas.height=rect.height*dpr;ctx.scale(dpr,dpr);
  const w=rect.width,h=rect.height,p={l:35,r:12,t:18,b:35};ctx.clearRect(0,0,w,h);
  $("chart-empty").classList.toggle("hidden",arr.length>0);if(!arr.length)return;
  const max=Math.max(10,...arr.map(r=>r.duration_hours));const yMax=Math.ceil(max/2)*2;
  const x=i=>p.l+(arr.length===1?(w-p.l-p.r)/2:i*(w-p.l-p.r)/(arr.length-1));
  const y=v=>h-p.b-(v/yMax)*(h-p.t-p.b);
  ctx.font="10px DM Sans";ctx.fillStyle="#8193ae";ctx.strokeStyle="#263650";ctx.lineWidth=1;
  for(let v=0;v<=yMax;v+=2){ctx.beginPath();ctx.moveTo(p.l,y(v));ctx.lineTo(w-p.r,y(v));ctx.stroke();ctx.fillText(v+"h",2,y(v)+3);}
  ctx.save();ctx.setLineDash([5,5]);ctx.strokeStyle="#ffbd69";ctx.beginPath();ctx.moveTo(p.l,y(TARGET));ctx.lineTo(w-p.r,y(TARGET));ctx.stroke();ctx.restore();
  const grad=ctx.createLinearGradient(0,p.t,0,h-p.b);grad.addColorStop(0,"rgba(105,224,193,.25)");grad.addColorStop(1,"rgba(105,224,193,0)");
  ctx.beginPath();arr.forEach((r,i)=>i?ctx.lineTo(x(i),y(r.duration_hours)):ctx.moveTo(x(i),y(r.duration_hours)));ctx.lineTo(x(arr.length-1),h-p.b);ctx.lineTo(x(0),h-p.b);ctx.closePath();ctx.fillStyle=grad;ctx.fill();
  ctx.beginPath();arr.forEach((r,i)=>i?ctx.lineTo(x(i),y(r.duration_hours)):ctx.moveTo(x(i),y(r.duration_hours)));ctx.strokeStyle="#69e0c1";ctx.lineWidth=2.5;ctx.stroke();
  arr.forEach((r,i)=>{ctx.beginPath();ctx.arc(x(i),y(r.duration_hours),3.5,0,Math.PI*2);ctx.fillStyle="#69e0c1";ctx.fill();if(arr.length<=8||i===0||i===arr.length-1){ctx.fillStyle="#91a2bd";ctx.font="9px DM Sans";ctx.textAlign="center";ctx.fillText(r.sleep_date.slice(5),x(i),h-10);}});
}
function renderDistribution(){
  const groups=[["Under 6h",records.filter(r=>r.duration_hours<6).length],["6–7.9h",records.filter(r=>r.duration_hours>=6&&r.duration_hours<TARGET).length],["8–9.9h",records.filter(r=>r.duration_hours>=8&&r.duration_hours<10).length],["10h+",records.filter(r=>r.duration_hours>=10).length]];
  const max=Math.max(1,records.length);$("distribution").innerHTML=groups.map(([name,n])=>`<div class="dist-row"><span>${name}</span><div class="dist-track"><div class="dist-fill" style="width:${n/max*100}%"></div></div><b>${n}</b></div>`).join("");
}
function refresh(){persist();render();}
$("sleep-form").addEventListener("submit",e=>{
  e.preventDefault();$("form-message").textContent="";
  try{
    const d=validateDate($("sleep-date").value),bed=$("bedtime").value,wake=$("wake-time").value,q=Number($("quality").value),hours=duration(bed,wake);
    if(records.some(r=>r.sleep_date===d))throw new Error("A record already exists for this sleep date. Edit or delete it first.");
    records.push({id:crypto.randomUUID?crypto.randomUUID():String(Date.now()),sleep_date:d,bedtime:bed,wake_time:wake,duration_hours:hours,quality:q,notes:$("notes").value.trim()});
    refresh();$("sleep-form").reset();$("sleep-date").value=todayISO();$("bedtime").value="22:30";$("wake-time").value="06:30";$("quality").value="3";updatePreview();toast(`Saved ${formatHours(hours)} of sleep.`);go("overview");
  }catch(err){$("form-message").textContent=err.message;}
});
function updatePreview(){
  try{const h=duration($("bedtime").value,$("wake-time").value);$("duration-preview").textContent=formatHours(h);$("duration-hint").textContent=h>=TARGET?"At or above the 8-hour target":"Below the 8-hour tracking target";}
  catch{$("duration-preview").textContent="—";$("duration-hint").textContent="Enter valid bedtime and wake time";}
}
["bedtime","wake-time"].forEach(id=>$(id).addEventListener("input",updatePreview));
$("sleep-date").value=todayISO();$("today-label").textContent=new Date().toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric",year:"numeric"});
$("search-input").addEventListener("input",renderRecords);$("filter-select").addEventListener("change",renderRecords);

function openEdit(id){
  const r=records.find(x=>x.id===id);if(!r)return;editingId=id;
  $("edit-id").value=id;$("edit-date").value=r.sleep_date;$("edit-bed").value=r.bedtime;$("edit-wake").value=r.wake_time;$("edit-quality").value=r.quality;$("edit-notes").value=r.notes||"";
  $("edit-dialog").showModal();
}
$("save-edit").addEventListener("click",e=>{
  e.preventDefault();try{
    const r=records.find(x=>x.id===editingId);if(!r)throw new Error("Record no longer exists.");
    const d=validateDate($("edit-date").value),bed=$("edit-bed").value,wake=$("edit-wake").value;
    if(records.some(x=>x.id!==editingId&&x.sleep_date===d))throw new Error("Another record already exists for this date.");
    r.sleep_date=d;r.bedtime=bed;r.wake_time=wake;r.duration_hours=duration(bed,wake);r.quality=Number($("edit-quality").value);r.notes=$("edit-notes").value.trim();
    $("edit-dialog").close();refresh();toast("Record updated.");
  }catch(err){alert(err.message);}
});
function deleteRecord(id){
  const r=records.find(x=>x.id===id);if(!r)return;
  if(confirm(`Delete the sleep record for ${r.sleep_date}? This cannot be undone.`)){records=records.filter(x=>x.id!==id);refresh();toast("Record deleted.");}
}

function download(name,content,type="text/plain"){
  const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=name;a.click();URL.revokeObjectURL(url);
}
function csvEscape(v){return `"${String(v??"").replace(/"/g,'""')}"`;}
function recordsCSV(arr=records){
  const cols=["sleep_date","bedtime","wake_time","duration_hours","quality","notes"];
  return [cols.join(","),...arr.map(r=>cols.map(k=>csvEscape(r[k])).join(","))].join("\n");
}
function reportMarkdown(){
  const s=summary();return `# Sleep Routine Analyzer — Summary\n\nGenerated: ${new Date().toLocaleString()}\n\n## Overview\n- Total records: ${s.total}\n- Average sleep: ${s.average.toFixed(2)} hours\n- Best night: ${s.best.toFixed(2)} hours\n- Target met: ${s.target} nights\n- Below target: ${s.below} nights\n- Average quality: ${s.quality.toFixed(1)}/5\n- Current streak: ${s.streak} days\n\n## Sleep records\n\n| Date | Bedtime | Wake time | Hours | Quality | Notes |\n|---|---|---|---:|---:|---|\n${sorted().map(r=>`| ${r.sleep_date} | ${r.bedtime} | ${r.wake_time} | ${r.duration_hours.toFixed(2)} | ${r.quality}/5 | ${(r.notes||"").replaceAll("|","/")} |`).join("\n")}\n\n## Alerts\n${alerts().map(a=>"- "+a.text).join("\n")||"- No threshold warnings."}\n\n> Personal awareness tool only; not a medical diagnostic tool.\n`;}
function reportText(){return `SLEEP ROUTINE ANALYZER AUDIT\nGenerated: ${new Date().toLocaleString()}\nRecords: ${records.length}\n\n${sorted().map(r=>`${r.sleep_date} | ${r.bedtime}-${r.wake_time} | ${r.duration_hours.toFixed(2)}h | quality ${r.quality}/5 | ${r.notes}`).join("\n")}\n\nWARNINGS\n${alerts().map(a=>"- "+a.text).join("\n")||"None"}\n`;}
$("export-md").addEventListener("click",()=>download("sleep_summary.md",reportMarkdown(),"text/markdown"));
$("export-txt").addEventListener("click",()=>download("sleep_audit.txt",reportText()));
$("export-csv").addEventListener("click",()=>download("sleep_records.csv",recordsCSV(),"text/csv"));
$("download-json").addEventListener("click",()=>download("sleep_records_backup.json",JSON.stringify(records,null,2),"application/json"));
$("export-png").addEventListener("click",()=>{
  if(!records.length){toast("Add records before exporting a chart.");return;}
  const c=document.createElement("canvas");c.width=1200;c.height=560;const ctx=c.getContext("2d");ctx.fillStyle="#0b1220";ctx.fillRect(0,0,c.width,c.height);ctx.fillStyle="#edf3ff";ctx.font="bold 30px sans-serif";ctx.fillText("Sleep duration trend",55,55);
  const arr=[...records].sort((a,b)=>a.sleep_date.localeCompare(b.sleep_date));const max=Math.max(10,...arr.map(r=>r.duration_hours));const x=i=>80+i*1040/Math.max(1,arr.length-1),y=v=>465-v/max*340;
  ctx.strokeStyle="#ffbd69";ctx.setLineDash([9,8]);ctx.beginPath();ctx.moveTo(80,y(TARGET));ctx.lineTo(1120,y(TARGET));ctx.stroke();ctx.setLineDash([]);
  ctx.strokeStyle="#69e0c1";ctx.lineWidth=5;ctx.beginPath();arr.forEach((r,i)=>i?ctx.lineTo(x(i),y(r.duration_hours)):ctx.moveTo(x(i),y(r.duration_hours)));ctx.stroke();
  arr.forEach((r,i)=>{ctx.fillStyle="#69e0c1";ctx.beginPath();ctx.arc(x(i),y(r.duration_hours),7,0,7);ctx.fill();ctx.fillStyle="#91a2bd";ctx.font="14px sans-serif";ctx.fillText(r.sleep_date.slice(5),x(i)-24,500);});
  c.toBlob(blob=>{const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="sleep_trend.png";a.click();URL.revokeObjectURL(url);});
});

$("import-csv").addEventListener("click",()=>$("csv-file").click());
$("csv-file").addEventListener("change",async e=>{
  const file=e.target.files[0];if(!file)return;
  try{
    const text=await file.text(),lines=text.replace(/^\uFEFF/,"").split(/\r?\n/).filter(x=>x.trim());
    const parseLine=line=>{const out=[];let cur="",quoted=false;for(let i=0;i<line.length;i++){const c=line[i];if(c==='"'&&line[i+1]==='"'&&quoted){cur+='"';i++;}else if(c==='"')quoted=!quoted;else if(c===","&&!quoted){out.push(cur);cur="";}else cur+=c;}out.push(cur);return out;};
    const headers=parseLine(lines[0]).map(x=>x.trim());const required=["sleep_date","bedtime","wake_time"];
    if(!required.every(x=>headers.includes(x)))throw new Error("CSV must include sleep_date, bedtime and wake_time columns.");
    let added=0,issues=[];
    lines.slice(1).forEach((line,i)=>{try{
      const vals=parseLine(line),row=Object.fromEntries(headers.map((h,j)=>[h,vals[j]??""])),d=validateDate(row.sleep_date),hours=duration(row.bedtime,row.wake_time),q=Number(row.quality||3);
      if(!Number.isInteger(q)||q<1||q>5)throw new Error("quality must be 1–5");
      if(records.some(r=>r.sleep_date===d))throw new Error("duplicate sleep date");
      records.push({id:crypto.randomUUID?crypto.randomUUID():String(Date.now()+i),sleep_date:d,bedtime:row.bedtime,wake_time:row.wake_time,duration_hours:hours,quality:q,notes:row.notes||""});added++;
    }catch(err){issues.push(`Row ${i+2}: ${err.message}`);}});
    refresh();alert(`Imported ${added} record(s).${issues.length?`\n\nSkipped rows:\n${issues.slice(0,12).join("\n")}`:""}`);toast(`CSV import complete: ${added} added.`);
  }catch(err){alert("Import failed: "+err.message);}finally{e.target.value="";}
});

window.addEventListener("resize",()=>renderChart());
render();go("overview");
'''

readme = r'''# Sleep Routine Analyzer — HTML, CSS & JavaScript Edition

This is the browser-based version of StudentLife Hack Project #32.

## Run the project
1. Extract the ZIP file.
2. Open the `sleep_routine_analyzer_web` folder.
3. Double-click `index.html` to open it in Chrome, Edge or Firefox.

No Python, Java, Node.js, database server or installation is needed.

## Files
- `index.html` — page structure and forms
- `styles.css` — modern responsive dashboard styling
- `app.js` — validation, calculations, storage, search, reports, charts and CSV import/export

## Implemented functionality
- Responsive modern dashboard with Overview, Log Sleep, Records, and Insights & Exports views.
- Sleep and wake time input using 24-hour time.
- Automatic overnight duration calculation.
- Date validation, future-date rejection, 0.5–18 hour duration validation, quality validation and one record per date.
- Browser localStorage persistence.
- Search by date/time/notes and category filters.
- Edit and delete records.
- Summary metrics: total, average, target achieved, best night, average quality and logging streak.
- Canvas trend chart and sleep duration distribution.
- Warnings for under-6-hour sleep, below-target sleep, low quality, and repeated short nights.
- Markdown summary, TXT audit log, CSV report, JSON backup and PNG chart downloads.
- Bulk CSV import with required-column checks, per-row validation, duplicate-date handling and issue reporting.

## CSV import template
Headers:
`sleep_date,bedtime,wake_time,quality,notes`

Example:
```csv
sleep_date,bedtime,wake_time,quality,notes
2026-11-20,22:30,06:30,4,No caffeine late
2026-11-21,23:15,07:00,3,Study night
```

## Important
Data is saved in the browser's localStorage on the device and browser used. It is not automatically synchronized across devices or browsers. Use Download JSON backup regularly if you want a portable copy. This is a personal tracking tool, not a medical diagnostic application.
'''

for name, content in {"index.html":html,"styles.css":css,"app.js":js,"README.md":readme,
                      "sleep_import_template.csv":"sleep_date,bedtime,wake_time,quality,notes\n2026-11-20,22:30,06:30,4,No caffeine late\n"}.items():
    (root/name).write_text(textwrap.dedent(content).lstrip(),encoding="utf-8")

zip_path=Path("/mnt/data/Sleep_Routine_Analyzer_HTML_CSS_JavaScript.zip")
with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
    for f in root.rglob("*"):
        if f.is_file(): z.write(f,Path(root.name)/f.relative_to(root))
print("Created",zip_path,zip_path.stat().st_size)
