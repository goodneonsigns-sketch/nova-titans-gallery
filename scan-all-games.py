import requests, os, json

TOKEN = open("/Users/company-brain/.openclaw/workspace/.secrets/nova-titans.env").read()
TOKEN = [l.split("=",1)[1] for l in TOKEN.strip().split("\n") if l.startswith("DROPBOX_ACCESS_TOKEN=")][0]

base = "/Nova Baseball/Nova Titans"
sample_base = "/Users/company-brain/.openclaw/workspace/projects/nova-titans-gallery/samples"

# Download dense samples from all remaining game folders
folders = ["2-12", "2-17-26", "2-19-26", "2-23-26", "2-25-26", "2-26-26", "3-5-26"]

for folder in folders:
    path = f"{base}/{folder}"
    folder_dir = os.path.join(sample_base, f"{folder}-dense")
    
    # Skip if already downloaded
    if os.path.exists(folder_dir) and len(os.listdir(folder_dir)) > 10:
        print(f"📁 {folder} already scanned ({len(os.listdir(folder_dir))} files), skipping")
        continue
    
    r = requests.post("https://api.dropboxapi.com/2/files/list_folder",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"path": path, "recursive": False, "limit": 500})
    
    if r.status_code != 200:
        print(f"Error {folder}: {r.status_code}")
        continue
    
    files = sorted([e for e in r.json()["entries"] if e[".tag"] == "file"], key=lambda x: x["name"])
    print(f"📁 {folder}: {len(files)} photos")
    
    os.makedirs(folder_dir, exist_ok=True)
    
    # Every 8th photo
    downloaded = 0
    for i in range(0, len(files), 8):
        f = files[i]
        dl = requests.post("https://content.dropboxapi.com/2/files/download",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Dropbox-API-Arg": json.dumps({"path": f["path_lower"]})
            })
        if dl.status_code == 200:
            filepath = os.path.join(folder_dir, f["name"])
            with open(filepath, "wb") as out:
                out.write(dl.content)
            downloaded += 1
    print(f"  ✅ Downloaded {downloaded} samples")

print("\nAll done!")
