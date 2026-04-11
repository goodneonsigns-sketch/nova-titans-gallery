#!/usr/bin/env python3
"""Parse MaxPreps stats HTML and update data.json with accurate player stats."""

import json
import re
from html.parser import HTMLParser

# Read the files
with open('maxpreps-stats.html', 'r') as f:
    html = f.read()

with open('data.json', 'r') as f:
    data = json.load(f)

# ─── Manual extraction from HTML (already fully read) ───────────────────────
# Data extracted directly from the MaxPreps HTML tables.

# Batting stats: jersey# -> {GP, Avg, PA, AB, R, H, RBI, 2B, 3B, HR}
batting_table1 = {
    1:  {'GP':13, 'Avg':'.167', 'PA':33,  'AB':30, 'R':6,  'H':5,  'RBI':3,  '2B':0, '3B':0, 'HR':0},
    2:  {'GP':12, 'Avg':'.227', 'PA':30,  'AB':22, 'R':4,  'H':5,  'RBI':3,  '2B':1, '3B':0, 'HR':0},
    6:  {'GP':15, 'Avg':'.421', 'PA':51,  'AB':38, 'R':16, 'H':16, 'RBI':5,  '2B':5, '3B':0, 'HR':0},
    8:  {'GP':11, 'Avg':'.214', 'PA':18,  'AB':14, 'R':2,  'H':3,  'RBI':0,  '2B':1, '3B':0, 'HR':0},
    9:  {'GP':15, 'Avg':'.275', 'PA':46,  'AB':40, 'R':6,  'H':11, 'RBI':9,  '2B':5, '3B':0, 'HR':0},
    10: {'GP':7,  'Avg':'.000', 'PA':1,   'AB':1,  'R':0,  'H':0,  'RBI':0,  '2B':0, '3B':0, 'HR':0},
    14: {'GP':9,  'Avg':'.238', 'PA':24,  'AB':21, 'R':2,  'H':5,  'RBI':4,  '2B':1, '3B':0, 'HR':0},
    18: {'GP':5,  'Avg':'.000', 'PA':3,   'AB':3,  'R':1,  'H':0,  'RBI':0,  '2B':0, '3B':0, 'HR':0},
    19: {'GP':12, 'Avg':'.200', 'PA':27,  'AB':20, 'R':4,  'H':4,  'RBI':2,  '2B':0, '3B':0, 'HR':0},
    20: {'GP':15, 'Avg':'.389', 'PA':52,  'AB':36, 'R':7,  'H':14, 'RBI':8,  '2B':4, '3B':0, 'HR':0},
    21: {'GP':15, 'Avg':'.256', 'PA':51,  'AB':39, 'R':8,  'H':10, 'RBI':10, '2B':0, '3B':0, 'HR':0},
    24: {'GP':15, 'Avg':'.298', 'PA':54,  'AB':47, 'R':11, 'H':14, 'RBI':9,  '2B':0, '3B':0, 'HR':0},
    25: {'GP':10, 'Avg':'.167', 'PA':27,  'AB':24, 'R':0,  'H':4,  'RBI':0,  '2B':0, '3B':0, 'HR':0},
    27: {'GP':6,  'Avg':'.500', 'PA':4,   'AB':4,  'R':3,  'H':2,  'RBI':2,  '2B':0, '3B':0, 'HR':0},
    32: {'GP':8,  'Avg':'.000', 'PA':4,   'AB':4,  'R':1,  'H':0,  'RBI':0,  '2B':0, '3B':0, 'HR':0},
    33: {'GP':5,  'Avg':'.000', 'PA':8,   'AB':6,  'R':0,  'H':0,  'RBI':1,  '2B':0, '3B':0, 'HR':0},
    41: {'GP':8,  'Avg':'',     'PA':0,   'AB':0,  'R':4,  'H':0,  'RBI':0,  '2B':0, '3B':0, 'HR':0},  # #41 is Christian English in MaxPreps
    45: {'GP':13, 'Avg':'.071', 'PA':16,  'AB':14, 'R':0,  'H':1,  'RBI':2,  '2B':0, '3B':0, 'HR':0},
}

# Note: MaxPreps #41 = Christian English (in data.json he is #4)
# MaxPreps jersey numbers differ from data.json in some cases
# We'll map by name where jersey doesn't match

