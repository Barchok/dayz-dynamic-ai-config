#!/usr/bin/env python3
"""Build the slot/attachment map that `validate.py --slots` needs.

types.xml says nothing about where an item can go, so a loadout can put a class
somewhere that cannot accept it. The engine's CreateAttachment(Ex) just returns
null: the entry silently never spawns, and the only symptom is a slot that comes
out emptier than its chances suggest. Two distinct forms of this:

  * wrong worn slot -- GorkaHelmetVisor is a Glass-slot attachment on
    GorkaHelmet, and sat dead in Headgear.
  * wrong optic -- an optic only mounts if its inventorySlot appears in the
    weapon's attachments[]. M16A2 has no optics category at all, so any optic
    on it is a no-op.

Authoritative fields in CfgVehicles/CfgWeapons:
  inventorySlot[]  on wearables and attachments (declared on *_ColorBase and
                   inherited, so the inheritance chain is walked)
  attachments[]    on weapons -- the attachment categories it accepts
  magazines[]      on weapons -- accepted magazine classes
  chamberableFrom[] on weapons -- accepted loose ammo

Source is an unpacked mirror of the vanilla configs, which saves unpacking the
game PBOs with DayZ Tools. Output is Bohemia's data, so it lands in the
gitignored snapshot dir next to types.xml and is never committed. This script
is original work and is.

    ./fetch_slotmap.py                       # -> ExpansionMod-Source/slotmap.json
    ./validate.py --types ExpansionMod-Source/types.xml \
                  --slots ExpansionMod-Source/slotmap.json
"""
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = "ravmustang/DayZ_SA_ClassName_Dump"
RAW = f"https://raw.githubusercontent.com/{REPO}/master/CurrentConfigs"
API = f"https://api.github.com/repos/{REPO}/contents/CurrentConfigs"

# wearables + attachments: flat config.cpp per folder
FLAT = [
    "characters_backpacks", "characters_belts", "characters_data",
    "characters_glasses", "characters_gloves", "characters_headgear",
    "characters_masks", "characters_pants", "characters_shoes",
    "characters_tops", "characters_vests", "gear_containers",
    "weapons_attachments_light", "weapons_attachments_magazine",
    "weapons_attachments_muzzle", "weapons_attachments_optics",
    "weapons_attachments_support",
]
# weapons: one subfolder per weapon, the top-level config.cpp is a stub
NESTED = ["weapons_firearms", "weapons_pistols", "weapons_shotguns",
          "weapons_launchers", "weapons_melee", "weapons_archery"]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "ExpansionMod-Source", "slotmap.json")

DECL = re.compile(r"class\s+(\w+)\s*(?::\s*(\w+))?\s*\{")
ARRAYS = {
    "slot": re.compile(r"inventorySlot\[\]\s*=\s*\{([^}]*)\}"),
    "attachments": re.compile(r"attachments\[\]\s*=\s*\{([^}]*)\}"),
    "magazines": re.compile(r"magazines\[\]\s*=\s*\{([^}]*)\}"),
    "ammo": re.compile(r"chamberableFrom\[\]\s*=\s*\{([^}]*)\}"),
    # fire modes drive how threatening a gun is in AI hands, which is a
    # different axis from how rare it is -- a Scout is rarer than an M4 and
    # far less dangerous. Projectile damage is NOT here: it lives in CfgAmmo
    # under Bullet_*, which this mirror does not publish.
    "modes": re.compile(r"modes\[\]\s*=\s*\{([^}]*)\}"),
}
SCALARS = {
    "count": re.compile(r"\bcount\s*=\s*(\d+)\s*;"),
    "chamberSize": re.compile(r"\bchamberSize\s*=\s*(\d+)\s*;"),
}

# Classes the mirror does not publish at all. Without these, validate.py has no
# record for the weapon and silently skips every attachment hung off it -- the
# check passes by omission, which is the worst kind of green. Confirmed in game
# rather than from config; keep the provenance note if you add to this.
OVERRIDES = {
    # SCAR-H: .308, full-auto, 20rd, mounts the generic optics family
    # (M68/holo, ACOG, MK4, Reflex) like the M4A1 and FAL do.
    "SCARH": {
        "magazines": ["Mag_SCARH_20Rnd"],
        "ammo": ["Ammo_308Win", "Ammo_308WinTracer"],
        "attachments": ["weaponWrap", "weaponOptics", "weaponFlashlight"],
        "modes": ["SemiAuto", "FullAuto"],
    },
    "SCARH_Black": {
        "magazines": ["Mag_SCARH_20Rnd_Black", "Mag_SCARH_20Rnd"],
        "ammo": ["Ammo_308Win", "Ammo_308WinTracer"],
        "attachments": ["weaponWrap", "weaponOptics", "weaponFlashlight"],
        "modes": ["SemiAuto", "FullAuto"],
    },
    "Mag_SCARH_20Rnd": {"slot": ["magazine", "magazine2", "magazine3"], "count": 20},
    "Mag_SCARH_20Rnd_Black": {"slot": ["magazine", "magazine2", "magazine3"], "count": 20},
}


def get(url):
    try:
        return urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
    except Exception:
        return None


def body_of(text, open_brace):
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace:i]
    return ""


def parse(text, parent, own):
    for m in DECL.finditer(text):
        name, par = m.group(1), m.group(2)
        if par:
            parent[name] = par
        body = body_of(text, m.end() - 1)
        for key, rx in ARRAYS.items():
            hit = rx.search(body)
            if hit:
                vals = [v.strip().strip('"') for v in hit.group(1).split(",")
                        if v.strip()]
                if vals:
                    own.setdefault(name, {}).setdefault(key, vals)
        for key, rx in SCALARS.items():
            hit = rx.search(body)
            if hit:
                own.setdefault(name, {}).setdefault(key, int(hit.group(1)))


def main():
    urls = [f"{RAW}/{f}/config.cpp" for f in FLAT]
    for folder in NESTED:
        listing = get(f"{API}/{folder}")
        if not listing:
            print(f"  skip {folder}: listing failed", file=sys.stderr)
            continue
        subs = [x["name"] for x in json.loads(listing) if x["type"] == "dir"]
        urls += [f"{RAW}/{folder}/{s}/config.cpp" for s in subs]
        print(f"  {folder}: {len(subs)} weapons")

    parent, own = {}, {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for text in ex.map(get, urls):
            if text:
                parse(text, parent, own)

    def resolve(name, key, seen=()):
        if name in own and key in own[name]:
            return own[name][key]
        if name in parent and name not in seen:
            return resolve(parent[name], key, seen + (name,))
        return None

    out = {}
    for name in set(parent) | set(own):
        rec = {}
        for key in list(ARRAYS) + list(SCALARS):
            val = resolve(name, key)
            if val:
                rec[key] = val
        if rec:
            out[name] = rec

    added = [k for k in OVERRIDES if k not in out]
    for name, rec in OVERRIDES.items():
        out.setdefault(name, {}).update(rec)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(dict(sorted(out.items())), open(OUT, "w"), indent=1)
    n_slot = sum(1 for v in out.values() if "slot" in v)
    n_att = sum(1 for v in out.values() if "attachments" in v)
    print(f"\n{len(out)} classes ({n_slot} with a worn slot, {n_att} accepting "
          f"attachments) -> {os.path.relpath(OUT)}")
    if added:
        print(f"  + {len(added)} from OVERRIDES (absent from the mirror): "
              f"{', '.join(sorted(added))}")


if __name__ == "__main__":
    main()
