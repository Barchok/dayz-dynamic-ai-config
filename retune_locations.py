#!/usr/bin/env python3
"""Rebuild the Location layer against the real trigger mechanic.

Spatial_Chance is rolled in Trigger.EOnFrame -> UpdateInsiders -> StayStart ->
OnStayStartServerEvent -> SpawnCheck, i.e. ONCE PER SERVER FRAME, ungated. So
the roll rate is the server's frame rate, not a timer. Chances are therefore
derived from a target per-visit probability and a nominal frame rate.

Two things are tuned independently:

  Spatial_Chance  -> how likely a POI is occupied during a NORMAL visit.
                     Derived, frame-rate dependent, tolerant of ~20% drift.
  MinCount/MaxCount and the variant list
                  -> the CEILING: the most a POI can ever put on the field.
                     Structural, completely frame-rate independent. This is
                     what stops a long firefight escalating, because standing
                     in the trigger re-rolls every frame indefinitely.

Spatial_Timer is the third dial: a trigger on cooldown cannot fire at any
frame rate, so it is the honest "this POI is dead right now" control.
"""
import json
import math

F = "/Users/michiel/git/dayz-dynamic-ai-config/SpatialSettings.json"

R = 50.0        # nominal server frame rate (small-scale server)
T_VISIT = 300.0  # a normal approach + loot + leave through a ~500m trigger
T_FIGHT = 900.0  # a sustained engagement / camping the POI

CIV, SUR, RAID = "CivilianTierLoadout.json", "SurvivorTierLoadout.json", "RaiderLoadout.json"
HUNT, GORKA, SOV = "HunterTierLoadout.json", "GorkaMilitaryLoadout.json", "SovietMilitaryLoadout.json"
EAST, WEST, ELITE = "EastMilitaryLoadout.json", "WestMilitaryLoadout.json", "EliteTierLoadout.json"
HAZ, SNIPER = "HazmatLoadout.json", "GhillieSniperLoadout.json"

# archetype -> variants: (loadout, faction, hunt, min, max, weight, accmin, accmax, timer)
# weight = share of that POI's occupancy hazard. Counts set the ceiling.
ARCH = {
    "TOP_MIL": [
        (ELITE, "West",        4, 1, 2, 1.0, 0.52, 0.80, 55),
        (WEST,  "West",        4, 1, 3, 1.2, 0.48, 0.74, 50),
        (GORKA, "Mercenaries", 5, 1, 2, 0.9, 0.44, 0.70, 48),
        (EAST,  "East",        6, 1, 1, 0.5, 0.46, 0.72, 60),
    ],
    "MIL": [
        (WEST,  "West",        4, 1, 2, 1.0, 0.46, 0.72, 50),
        (SOV,   "Mercenaries", 4, 1, 2, 1.1, 0.42, 0.66, 48),
        (GORKA, "Mercenaries", 5, 1, 1, 0.8, 0.42, 0.66, 48),
        (RAID,  "Raiders",     5, 1, 1, 0.6, 0.36, 0.60, 45),
    ],
    "EAST_MIL": [
        (EAST,  "East",        4, 1, 2, 1.2, 0.48, 0.74, 52),
        (SOV,   "East",        4, 1, 2, 1.0, 0.42, 0.66, 48),
        (HUNT,  "Mercenaries", 6, 1, 2, 0.6, 0.42, 0.66, 45),
    ],
    "NBC": [
        (HAZ,   "Mercenaries", 4, 1, 2, 1.0, 0.45, 0.70, 60),
        (ELITE, "West",        4, 1, 2, 0.3, 0.50, 0.78, 75),
    ],
    "TOWN": [
        (RAID,  "Raiders",     5, 1, 2, 1.1, 0.34, 0.58, 45),
        (SUR,   "Raiders",     5, 1, 1, 1.0, 0.30, 0.54, 42),
        (HUNT,  "Mercenaries", 5, 1, 1, 0.5, 0.38, 0.62, 48),
        (CIV,   "Raiders",     5, 1, 1, 0.6, 0.24, 0.48, 40),
    ],
    "COAST_TOWN": [
        (CIV,   "Raiders",     5, 1, 2, 1.2, 0.24, 0.48, 40),
        (SUR,   "Raiders",     5, 1, 1, 1.0, 0.30, 0.54, 42),
        (RAID,  "Raiders",     5, 1, 1, 0.7, 0.34, 0.58, 45),
    ],
    "WILD": [
        (HUNT,  "Mercenaries", 6, 1, 2, 1.0, 0.42, 0.66, 48),
        (GORKA, "Mercenaries", 5, 1, 1, 0.7, 0.42, 0.66, 50),
        (RAID,  "Raiders",     5, 1, 1, 0.7, 0.36, 0.60, 45),
    ],
}

