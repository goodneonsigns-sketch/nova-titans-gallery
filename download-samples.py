import requests, os, json

TOKEN = open("/Users/company-brain/.openclaw/workspace/.secrets/nova-titans.env").read()
TOKEN = [l.split("=",1)[1] for l in TOKEN.strip().split("\n") if l.startswith("DROPBOX_ACCESS_TOKEN=")][0]

base = "/Nova Baseball/Nova Titans"
sample_base = "/Users/company-brain/.openclaw/workspace/projects/nova-titans-gallery/samples"

# Download first 15 and last 15 from root folder (group photos often at start/end)
# Also first 15 from 2-3-26 (practice/first day)
for folder, start_count, end_count in [("", 15, 15), ("2-3-26", 15, 5)]:
    path = f"{base}/{folder}" if folder else base
    label = folder if folder else "root"
    
    r = requests.post("https://api.dropboxapi.com/2/files/list_folder",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"path": path, "recursive": False, "limit": 500})
    
    if r.status_code != 200:
        print(f"Error {folder}: {r.status_code}")
        continue
    
    files = sorted([e for e in r.json()["entries"] if e[".tag"] == "file"], key=lambda x: x["name"])
    print(f"📁 {label}: {len(files)} files")
    
    samples = files[:start_count] + files[-end_count:]
    
    folder_dir = os.path.join(sample_base, f"{label}-group")
    os.makedirs(folder_dir, exist_ok=True)
    
    for f in samples:
        dl = requests.post("https://content.dropboxapi.com/2/files/download",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Dropbox-API-Arg": json.dumps({"path": f["path_lower"]})
            })
        if dl.status_code == 200:
            filepath = os.path.join(folder_dir, f["name"])
            with open(filepath, "wb") as out:
                out.write(dl.content)
            print(f"  ✅ {f['name']}")

print("\nDone!")