# Second batting table: jersey# -> {BB, K, OBP, SLG, OPS}
batting_table2 = {
    1:  {'BB':3,  'K':7,  'OBP':'.242', 'SLG':'.167', 'OPS':'.409'},
    2:  {'BB':7,  'K':5,  'OBP':'.433', 'SLG':'.273', 'OPS':'.706'},
    6:  {'BB':5,  'K':5,  'OBP':'.569', 'SLG':'.553', 'OPS':'1.122'},
    8:  {'BB':3,  'K':1,  'OBP':'.389', 'SLG':'.286', 'OPS':'.675'},
    9:  {'BB':4,  'K':14, 'OBP':'.370', 'SLG':'.400', 'OPS':'.770'},
    10: {'BB':0,  'K':1,  'OBP':'.000', 'SLG':'.000', 'OPS':'.000'},
    14: {'BB':3,  'K':6,  'OBP':'.333', 'SLG':'.286', 'OPS':'.619'},
    18: {'BB':0,  'K':2,  'OBP':'.000', 'SLG':'.000', 'OPS':'.000'},
    19: {'BB':4,  'K':5,  'OBP':'.385', 'SLG':'.200', 'OPS':'.585'},
    20: {'BB':11, 'K':4,  'OBP':'.540', 'SLG':'.500', 'OPS':'1.040'},
    21: {'BB':9,  'K':11, 'OBP':'.408', 'SLG':'.256', 'OPS':'.664'},
    24: {'BB':5,  'K':12, 'OBP':'.389', 'SLG':'.298', 'OPS':'.687'},
    25: {'BB':2,  'K':8,  'OBP':'.259', 'SLG':'.167', 'OPS':'.426'},
    27: {'BB':0,  'K':1,  'OBP':'.500', 'SLG':'.500', 'OPS':'1.000'},
    32: {'BB':0,  'K':2,  'OBP':'.000', 'SLG':'.000', 'OPS':'.000'},
    33: {'BB':0,  'K':3,  'OBP':'.125', 'SLG':'.000', 'OPS':'.125'},
    41: {'BB':0,  'K':0,  'OBP':'',     'SLG':'',     'OPS':''},
    45: {'BB':1,  'K':5,  'OBP':'.133', 'SLG':'.071', 'OPS':'.204'},
}

# Baserunning: jersey# -> {SB}
baserunning = {
    1:  {'SB':3},
    2:  {'SB':3},
    6:  {'SB':11},
    8:  {'SB':0},
    9:  {'SB':1},
    10: {'SB':0},
    14: {'SB':1},
    18: {'SB':0},
    19: {'SB':6},
    20: {'SB':4},
    21: {'SB':8},
    24: {'SB':7},
    25: {'SB':1},
    27: {'SB':6},
    32: {'SB':1},
    33: {'SB':0},
    41: {'SB':1},
    45: {'SB':0},
}

# Pitching table 1: jersey# -> {ERA, W, L, APP, SV}
pitching_table1 = {
    3:  {'ERA':'5.60',  'W':0, 'L':0, 'APP':4, 'SV':0},
    10: {'ERA':'7.00',  'W':0, 'L':3, 'APP':6, 'SV':1},
    11: {'ERA':'3.32',  'W':0, 'L':0, 'APP':3, 'SV':0},
    15: {'ERA':'8.40',  'W':0, 'L':1, 'APP':4, 'SV':0},
    20: {'ERA':'6.79',  'W':3, 'L':3, 'APP':8, 'SV':0},
    24: {'ERA':'6.30',  'W':0, 'L':1, 'APP':2, 'SV':1},
    29: {'ERA':'0.00',  'W':0, 'L':0, 'APP':1, 'SV':0},
    32: {'ERA':'',      'W':0, 'L':0, 'APP':1, 'SV':0},
    34: {'ERA':'2.86',  'W':0, 'L':0, 'APP':5, 'SV':0},
    45: {'ERA':'10.26', 'W':1, 'L':2, 'APP':6, 'SV':0},
}

# Pitching table 2: jersey# -> {IP, H, R, ER, BB, K}
pitching_table2 = {
    3:  {'IP':'5.0',  'H':7,  'R':5,  'ER':4,  'BB':3,  'K':0},
    10: {'IP':'18.0', 'H':23, 'R':21, 'ER':18, 'BB':17, 'K':13},
    11: {'IP':'6.1',  'H':2,  'R':4,  'ER':3,  'BB':7,  'K':3},
    15: {'IP':'5.0',  'H':5,  'R':8,  'ER':6,  'BB':4,  'K':4},
    20: {'IP':'33.0', 'H':57, 'R':44, 'ER':32, 'BB':14, 'K':22},
    24: {'IP':'3.1',  'H':2,  'R':3,  'ER':3,  'BB':1,  'K':4},
    29: {'IP':'3.0',  'H':1,  'R':3,  'ER':0,  'BB':1,  'K':4},
    32: {'IP':'',     'H':0,  'R':0,  'ER':0,  'BB':0,  'K':0},
    34: {'IP':'7.1',  'H':7,  'R':6,  'ER':3,  'BB':5,  'K':4},
    45: {'IP':'14.1', 'H':29, 'R':26, 'ER':21, 'BB':9,  'K':10},
}

# ─── Name mapping for MaxPreps jersey # vs data.json jersey # ───────────────
# MaxPreps uses #41 for Christian English, but data.json has him as #4
# All other jerseys match between the two datasets

maxpreps_to_datajson_jersey = {
    41: 4,  # Christian English: MaxPreps #41 -> data.json #4
}