# tag -> (archetype, x, y, z, radius, busy, has_sniper)
POIS = [
    ("P01", "TOP_MIL",     4600, 200, 10400, 560, 2.4, True),
    ("P02", "TOP_MIL",     1700, 340, 13800, 534, 1.5, True),
    ("P03", "MIL",         3800, 250,  8700, 510, 1.8, True),
    ("P04", "EAST_MIL",   11800, 150, 12300, 522, 1.3, True),
    ("P05", "MIL",         2600, 210,  5400, 496, 0.9, False),
    ("P06", "MIL",         4900,  20,  2500, 470, 1.6, True),
    ("P07", "NBC",         2050, 130,  2350, 420, 0.5, False),
    ("P08", "NBC",        13100,  10, 14100, 420, 0.35, False),
    ("P09", "TOWN",       12000,  30,  9000, 496, 1.7, False),
    ("P10", "TOWN",        6100, 240,  7700, 470, 2.0, False),
    ("P11", "EAST_MIL",   11900,  60, 14300, 496, 1.1, True),
    ("P12", "WILD",        3700, 300,  6000, 470, 0.8, False),
    ("P13", "MIL",         7500, 200, 14500, 510, 0.6, True),
    ("P14", "WILD",        2000, 260,  7300, 470, 0.45, False),
    ("P15", "COAST_TOWN",  6600,  25,  2500, 496, 2.2, False),
    ("P16", "COAST_TOWN", 10400,  20,  2200, 496, 1.9, False),
    ("P17", "WILD",        8800, 180, 11200, 470, 0.4, False),
    ("P18", "TOWN",        9000, 150,  8600, 470, 1.2, False),
]

SNIPER_PER_VISIT = 0.06   # he is meant to be a story, not a fixture


def occupancy_target(busy):
    """Chance a POI has produced at least one patrol during a normal visit."""
    return min(0.72, 1.0 - math.exp(-0.47 * busy))


def chance_from_hazard(h):
    """Per-frame chance giving hazard h over T_VISIT at R frames/sec."""
    return 1.0 - math.exp(-h / (R * T_VISIT))


def ring(x, y, z, r, n=4, phase=0.0):
    return [[round(x + r * math.cos(phase + i * 2 * math.pi / n), 1), float(y),
             round(z + r * math.sin(phase + i * 2 * math.pi / n), 1)] for i in range(n)]


def loc(name, pos, radius, loadout, faction, mn, mx, hunt, amin, amax, chance,
        timer, spawn_r, phase):
    x, y, z = pos
    return {
        "Spatial_Name": name,
        "Spatial_TriggerRadius": float(radius),
        "Spatial_ZoneLoadout": loadout,
        "Spatial_MinCount": mn,
        "Spatial_MaxCount": mx,
        "Spatial_HuntMode": hunt,
        "Spatial_Faction": faction,
        "Spatial_Lootable": 1,
        "Spatial_Chance": round(chance, 8),
        "Spatial_MinAccuracy": amin,
        "Spatial_MaxAccuracy": amax,
        "Spatial_Timer": float(timer),
        "Spatial_SpawnMode": 0,
        "Spatial_UnlimitedReload": 0,
        "Spatial_TriggerPosition": [float(x), float(y), float(z)],
        "Spatial_SpawnPosition": ring(x, y, z, spawn_r, 4, phase),
    }


