#!/usr/bin/env python3
"""Build the Nova Titans gallery site with clickable player cards, stats, and game galleries."""
import json
import os

# Load data
with open('data.json') as f:
    data = json.load(f)

# Batting stats from browardhighschoolbaseball.com (scraped 2026-03-24)
batting_stats = {
    "Nico Gonzalez": {"AB":10,"R":3,"H":2,"RBI":1,"2B":0,"3B":0,"HR":0,"BB":3,"K":2,"BA":".200","OBP":".385","SLG":".200"},
    "Juan Zapata": {"AB":8,"R":3,"H":2,"RBI":2,"2B":1,"3B":0,"HR":0,"BB":3,"K":1,"BA":".250","OBP":".455","SLG":".375"},
    "Musa Adeoye": {"AB":11,"R":6,"H":6,"RBI":1,"2B":4,"3B":0,"HR":0,"BB":3,"K":1,"BA":".545","OBP":".667","SLG":".909"},
    "Eli Steckler": {"AB":13,"R":4,"H":6,"RBI":6,"2B":3,"3B":0,"HR":0,"BB":2,"K":1,"BA":".462","OBP":".563","SLG":".692"},
    "Colin Correll": {"AB":5,"R":0,"H":1,"RBI":1,"2B":0,"3B":0,"HR":0,"BB":1,"K":2,"BA":".200","OBP":".333","SLG":".200"},
    "Branden Estevez": {"AB":8,"R":0,"H":1,"RBI":1,"2B":0,"3B":0,"HR":0,"BB":2,"K":2,"BA":".125","OBP":".300","SLG":".125"},
    "Anthony Amaya": {"AB":11,"R":2,"H":5,"RBI":3,"2B":1,"3B":0,"HR":0,"BB":3,"K":3,"BA":".455","OBP":".571","SLG":".545"},
    "Aiden Pitti-Shortt": {"AB":13,"R":3,"H":4,"RBI":4,"2B":0,"3B":0,"HR":0,"BB":4,"K":3,"BA":".308","OBP":".471","SLG":".308"},
    "Ricky Relyea": {"AB":11,"R":0,"H":2,"RBI":0,"2B":0,"3B":0,"HR":0,"BB":1,"K":6,"BA":".182","OBP":".250","SLG":".182"},
    "Franklin DeSouza": {"AB":14,"R":7,"H":7,"RBI":4,"2B":0,"3B":0,"HR":0,"BB":2,"K":2,"BA":".500","OBP":".611","SLG":".500"},
    "Josh Bardales": {"AB":3,"R":3,"H":1,"RBI":1,"2B":0,"3B":0,"HR":0,"BB":0,"K":1,"BA":".333","OBP":".333","SLG":".333"},
    "Garrett Schnur": {"AB":6,"R":0,"H":0,"RBI":1,"2B":0,"3B":0,"HR":0,"BB":0,"K":2,"BA":".000","OBP":".000","SLG":".000"},
    "Ryden Biscardi": {"AB":3,"R":0,"H":0,"RBI":0,"2B":0,"3B":0,"HR":0,"BB":0,"K":1,"BA":".000","OBP":".000","SLG":".000"},
    "Aidan Donnellon": {"AB":1,"R":1,"H":0,"RBI":0,"2B":0,"3B":0,"HR":0,"BB":0,"K":1,"BA":".000","OBP":".000","SLG":".000"},
    "Christian English": {"AB":0,"R":1,"H":0,"RBI":0,"2B":0,"3B":0,"HR":0,"BB":0,"K":0,"BA":".000","OBP":".000","SLG":".000"},
}

# Player headshot mapping (jersey# -> best available photo)
player_photos = {
    1: "action2.jpg",    # Nico - batter at plate
    6: None,             # Musa - no good headshot
    9: None,             # Eli
    11: None,            # Joseph
    12: None,            # Jeremy
    14: None,            # Colin
    15: None,            # Brock
    18: None,            # Aidan
    19: None,            # Branden
    20: "action5.jpg",   # Anthony - on the mound
    21: None,            # Aiden PS
    24: None,            # Franklin
    25: None,            # Ricky
    29: None,            # Angelo
    45: None,            # Garrett
}

# Game-to-Dropbox folder mapping
game_folders = {
    "2/10/26": None,       # vs Coral Glades - no folder match
    "2/12/26": "2-12",     # vs South Plantation
    "2/17/26": "2-17-26",  # vs Pompano Beach
    "2/19/26": "2-19-26",  # vs Pine Crest
    "2/23/26": "2-23-26",  # vs CS Charter
    "2/25/26": "2-25-26",  # vs CS Colts
    "2/26/26": "2-26-26",  # vs Coral Glades
    "3/03/26": "3-3-26",   # vs Monarch Knights
    "3/05/26": "3-5-26",   # vs Cooper City
}

