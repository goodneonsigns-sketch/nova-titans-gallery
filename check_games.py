#!/usr/bin/env python3
import json

with open('game-photos.json', 'r') as f:
    data = json.load(f)

print(f'Total games: {len(data)}')
print('\nAll game folders:')
for i, key in enumerate(sorted(data.keys())):
    print(f'  {i+1:2d}. {key}')

print('\nChecking for new games:')
for game in ['3-17-26', '3-24-26', '3-26-26']:
    if game in data:
        info = data[game]['info']
        print(f'  ✓ {game}: {info["opponent"]} ({info["result"]}) - {data[game]["total_photos"]} photos')
    else:
        print(f'  ✗ {game}: NOT FOUND')