def get_datajson_jersey(mp_jersey):
    return maxpreps_to_datajson_jersey.get(mp_jersey, mp_jersey)

# ─── Build lookup by jersey number for data.json ────────────────────────────
jersey_to_player = {}
for p in data['roster']:
    jersey_to_player[p['number']] = p

# ─── Update batting stats ────────────────────────────────────────────────────
updated_batting = []
for mp_jersey, b1 in batting_table1.items():
    dj_jersey = get_datajson_jersey(mp_jersey)
    player = jersey_to_player.get(dj_jersey)
    if not player:
        print(f"  WARNING: No data.json player for MaxPreps jersey #{mp_jersey} (mapped to #{dj_jersey})")
        continue

    b2 = batting_table2.get(mp_jersey, {})
    sb = baserunning.get(mp_jersey, {}).get('SB', 0)

    avg = b1.get('Avg', '')
    if avg and avg != '.000' and avg != '.':
        ba_display = avg
    elif avg == '.000':
        ba_display = '.000'
    else:
        ba_display = ''

    player['batting'] = {
        'GP': b1['GP'],
        'AB': b1['AB'],
        'R':  b1['R'],
        'H':  b1['H'],
        'RBI': b1['RBI'],
        '2B': b1['2B'],
        '3B': b1['3B'],
        'HR': b1['HR'],
        'BB': b2.get('BB', 0),
        'K':  b2.get('K', 0),
        'SB': sb,
        'BA': ba_display,
        'OBP': b2.get('OBP', ''),
        'SLG': b2.get('SLG', ''),
        'OPS': b2.get('OPS', ''),
    }
    updated_batting.append(player['name'])

# ─── Update pitching stats ───────────────────────────────────────────────────
updated_pitching = []
for mp_jersey, p1 in pitching_table1.items():
    dj_jersey = get_datajson_jersey(mp_jersey)
    player = jersey_to_player.get(dj_jersey)
    if not player:
        print(f"  WARNING: No data.json player for MaxPreps pitcher jersey #{mp_jersey} (mapped to #{dj_jersey})")
        continue

    p2 = pitching_table2.get(mp_jersey, {})
    ip_raw = p2.get('IP', '')
    # Normalize IP: MaxPreps shows "5" for 5.0 innings, "18" for 18.0, etc.
    if ip_raw and ip_raw != '':
        try:
            ip_float = float(ip_raw)
            # If it's a whole number, add ".0"
            if '.' not in str(ip_raw):
                ip_display = f"{int(ip_float)}.0"
            else:
                ip_display = ip_raw
        except:
            ip_display = ip_raw
    else:
        ip_display = '.0'

    player['pitching'] = {
        'ERA': p1.get('ERA', ''),
        'W':   p1.get('W', 0),
        'L':   p1.get('L', 0),
        'APP': p1.get('APP', 0),
        'SV':  p1.get('SV', 0),
        'IP':  ip_display,
        'H':   p2.get('H', 0),
        'R':   p2.get('R', 0),
        'ER':  p2.get('ER', 0),
        'BB':  p2.get('BB', 0),
        'K':   p2.get('K', 0),
        # Keep WHIP blank (not in MaxPreps printable)
        'WHIP': '',
    }
    updated_pitching.append(player['name'])

# ─── Reset pitching for players not in pitcher list ─────────────────────────
pitcher_dj_jerseys = {get_datajson_jersey(j) for j in pitching_table1.keys()}
for p in data['roster']:
    if p['number'] not in pitcher_dj_jerseys:
        # Keep their existing pitching dict structure but clear it
        p['pitching'] = {
            'ERA': '',
            'W': 0,
            'L': 0,
            'APP': 0,
            'SV': 0,
            'IP': '.0',
            'H': 0,
            'R': 0,
            'ER': 0,
            'BB': 0,
            'K': 0,
            'WHIP': '',
        }

# ─── Reset batting for players not in batting list ──────────────────────────
batting_dj_jerseys = {get_datajson_jersey(j) for j in batting_table1.keys()}
for p in data['roster']:
    if p['number'] not in batting_dj_jerseys:
        p['batting'] = {
            'GP': 0,
            'AB': 0,
            'R': 0,
            'H': 0,
            'RBI': 0,
            '2B': 0,
            '3B': 0,
            'HR': 0,
            'BB': 0,
            'K': 0,
            'SB': 0,
            'BA': '',
            'OBP': '',
            'SLG': '',
            'OPS': '',
        }

# ─── Save updated data.json ──────────────────────────────────────────────────
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Updated batting stats for: {', '.join(updated_batting)}")
print(f"✅ Updated pitching stats for: {', '.join(updated_pitching)}")
print(f"✅ data.json saved successfully")
print(f"\nSummary:")
print(f"  Batters updated: {len(updated_batting)}")
print(f"  Pitchers updated: {len(updated_pitching)}")