# Photo counts per game folder
game_photo_counts = {
    "2-12": 157, "2-17-26": 111, "2-19-26": 44, "2-23-26": 244,
    "2-25-26": 213, "2-26-26": 81, "3-3-26": 294, "3-5-26": 263,
}

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
.pc-photo{{width:56px;height:56px;border-radius:50%;object-fit:cover;border:2px solid var(--g);flex-shrink:0}}
.pc-placeholder{{width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,var(--g),#004d26);border:2px solid #1e2e1e;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-family:'Oswald';font-size:1.4rem;color:var(--gd)}}
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
.modal-photo{{width:100px;height:100px;border-radius:50%;object-fit:cover;border:3px solid var(--gd)}}
.modal-placeholder{{width:100px;height:100px;border-radius:50%;background:rgba(0,0,0,.3);border:3px solid var(--gd);display:flex;align-items:center;justify-content:center;font-family:'Oswald';font-size:3rem;color:var(--gd)}}
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
        
        # Check for headshot
        photo_file = player_photos.get(num)
        if photo_file:
            photo_html = f'<img class="pc-photo" src="{photo_file}" alt="{name}">'
        else:
            photo_html = f'<div class="pc-placeholder">#{num}</div>'
        
        # Check for batting stats
        stats = batting_stats.get(name, {})
        ba_display = stats.get('BA', '')
        ba_html = f'<div class="ba">BA: {ba_display}</div>' if ba_display and ba_display != '.000' else ''
        
        # Build stats data attribute for modal
        stats_json = json.dumps(stats).replace('"', '&quot;') if stats else '{}'
        
        html += f'''<div class="pc" onclick="openPlayer({num})" data-num="{num}" data-name="{name}" data-pos="{pos}" data-ht="{ht}" data-wt="{wt}" data-grad="{year}" data-photo="{photo_file or ''}" data-stats="{stats_json}">
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
    
    folder = game_folders.get(game['date'])
    photo_count = game_photo_counts.get(folder, 0) if folder else 0
    
    photo_section = ''
    if photo_count > 0:
        photo_section = f'<div class="gp"><span class="gp-count">📷 {photo_count} photos</span><br>Click to view & download</div>'
    elif result != 'upcoming':
        photo_section = '<div class="gp">No photos yet</div>'
    else:
        photo_section = '<div class="gp">Game not yet played</div>'
    
    html += f'''<div class="gc {css_class}">
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
html += '<p style="margin-top:12px;font-size:.75rem;color:#555">Nova Titans Baseball &bull; Davie, FL &bull; Updated 2026-03-24</p>\n'
html += '</footer></div></section>\n'

# --- PLAYER MODAL ---
html += '''
<!-- Player Modal -->
<div class="modal-overlay" id="playerModal" onclick="if(event.target===this)closePlayer()">
<div class="modal">
<button class="modal-close" onclick="closePlayer()">&times;</button>
<div class="modal-header" id="modalHeader"></div>
<div class="modal-body" id="modalBody"></div>
</div>
</div>

<script>
const battingStats = ''' + json.dumps(batting_stats) + ''';

function openPlayer(num) {
  const card = document.querySelector(`.pc[data-num="${num}"]`);
  if (!card) return;
  
  const name = card.dataset.name;
  const pos = card.dataset.pos;
  const ht = card.dataset.ht;
  const wt = card.dataset.wt;
  const grad = card.dataset.grad;
  const photo = card.dataset.photo;
  
  const stats = battingStats[name] || {};
  
  // Header
  const photoHtml = photo 
    ? `<img class="modal-photo" src="${photo}" alt="${name}">`
    : `<div class="modal-placeholder">#${num}</div>`;
  
  document.getElementById('modalHeader').innerHTML = `
    ${photoHtml}
    <div class="modal-info">
      <span class="num">#${num}</span>
      <h2>${name}</h2>
      <div class="details">${pos} &bull; ${ht} &bull; ${wt} lbs &bull; Class of ${grad}</div>
    </div>
  `;
  
  // Body - Stats
  let statsHtml = '';
  if (stats.AB > 0) {
    statsHtml = `
      <h3 style="color:var(--gd);margin-bottom:12px;font-family:Oswald">BATTING STATS</h3>
      <div class="stats-grid">
        <div class="stat-box"><div class="val">${stats.BA}</div><div class="label">AVG</div></div>
        <div class="stat-box"><div class="val">${stats.OBP}</div><div class="label">OBP</div></div>
        <div class="stat-box"><div class="val">${stats.SLG}</div><div class="label">SLG</div></div>
        <div class="stat-box"><div class="val">${stats.AB}</div><div class="label">AB</div></div>
        <div class="stat-box"><div class="val">${stats.R}</div><div class="label">Runs</div></div>
        <div class="stat-box"><div class="val">${stats.H}</div><div class="label">Hits</div></div>
        <div class="stat-box"><div class="val">${stats.RBI}</div><div class="label">RBI</div></div>
        <div class="stat-box"><div class="val">${stats["2B"]}</div><div class="label">2B</div></div>
        <div class="stat-box"><div class="val">${stats.BB}</div><div class="label">BB</div></div>
        <div class="stat-box"><div class="val">${stats.K}</div><div class="label">K</div></div>
      </div>
    `;
  } else {
    statsHtml = '<p style="color:var(--tm);text-align:center;padding:20px">No batting stats recorded yet this season</p>';
  }
  
  document.getElementById('modalBody').innerHTML = statsHtml;
  document.getElementById('playerModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closePlayer() {
  document.getElementById('playerModal').classList.remove('active');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closePlayer(); });
</script>

</body>
</html>
'''

# Write output
with open('index.html', 'w') as f:
    f.write(html)

print(f"Built index.html: {len(html)} chars, {html.count(chr(10))} lines")
print(f"Players with stats: {len(batting_stats)}")
print(f"Players with photos: {sum(1 for v in player_photos.values() if v)}")
print(f"Games with photos: {sum(1 for v in game_photo_counts.values() if v > 0)}")