d = json.load(open(F))
locations = []
report = []

for tag, arch, x, y, z, rad, busy, has_sniper in POIS:
    variants = ARCH[arch]
    target = occupancy_target(busy)
    H = -math.log(1.0 - target)
    wsum = sum(v[5] for v in variants)

    hazards = []
    for i, (lo, fac, hunt, mn, mx, w, amin, amax, tmr) in enumerate(variants):
        h = H * w / wsum
        hazards.append(h)
        locations.append(loc(f"{tag}_{i+1}", (x, y, z), rad, lo, fac, mn, mx, hunt,
                             amin, amax, chance_from_hazard(h), tmr,
                             60 + i * 25, i * 0.7))

    if has_sniper:
        hs = -math.log(1.0 - SNIPER_PER_VISIT)
        hazards.append(hs)
        locations.append(loc(f"{tag}_SNIPER", (x, y, z), rad, SNIPER, "Mercenaries",
                             1, 1, 4, 0.50, 0.72, chance_from_hazard(hs), 90,
                             170, 2.9))

    ceiling = sum(v[4] for v in variants) + (1 if has_sniper else 0)
    report.append((tag, arch, busy, target, hazards, ceiling))

d["Location"] = locations
json.dump(d, open(F, "w"), indent=1)


def p_occupied(hazards, T):
    """P(at least one variant has fired) after T seconds inside."""
    return 1.0 - math.exp(-sum(hazards) * T / T_VISIT)


def expected_ai(tag, arch, hazards, T, has_sniper):
    variants = list(ARCH[arch])
    if has_sniper:
        variants = variants + [(None, None, 4, 1, 1, 0, 0, 0, 90)]
    e = 0.0
    for (v, h) in zip(variants, hazards):
        pf = 1.0 - math.exp(-h * T / T_VISIT)
        e += pf * (v[3] + v[4]) / 2.0
    return e


print(f"Locations: {len(locations)} across {len(POIS)} POIs")
print(f"nominal R = {R:.0f} fps, normal visit = {T_VISIT:.0f}s, long fight = {T_FIGHT:.0f}s\n")
print(f"  {'POI':5s} {'type':11s} {'busy':>5s} {'occupied':>9s} {'E[AI]':>6s} "
      f"{'occupied':>9s} {'E[AI]':>6s} {'ceiling':>8s}")
print(f"  {'':5s} {'':11s} {'':>5s} {'@5min':>9s} {'@5min':>6s} "
      f"{'@15min':>9s} {'@15min':>6s} {'':>8s}")
for tag, arch, busy, target, hz, ceiling in sorted(report, key=lambda r: -r[2]):
    hs = next(p[7] for p in POIS if p[0] == tag)
    print(f"  {tag:5s} {arch:11s} {busy:5.2f} {p_occupied(hz, T_VISIT)*100:8.0f}% "
          f"{expected_ai(tag, arch, hz, T_VISIT, hs):6.1f} "
          f"{p_occupied(hz, T_FIGHT)*100:8.0f}% "
          f"{expected_ai(tag, arch, hz, T_FIGHT, hs):6.1f} {ceiling:8d}")

print(f"\n  map-wide ceiling if every POI maxed at once: "
      f"{sum(r[5] for r in report)} (MaxAI caps concurrent patrols at {d.get('MaxAI')})")

print("\nFrame-rate sensitivity (P(occupied) on a normal visit):")
print(f"  {'POI':5s} {'@40fps':>7s} {'@50fps':>7s} {'@60fps':>7s}")
for tag, arch, busy, target, hz, ceiling in sorted(report, key=lambda r: -r[2])[:6]:
    row = []
    for rate in (40.0, 50.0, 60.0):
        # chances were baked at R; actual hazard scales linearly with real fps
        row.append((1.0 - math.exp(-sum(hz) * rate / R)) * 100)
    print(f"  {tag:5s} {row[0]:6.0f}% {row[1]:6.0f}% {row[2]:6.0f}%")
