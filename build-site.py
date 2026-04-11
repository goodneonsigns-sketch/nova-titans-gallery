#!/usr/bin/env python3
"""Build the Nova Titans gallery site with clickable player cards, stats, and game galleries."""
import json
import os

# Load data
with open('data.json') as f:
    data = json.load(f)

# Load game photos data if available
game_photos = {}
if os.path.exists('game-photos.json'):
    with open('game-photos.json') as f:
        game_photos = json.load(f)

# Photo counts per game folder (from game-photos.json or fallback)
game_photo_counts = {}
for folder, gdata in game_photos.items():
    game_photo_counts[folder] = gdata.get('total_photos', 0)

roster = data['roster']
schedule = data['schedule']
team = data['team']

# Build HTML
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nova Titans Baseball — Spring 2026 Photo Gallery</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Oswald:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--g:#006633;--gd:#FFD700;--bg:#0a0f0a;--cb:#131a13;--t:#f0f0f0;--tm:#999;--w:#2ecc71;--l:#e74c3c}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--t);line-height:1.6}}
h1,h2,h3,h4{{font-family:'Oswald',sans-serif;font-weight:700}}
a{{color:var(--gd);text-decoration:none}}
.container{{max-width:1200px;margin:0 auto;padding:0 20px}}

/* Nav */
nav{{position:sticky;top:0;background:rgba(10,15,10,.95);backdrop-filter:blur(10px);border-bottom:1px solid #1a1a1a;z-index:100;padding:12px 0}}
nav .container{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap}}
nav img{{height:40px}}
nav ul{{list-style:none;display:flex;gap:20px}}
nav a{{color:var(--tm);font-size:14px;font-weight:500;transition:.2s}}
nav a:hover{{color:var(--gd)}}

/* Hero */
.hero{{padding:120px 0 80px;text-align:center;background:linear-gradient(180deg,rgba(10,15,10,.55),rgba(10,15,10,.85)),url('hero.jpg') center 40%/cover no-repeat;position:relative}}
.hero img{{width:100px;margin-bottom:20px;filter:drop-shadow(0 0 20px rgba(255,215,0,.4))}}
.hero h1{{font-size:clamp(2.5rem,6vw,4.5rem);letter-spacing:3px;background:linear-gradient(135deg,var(--gd),#fff,var(--gd));-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-shadow:0 0 40px rgba(255,215,0,.3)}}
.hero .sub{{color:#ccc;font-size:1.1rem;margin:8px 0}}
.hero .record{{font-family:'Oswald';font-size:2rem;color:var(--gd);text-shadow:0 2px 10px rgba(0,0,0,.5)}}

/* Stats bar */
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;padding:40px 0}}
.stat{{background:var(--cb);border:1px solid #1e2e1e;border-radius:12px;padding:20px;text-align:center}}
.stat h4{{color:var(--gd);font-size:.85rem;text-transform:uppercase;letter-spacing:1px}}
.stat p{{font-size:1.4rem;font-weight:700;margin-top:4px}}
.stat span{{color:var(--tm);font-size:.8rem}}

/* Section */
section{{padding:50px 0}}
.st{{font-size:2rem;text-align:center;margin-bottom:30px;color:var(--gd)}}

/* Action strip */
.action-strip{{display:flex;gap:12px;overflow-x:auto;padding:20px 0;scroll-snap-type:x mandatory}}
.action-strip img{{height:300px;border-radius:10px;object-fit:cover;scroll-snap-align:start;flex-shrink:0}}

/* Roster with headshots */
.yg{{margin-bottom:30px}}
.yg h3{{font-size:1.3rem;color:var(--gd);border-bottom:2px solid #1e2e1e;padding-bottom:8px;margin-bottom:16px}}
.pg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}}
.pc{{background:var(--cb);border:1px solid #1e2e1e;border-radius:10px;padding:14px;display:flex;gap:12px;align-items:center;cursor:pointer;transition:.3s;position:relative;overflow:hidden}}
.pc:hover{{border-color:var(--gd);transform:translateY(-2px);box-shadow:0 4px 20px rgba(255,215,0,.15)}}
.pc-photo{{width:120px;height:120px;border-radius:50%;object-fit:cover;border:3px solid var(--g);flex-shrink:0}}
.pc-placeholder{{width:120px;height:120px;border-radius:50%;background:linear-gradient(135deg,var(--g),#004d26);border:3px solid #1e2e1e;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-family:'Oswald';font-size:2.5rem;color:var(--gd)}}
.pn{{font-family:'Oswald';font-size:1.1rem;color:var(--gd);min-width:30px}}
.pi h4{{font-size:.95rem;margin-bottom:2px}}
.pi .pos{{color:var(--g);font-weight:600;font-size:.8rem}}
.pi .hw{{color:var(--tm);font-size:.75rem}}
.pi .ba{{color:var(--gd);font-size:.8rem;font-weight:600;margin-top:2px}}

/* Player Modal */
.modal-overlay{{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.85);z-index:200;overflow-y:auto;padding:20px}}
.modal-overlay.active{{display:flex;align-items:flex-start;justify-content:center}}
.modal{{background:var(--cb);border:1px solid #1e2e1e;border-radius:16px;max-width:700px;width:100%;margin:40px auto;padding:0;overflow:hidden;position:relative}}
.modal-close{{position:absolute;top:16px;right:16px;background:rgba(0,0,0,.6);border:none;color:#fff;font-size:1.5rem;width:36px;height:36px;border-radius:50%;cursor:pointer;z-index:10;display:flex;align-items:center;justify-content:center}}
.modal-close:hover{{background:var(--l)}}
.modal-header{{background:linear-gradient(135deg,var(--g),#004d26);padding:30px;display:flex;gap:20px;align-items:center}}
.modal-photo{{width:120px;height:120px;border-radius:50%;object-fit:cover;border:3px solid var(--gd)}}
.modal-placeholder{{width:120px;height:120px;border-radius:50%;background:rgba(0,0,0,.3);border:3px solid var(--gd);display:flex;align-items:center;justify-content:center;font-family:'Oswald';font-size:3rem;color:var(--gd)}}
.modal-info h2{{font-family:'Oswald';font-size:1.8rem;color:#fff}}
.modal-info .num{{color:var(--gd);font-size:2.5rem;font-family:'Oswald'}}
.modal-info .details{{color:rgba(255,255,255,.8);font-size:.9rem}}
.modal-body{{padding:24px}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:10px;margin-bottom:24px}}
.stat-box{{background:rgba(0,0,0,.3);border-radius:8px;padding:10px;text-align:center}}
.stat-box .val{{font-family:'Oswald';font-size:1.3rem;color:var(--gd)}}
.stat-box .label{{font-size:.7rem;color:var(--tm);text-transform:uppercase}}
.modal-photos{{margin-top:16px}}
.modal-photos h3{{font-size:1.1rem;color:var(--gd);margin-bottom:12px}}
.modal-photo-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}}
.modal-photo-grid img{{width:100%;border-radius:8px;cursor:pointer;transition:.3s}}
.modal-photo-grid img:hover{{transform:scale(1.05)}}

/* Game Gallery */
.gg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
.gc{{background:var(--cb);border:1px solid #1e2e1e;border-radius:10px;padding:20px;transition:.3s;cursor:pointer}}
.gc:hover{{border-color:var(--gd)}}
.gc.win{{border-left:3px solid var(--w)}}
.gc.loss{{border-left:3px solid var(--l)}}
.gc.upcoming{{border-left:3px solid var(--gd)}}
.gd{{color:var(--gd);font-family:'Oswald';font-size:.9rem}}
.go{{font-size:1.1rem;font-weight:600;margin:6px 0}}
.gr{{font-weight:700;margin-bottom:8px}}
.gr.win-text{{color:var(--w)}}
.gr.loss-text{{color:var(--l)}}
.gp{{color:var(--tm);font-size:.85rem;padding:12px;text-align:center;border:1px dashed #333;border-radius:8px;margin-top:8px}}
.gp-count{{color:var(--gd);font-weight:600}}
.gp img{{width:100%;max-height:180px;object-fit:cover;border-radius:8px;margin-bottom:6px}}
.gp-thumbs{{display:grid;grid-template-columns:repeat(2,1fr);gap:4px;margin-bottom:8px}}
.gp-thumbs img{{width:100%;height:80px;object-fit:cover;border-radius:6px;transition:.3s}}
.gp-thumbs img:hover{{opacity:.8}}

/* Schedule */
table{{width:100%;border-collapse:collapse}}
th{{background:var(--g);color:#fff;padding:10px;text-align:left;font-family:'Oswald';font-size:.9rem}}
td{{padding:10px;border-bottom:1px solid #1a1a1a;font-size:.9rem}}
tr:hover{{background:rgba(255,215,0,.05)}}
.win-r{{color:var(--w);font-weight:700}}
.loss-r{{color:var(--l);font-weight:700}}
.upcoming-r{{color:var(--gd)}}

/* Footer */
footer{{text-align:center;padding:40px 0;border-top:1px solid #1a1a1a;color:var(--tm);font-size:.85rem}}
footer .titles{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-bottom:16px}}
footer .title-badge{{background:var(--cb);border:1px solid #1e2e1e;border-radius:6px;padding:4px 10px;font-size:.75rem}}

/* Responsive */
@media(max-width:900px){{.action-strip img{{height:200px}}.modal-header{{flex-direction:column;text-align:center}}}}
@media(max-width:600px){{.pg{{grid-template-columns:1fr}}.gg{{grid-template-columns:1fr}}.stats{{grid-template-columns:repeat(2,1fr)}}.stats-grid{{grid-template-columns:repeat(4,1fr)}}nav ul{{gap:10px}}nav a{{font-size:12px}}}}
</style>
</head>
<body>

<nav>
<div class="container">
<img src="logo.png" alt="Nova Titans">
<ul>
<li><a href="#roster">Roster</a></li>
<li><a href="#games">Games</a></li>
<li><a href="#schedule">Schedule</a></li>
<li><a href="#history">History</a></li>
</ul>
</div>
</nav>

<header class="hero">
<img src="logo.png" alt="Nova Titans Logo">
<h1>NOVA TITANS</h1>
<p class="sub">Spring 2026 &bull; {team["district"]} &bull; {team["location"]}</p>
<p class="record">{team["record"]["overall"]}</p>
</header>

<div class="container">
<div class="stats">
<div class="stat"><h4>Overall</h4><p>{team["record"]["overall"]}</p></div>
<div class="stat"><h4>Team BA</h4><p>.316</p></div>
<div class="stat"><h4>Runs Scored</h4><p>33</p></div>
<div class="stat"><h4>Games Played</h4><p>12</p></div>
</div>
</div>

<div class="container">
<div class="action-strip">
<img src="action1.jpg" alt="Pitcher in windup">
<img src="action2.jpg" alt="Batter at plate">
<img src="action3.jpg" alt="Runner scoring">
<img src="action4.jpg" alt="Play at home">
<img src="action5.jpg" alt="On the mound">
<img src="action6.jpg" alt="Dugout">
</div>
</div>
'''

# --- ROSTER SECTION ---
html += '<section id="roster"><div class="container">\n'
html += '<h2 class="st">⚾ ROSTER</h2>\n'

# Group by grad year
years = {}
for p in roster:
    y = p['gradYear']
    if y not in years:
        years[y] = []
    years[y].append(p)

for year in sorted(years.keys()):
    players = years[year]
    label = "Seniors" if year == 2026 else "Juniors" if year == 2027 else "Sophomores" if year == 2028 else "Freshmen"
    html += f'<div class="yg"><h3>{label} (Class of {year})</h3><div class="pg">\n'
    
    for p in sorted(players, key=lambda x: x['number']):
        num = p['number']
        name = p['name']
        pos = p['positions'] or '—'
        ht = p['height'] or '—'
        wt = p['weight'] or '—'
        headshot = p.get('headshot')
        batting = p.get('batting', {})
        pitching = p.get('pitching', {})
        
        # Check for headshot
        if headshot:
            photo_html = f'<img class="pc-photo" src="{headshot}" alt="{name}">'
        else:
            photo_html = f'<div class="pc-placeholder">#{num}</div>'
        
        # Check for batting stats
        ba_display = batting.get('BA', '')
        if ba_display and ba_display != '0' and ba_display != '.000' and ba_display != '0.00':
            ba_html = f'<div class="ba">BA: {ba_display}</div>'
        else:
            ba_html = ''
        
        # Build stats data attribute for modal
        stats_json = json.dumps({
            'batting': batting,
            'pitching': pitching
        }).replace('"', '&quot;')
        
        html += f'''<div class="pc" onclick="openPlayer({num})" data-num="{num}" data-name="{name}" data-pos="{pos}" data-ht="{ht}" data-wt="{wt}" data-grad="{year}" data-headshot="{headshot or ''}" data-stats="{stats_json}">
{photo_html}
<div class="pi">
<h4><span class="pn">#{num}</span> {name}</h4>
<span class="pos">{pos}</span>
<span class="hw">{ht} &bull; {wt} lbs &bull; Class of {year}</span>
{ba_html}
</div>
</div>
'''
    html += '</div></div>\n'

html += '</div></section>\n'

# --- GAME GALLERY SECTION ---
html += '<section id="games"><div class="container">\n'
html += '<h2 class="st">📸 GAME GALLERY</h2>\n'
html += '<div class="gg">\n'

# Create a mapping from date string to folder name
date_to_folder = {}
for folder, gdata in game_photos.items():
    date_str = gdata['info']['date']
    date_to_folder[date_str] = folder

for game in schedule:
    result = game['result']
    if result == 'upcoming' or result == 'N/A':
        css_class = 'upcoming' if result == 'upcoming' else ''
        result_class = 'upcoming-r'
        result_text = 'Upcoming' if result == 'upcoming' else 'TBD'
    elif '(W)' in result:
        css_class = 'win'
        result_class = 'win-text'
        result_text = result
    else:
        css_class = 'loss'
        result_class = 'loss-text'
        result_text = result
    
    folder = date_to_folder.get(game['date'])
    photo_count = game_photo_counts.get(folder, 0) if folder else 0
    
    photo_section = ''
    game_folder_data = game_photos.get(folder, {}) if folder else {}
    thumbs = game_folder_data.get('thumbnails', [])
    
    if thumbs:
        thumb_grid = '<div class="gp-thumbs">'
        for t in thumbs[:4]:  # Show 4 thumbnails on the card
            thumb_grid += f'<img src="{t["thumb"]}" alt="Game photo" loading="lazy">'
        thumb_grid += '</div>'
        photo_section = f'{thumb_grid}<div class="gp"><span class="gp-count">📷 {photo_count} photos</span> — Click to view all</div>'
    elif photo_count > 0:
        photo_section = f'<div class="gp"><span class="gp-count">📷 {photo_count} photos</span><br>Click to view & download</div>'
    elif result != 'upcoming':
        photo_section = '<div class="gp">No photos yet</div>'
    else:
        photo_section = '<div class="gp">Game not yet played</div>'
    
    # Store folder name as data attribute for modal
    folder_attr = f'data-folder="{folder}"' if folder and thumbs else ''
    click_attr = f'onclick="openGameGallery(\'{folder}\')"' if folder and thumbs else ''
    
    html += f'''<div class="gc {css_class}" {folder_attr} {click_attr}>
<div class="gd">{game["date"]} &bull; {game["time"]}</div>
<div class="go">vs {game["opponent"]}</div>
<div class="gr {result_class}">{result_text}</div>
{photo_section}
</div>
'''

html += '</div></div></section>\n'

# --- SCHEDULE TABLE ---
html += '<section id="schedule"><div class="container">\n'
html += '<h2 class="st">📅 FULL SCHEDULE</h2>\n'
html += '<table><tr><th>Date</th><th>Time</th><th>Opponent</th><th>Type</th><th>Result</th></tr>\n'

for game in schedule:
    result = game['result']
    if '(W)' in result:
        rc = 'win-r'
    elif '(L)' in result:
        rc = 'loss-r'
    elif result == 'upcoming':
        rc = 'upcoming-r'
        result = '—'
    else:
        rc = ''
    
    opp_rec = f' ({game["oppRecord"]})' if game.get('oppRecord') else ''
    html += f'<tr><td>{game["date"]}</td><td>{game["time"]}</td><td>{game["opponent"]}{opp_rec}</td><td>{game["type"]}</td><td class="{rc}">{result}</td></tr>\n'

html += '</table></div></section>\n'

# --- HISTORY / TITLES ---
html += '<section id="history"><div class="container">\n'
html += '<h2 class="st">🏆 PROGRAM HISTORY</h2>\n'
html += '<footer><div class="titles">\n'
for title in data['titles']:
    html += f'<span class="title-badge">{title}</span>\n'
html += '</div>\n'
html += f'<p>Head Coach: {data["coaches"][0]["name"]} ({data["coaches"][0]["totalYears"]} years) &bull; '
html += f'Asst: {data["coaches"][1]["name"]} ({data["coaches"][1]["totalYears"]} years)</p>\n'
html += '<p style="margin-top:12px;font-size:.75rem;color:#555">Nova Titans Baseball &bull; Davie, FL &bull; Updated 2026-04-10</p>\n'
html += '</footer></div></section>\n'

# --- PLAYER MODAL + LIGHTBOX ---
html += '''
<!-- Player Modal -->
<div class="modal-overlay" id="playerModal" onclick="if(event.target===this)closePlayer()">
<div class="modal">
<button class="modal-close" onclick="closePlayer()">&times;</button>
<div class="modal-header" id="modalHeader"></div>
<div class="modal-body" id="modalBody"></div>
</div>
</div>

<!-- Game Gallery Lightbox -->
<div id="gameLightbox" class="lb-overlay" role="dialog" aria-modal="true" aria-label="Game photo gallery">
  <!-- Grid view -->
  <div id="lbGrid" class="lb-grid-view">
    <div class="lb-grid-header">
      <div class="lb-game-info">
        <h2 id="lbGameTitle" class="lb-game-title"></h2>
        <div id="lbGameMeta" class="lb-game-meta"></div>
        <div id="lbPhotoCount" class="lb-photo-count"></div>
      </div>
      <button class="lb-close-btn" onclick="closeLightbox()" aria-label="Close">&times;</button>
    </div>
    <div id="lbThumbnailGrid" class="lb-thumbnail-grid"></div>
  </div>

  <!-- Single photo view -->
  <div id="lbSingle" class="lb-single-view" style="display:none">
    <div class="lb-single-header">
      <button class="lb-back-btn" onclick="showGrid()" aria-label="Back to grid">&#8592; All Photos</button>
      <span id="lbCounter" class="lb-counter"></span>
      <button class="lb-close-btn" onclick="closeLightbox()" aria-label="Close">&times;</button>
    </div>
    <div class="lb-image-area" id="lbImageArea">
      <button class="lb-nav lb-prev" id="lbPrev" onclick="navigatePhoto(-1)" aria-label="Previous photo">&#10094;</button>
      <div class="lb-img-wrapper" id="lbImgWrapper">
        <img id="lbMainImg" class="lb-main-img" src="" alt="Game photo">
      </div>
      <button class="lb-nav lb-next" id="lbNext" onclick="navigatePhoto(1)" aria-label="Next photo">&#10095;</button>
    </div>
  </div>
</div>

<style>
/* ===== LIGHTBOX STYLES ===== */
.lb-overlay{display:none;position:fixed;inset:0;background:#0a0f0a;z-index:500;flex-direction:column;overflow:hidden}
.lb-overlay.lb-active{display:flex}

/* Grid view */
.lb-grid-view{display:flex;flex-direction:column;height:100%;overflow:hidden}
.lb-grid-header{display:flex;align-items:flex-start;justify-content:space-between;padding:20px 24px 16px;border-bottom:1px solid #1e2e1e;flex-shrink:0;background:linear-gradient(180deg,rgba(0,102,51,.3),transparent)}
.lb-game-title{font-family:'Oswald',sans-serif;font-size:1.8rem;color:#fff;margin-bottom:4px}
.lb-game-meta{color:rgba(255,255,255,.75);font-size:.95rem;margin-bottom:6px}
.lb-photo-count{color:#FFD700;font-size:.85rem;font-weight:600}
.lb-close-btn{background:rgba(255,255,255,.12);border:none;color:#fff;font-size:1.8rem;width:44px;height:44px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:.2s;line-height:1}
.lb-close-btn:hover{background:rgba(231,76,60,.8)}

.lb-thumbnail-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;padding:20px 24px;overflow-y:auto;flex:1}
.lb-thumb-item{border-radius:10px;overflow:hidden;cursor:pointer;background:#131a13;border:2px solid transparent;transition:.25s;aspect-ratio:4/3}
.lb-thumb-item:hover{border-color:#FFD700;transform:scale(1.02);box-shadow:0 4px 20px rgba(255,215,0,.2)}
.lb-thumb-item img{width:100%;height:100%;object-fit:cover;display:block;transition:.2s}

/* Single photo view */
.lb-single-view{display:flex;flex-direction:column;height:100%}
.lb-single-header{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid #1e2e1e;flex-shrink:0;background:rgba(0,0,0,.5)}
.lb-back-btn{background:none;border:1px solid rgba(255,255,255,.25);color:#fff;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:.85rem;transition:.2s}
.lb-back-btn:hover{border-color:#FFD700;color:#FFD700}
.lb-counter{color:rgba(255,255,255,.75);font-family:'Oswald',sans-serif;font-size:1.1rem}

.lb-image-area{flex:1;display:flex;align-items:center;position:relative;overflow:hidden}
.lb-img-wrapper{flex:1;display:flex;align-items:center;justify-content:center;height:100%;padding:20px;position:relative}
.lb-main-img{max-width:100%;max-height:100%;object-fit:contain;border-radius:6px;transition:opacity .2s ease;display:block}
.lb-main-img.lb-fading{opacity:0}

.lb-nav{position:absolute;top:50%;transform:translateY(-50%);background:rgba(0,0,0,.6);border:none;color:#fff;font-size:2rem;width:54px;height:54px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:.2s;z-index:10;line-height:1}
.lb-nav:hover{background:rgba(0,102,51,.85);color:#FFD700}
.lb-prev{left:16px}
.lb-next{right:16px}
.lb-nav:disabled{opacity:.25;cursor:default}

@media(max-width:600px){
  .lb-thumbnail-grid{grid-template-columns:repeat(2,1fr);gap:8px;padding:14px}
  .lb-grid-header{padding:14px 16px 12px}
  .lb-game-title{font-size:1.3rem}
  .lb-nav{width:40px;height:40px;font-size:1.4rem}
  .lb-prev{left:8px}
  .lb-next{right:8px}
  .lb-img-wrapper{padding:10px 60px}
}
</style>

<script>
/* ===== PLAYER MODAL ===== */
function openPlayer(num) {
  const card = document.querySelector(`.pc[data-num="${num}"]`);
  if (!card) return;
  
  const name = card.dataset.name;
  const pos = card.dataset.pos;
  const ht = card.dataset.ht;
  const wt = card.dataset.wt;
  const grad = card.dataset.grad;
  const headshot = card.dataset.headshot;
  const stats = JSON.parse(card.dataset.stats || '{}');
  const batting = stats.batting || {};
  const pitching = stats.pitching || {};
  
  const photoHtml = headshot 
    ? `<img class="modal-photo" src="${headshot}" alt="${name}">`
    : `<div class="modal-placeholder">#${num}</div>`;
  
  document.getElementById('modalHeader').innerHTML = `
    ${photoHtml}
    <div class="modal-info">
      <span class="num">#${num}</span>
      <h2>${name}</h2>
      <div class="details">${pos} &bull; ${ht} &bull; ${wt} lbs &bull; Class of ${grad}</div>
    </div>
  `;
  
  let statsHtml = '';
  const hasBatting = batting.AB > 0;
  const hasPitching = pitching.IP && pitching.IP !== '.0' && pitching.IP !== '0' && parseFloat(pitching.IP) > 0;
  
  if (hasBatting || hasPitching) {
    statsHtml = '<div style="display:flex;flex-direction:column;gap:24px">';
    if (hasBatting) {
      statsHtml += `<div>
        <h3 style="color:var(--gd);margin-bottom:12px;font-family:Oswald">BATTING STATS</h3>
        <div class="stats-grid">
          <div class="stat-box"><div class="val">${batting.BA||'0'}</div><div class="label">AVG</div></div>
          <div class="stat-box"><div class="val">${batting.OBP||'0'}</div><div class="label">OBP</div></div>
          <div class="stat-box"><div class="val">${batting.SLG||'0.00'}</div><div class="label">SLG</div></div>
          <div class="stat-box"><div class="val">${batting.AB||0}</div><div class="label">AB</div></div>
          <div class="stat-box"><div class="val">${batting.R||0}</div><div class="label">Runs</div></div>
          <div class="stat-box"><div class="val">${batting.H||0}</div><div class="label">Hits</div></div>
          <div class="stat-box"><div class="val">${batting.RBI||0}</div><div class="label">RBI</div></div>
          <div class="stat-box"><div class="val">${batting["2B"]||0}</div><div class="label">2B</div></div>
          <div class="stat-box"><div class="val">${batting["3B"]||0}</div><div class="label">3B</div></div>
          <div class="stat-box"><div class="val">${batting.HR||0}</div><div class="label">HR</div></div>
          <div class="stat-box"><div class="val">${batting.BB||0}</div><div class="label">BB</div></div>
          <div class="stat-box"><div class="val">${batting.K||0}</div><div class="label">K</div></div>
        </div></div>`;
    }
    if (hasPitching) {
      statsHtml += `<div>
        <h3 style="color:var(--gd);margin-bottom:12px;font-family:Oswald">PITCHING STATS</h3>
        <div class="stats-grid">
          <div class="stat-box"><div class="val">${pitching.W||0}</div><div class="label">W</div></div>
          <div class="stat-box"><div class="val">${pitching.L||0}</div><div class="label">L</div></div>
          <div class="stat-box"><div class="val">${pitching.SV||0}</div><div class="label">SV</div></div>
          <div class="stat-box"><div class="val">${pitching.IP||'0.0'}</div><div class="label">IP</div></div>
          <div class="stat-box"><div class="val">${pitching.K||0}</div><div class="label">K</div></div>
          <div class="stat-box"><div class="val">${pitching.BB||0}</div><div class="label">BB</div></div>
          <div class="stat-box"><div class="val">${pitching.ERA||'—'}</div><div class="label">ERA</div></div>
          <div class="stat-box"><div class="val">${pitching.WHIP||'—'}</div><div class="label">WHIP</div></div>
        </div></div>`;
    }
    statsHtml += '</div>';
  } else {
    statsHtml = '<p style="color:var(--tm);text-align:center;padding:20px">No stats recorded yet this season</p>';
  }
  
  document.getElementById('modalBody').innerHTML = statsHtml;
  document.getElementById('playerModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closePlayer() {
  document.getElementById('playerModal').classList.remove('active');
  document.body.style.overflow = '';
}

/* ===== GAME LIGHTBOX ===== */
const gamePhotos = ''' + json.dumps({k: {"info": v["info"], "total_photos": v["total_photos"], "thumbnails": v["thumbnails"]} for k, v in game_photos.items()}) + ''';

let lbFolder = null;
let lbThumbs = [];
let lbCurrentIdx = 0;
let lbSwipeStartX = 0;

function openGameGallery(folder) {
  const data = gamePhotos[folder];
  if (!data) return;

  lbFolder = folder;
  lbThumbs = data.thumbnails;
  const info = data.info;
  const total = data.total_photos;
  const shown = lbThumbs.length;
  const resultClass = info.result.includes('W') ? 'color:#2ecc71' : info.result.includes('L') ? 'color:#e74c3c' : 'color:#FFD700';

  // Populate header
  document.getElementById('lbGameTitle').textContent = 'vs ' + info.opponent;
  document.getElementById('lbGameMeta').innerHTML = info.date + ' &bull; <span style="' + resultClass + ';font-weight:700">' + info.result + '</span>';
  document.getElementById('lbPhotoCount').textContent = 'Showing ' + shown + ' of ' + total + ' photos';

  // Populate thumbnail grid
  const grid = document.getElementById('lbThumbnailGrid');
  grid.innerHTML = '';
  lbThumbs.forEach((t, i) => {
    const div = document.createElement('div');
    div.className = 'lb-thumb-item';
    div.setAttribute('aria-label', 'Photo ' + (i+1));
    div.onclick = () => openSinglePhoto(i);
    const img = document.createElement('img');
    img.src = t.thumb;
    img.alt = t.original_name || ('Photo ' + (i+1));
    img.loading = 'lazy';
    div.appendChild(img);
    grid.appendChild(div);
  });

  // Show grid view
  document.getElementById('lbGrid').style.display = 'flex';
  document.getElementById('lbSingle').style.display = 'none';
  document.getElementById('gameLightbox').classList.add('lb-active');
  document.body.style.overflow = 'hidden';

  // Preload all thumbnails
  lbThumbs.forEach(t => { const i = new Image(); i.src = t.thumb; });
}

function showGrid() {
  document.getElementById('lbGrid').style.display = 'flex';
  document.getElementById('lbSingle').style.display = 'none';
}

function openSinglePhoto(idx) {
  lbCurrentIdx = idx;
  document.getElementById('lbGrid').style.display = 'none';
  document.getElementById('lbSingle').style.display = 'flex';
  renderPhoto(idx, false);
}

function renderPhoto(idx, animate) {
  const img = document.getElementById('lbMainImg');
  const src = lbThumbs[idx].thumb;

  if (animate) {
    img.classList.add('lb-fading');
    setTimeout(() => {
      img.src = src;
      img.onload = () => img.classList.remove('lb-fading');
      img.onerror = () => img.classList.remove('lb-fading');
    }, 180);
  } else {
    img.src = src;
  }

  const total = lbThumbs.length;
  document.getElementById('lbCounter').textContent = (idx + 1) + ' / ' + total;
  document.getElementById('lbPrev').disabled = idx === 0;
  document.getElementById('lbNext').disabled = idx === total - 1;

  // Preload adjacent
  if (idx + 1 < total) { const p = new Image(); p.src = lbThumbs[idx+1].thumb; }
  if (idx - 1 >= 0)    { const p = new Image(); p.src = lbThumbs[idx-1].thumb; }
}

function navigatePhoto(dir) {
  const next = lbCurrentIdx + dir;
  if (next < 0 || next >= lbThumbs.length) return;
  lbCurrentIdx = next;
  renderPhoto(lbCurrentIdx, true);
}

function closeLightbox() {
  document.getElementById('gameLightbox').classList.remove('lb-active');
  document.body.style.overflow = '';
  lbFolder = null;
  lbThumbs = [];
}

/* ===== KEYBOARD NAVIGATION ===== */
document.addEventListener('keydown', e => {
  const lb = document.getElementById('gameLightbox');
  const lbActive = lb.classList.contains('lb-active');
  const singleVisible = lbActive && document.getElementById('lbSingle').style.display !== 'none';

  if (e.key === 'Escape') {
    if (singleVisible) { showGrid(); }
    else if (lbActive) { closeLightbox(); }
    else { closePlayer(); }
    return;
  }

  if (singleVisible) {
    if (e.key === 'ArrowLeft')  { e.preventDefault(); navigatePhoto(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); navigatePhoto(1); }
  }
});

/* ===== TOUCH / SWIPE ===== */
const lbImageArea = document.getElementById('lbImageArea');
lbImageArea.addEventListener('touchstart', e => { lbSwipeStartX = e.touches[0].clientX; }, {passive:true});
lbImageArea.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - lbSwipeStartX;
  if (Math.abs(dx) > 50) navigatePhoto(dx < 0 ? 1 : -1);
}, {passive:true});
</script>

</body>
</html>
'''

# Write output
with open('index.html', 'w') as f:
    f.write(html)

# Calculate some stats for reporting
players_with_batting = sum(1 for p in roster if p.get('batting', {}).get('AB', 0) > 0)
players_with_pitching = 0
for p in roster:
    pitching = p.get('pitching', {})
    ip = pitching.get('IP', '0')
    try:
        if ip and ip != '.0' and ip != '0' and float(ip) > 0:
            players_with_pitching += 1
    except:
        pass

players_with_headshots = sum(1 for p in roster if p.get('headshot'))

print(f"Built index.html: {len(html)} chars, {html.count(chr(10))} lines")
print(f"Total players: {len(roster)}")
print(f"Players with batting stats (AB>0): {players_with_batting}")
print(f"Players with pitching stats (IP>0): {players_with_pitching}")
print(f"Players with headshots: {players_with_headshots}")
print(f"Games with photos: {sum(1 for v in game_photo_counts.values() if v > 0)}")
print(f"Team record: {team['record']['overall']}")