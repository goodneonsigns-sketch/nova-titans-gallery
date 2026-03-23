import requests, os, json

TOKEN = open("/Users/company-brain/.openclaw/workspace/.secrets/nova-titans.env").read()
TOKEN = [l.split("=",1)[1] for l in TOKEN.strip().split("\n") if l.startswith("DROPBOX_ACCESS_TOKEN=")][0]

base = "/Nova Baseball/Nova Titans"
picks_dir = "/Users/company-brain/.openclaw/workspace/projects/nova-titans-gallery/player-picks"
os.makedirs(picks_dir, exist_ok=True)

# Best action shots identified during scan - download the specific files
# Format: (folder, filename_pattern, player_number)
# We'll download nearby photos from the sequences where we found each player
targets = [
    # Nico #1 - multiple games
    ("root", None, 1, 20),  # root folder, first 20 (intro lineup has #1)
    # #20 Anthony Amaya - pitcher, lots of shots in 3-3-26
    ("3-3-26", None, 20, 5),  # first 5
    # #29 Angelo Olmeda - pitcher in root
    # Already have root samples
    # #25 Ricky Relyea - batting
    # Already identified in 2-12
    # #45 Garrett Schnur - batting 3-3-26
    # Already have
]

# Actually, let me just download the SPECIFIC best photos we identified
# For player cards, I need one good action shot per player
# Let me grab specific ranges from games where we found players

# From root: DSC03776 (pitcher in green - GREAT profile), DSC03788 (pitcher on mound - GREAT)
# From 3-3-26: DSC06364 (#20 pitching), DSC06417 (#21 swing), DSC06484 (#24 contact)
# From 3-3-26: DSC06714 (#45 batting)
# From 2-25-26: DSC05867 (#2 batting back view)
# From 2-12: we found #25, #18, #1, #35

specific_files = [
    # Root - team intro sequence + pitchers
    "/Nova Baseball/Nova Titans/DSC03415.jpg",  # #1 in lineup
    "/Nova Baseball/Nova Titans/DSC03417.jpg",  # best group lineup
    "/Nova Baseball/Nova Titans/DSC03430.jpg",  # full team (hero)
    "/Nova Baseball/Nova Titans/DSC03774.jpg",  # dugout group
    "/Nova Baseball/Nova Titans/DSC03776.jpg",  # pitcher GREAT
    "/Nova Baseball/Nova Titans/DSC03788.jpg",  # pitcher on mound GREAT
    "/Nova Baseball/Nova Titans/DSC03789.jpg",  # pitcher follow through
    "/Nova Baseball/Nova Titans/DSC03791.jpg",  # #29 pitcher
    # 3-3-26 Monarch Knights game - best action
    "/Nova Baseball/Nova Titans/3-3-26/DSC06346.JPG",  # fielding
    "/Nova Baseball/Nova Titans/3-3-26/DSC06364.JPG",  # #20 pitcher
    "/Nova Baseball/Nova Titans/3-3-26/DSC06417.JPG",  # #21 hitting
    "/Nova Baseball/Nova Titans/3-3-26/DSC06427.JPG",  # #6 at plate
    "/Nova Baseball/Nova Titans/3-3-26/DSC06484.JPG",  # #24 contact
    "/Nova Baseball/Nova Titans/3-3-26/DSC06530.JPG",  # scoring play
    "/Nova Baseball/Nova Titans/3-3-26/DSC06542.JPG",  # #9 batting
    "/Nova Baseball/Nova Titans/3-3-26/DSC06598.JPG",  # batter facing camera GREAT
    "/Nova Baseball/Nova Titans/3-3-26/DSC06611.JPG",  # batter facing camera GREAT
    "/Nova Baseball/Nova Titans/3-3-26/DSC06714.JPG",  # #45 batting
    "/Nova Baseball/Nova Titans/3-3-26/DSC06745.JPG",  # #15 pitching
]

for filepath in specific_files:
    filename = filepath.split("/")[-1]
    dl = requests.post("https://content.dropboxapi.com/2/files/download",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Dropbox-API-Arg": json.dumps({"path": filepath.lower()})
        })
    if dl.status_code == 200:
        out_path = os.path.join(picks_dir, filename)
        with open(out_path, "wb") as out:
            out.write(dl.content)
        print(f"✅ {filename} ({len(dl.content)/1024:.0f} KB)")
    else:
        print(f"❌ {filename}: {dl.status_code}")

print(f"\nDone! {len(os.listdir(picks_dir))} files in player-picks/")
