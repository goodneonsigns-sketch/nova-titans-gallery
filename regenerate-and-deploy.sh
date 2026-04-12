#!/usr/bin/env bash
# regenerate-and-deploy.sh
# Refreshes all Dropbox temporary links, rebuilds the site, and pushes to GitHub.
# Run this script every 3-4 hours (temp links expire after 4 hours) OR
# whenever new photos are added to Dropbox.
#
# Usage:
#   ./regenerate-and-deploy.sh
#   ./regenerate-and-deploy.sh --no-generate    # skip link generation (use cached)
#   ./regenerate-and-deploy.sh --no-push        # build only, don't push

set -e
cd "$(dirname "$0")"

SKIP_GENERATE=false
SKIP_PUSH=false

for arg in "$@"; do
    case $arg in
        --no-generate) SKIP_GENERATE=true ;;
        --no-push)     SKIP_PUSH=true ;;
    esac
done

echo "=== Nova Titans Gallery — Regenerate & Deploy ==="
echo "$(date)"
echo ""

# Step 1: Generate fresh Dropbox temporary links
if [ "$SKIP_GENERATE" = false ]; then
    echo "📥 Generating fresh Dropbox temporary links (this takes ~6 minutes)..."
    python3 generate-dropbox-links.py --reset --concurrency 6
    echo ""
fi

# Step 2: Build the site
echo "🔨 Building site..."
python3 build-site.py
echo ""

# Step 3: Push to GitHub
if [ "$SKIP_PUSH" = false ]; then
    echo "🚀 Pushing to GitHub..."
    git add index.html dropbox-links.json generate-dropbox-links.py regenerate-and-deploy.sh build-site.py
    git commit -m "Refresh: all $(python3 -c "import json; d=json.load(open('dropbox-links.json')); print(sum(len(v) for v in d.values()))") Dropbox photo links — $(date '+%Y-%m-%d %H:%M')" || echo "(nothing to commit)"
    git push
    echo ""
fi

echo "✅ Done! Site updated with all game photos from Dropbox."
echo "⚠️  Note: Temporary links expire in ~4 hours. Run this script again to refresh."
