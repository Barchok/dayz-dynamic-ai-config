#!/usr/bin/env python3
"""Pre-deploy validator for the Spatial AI config.

Catches the three failure modes that fail SILENTLY on a live server:

  1. A loadout node without an explicit "Chance". Enforce zeroes absent
     primitive fields on JSON load, so ExpansionPrefabObject.CanSpawn() sees
     Chance == 0 and the item never spawns. No error is logged. This is what
     produced naked, unarmed AI.

  2. Multiple weapons in one Shoulder/Hands slot. The AI remap in
     ExpansionPrefabObject.c puts candidate #1 in HANDS and #2 on SHOULDER,
     so the AI carries two guns. Stock uses one weapon per named set instead.

  3. A loadout referenced by SpatialSettings.json that is not on disk.
     SpatialSettings.c only existence-checks Point loadouts, and its fallback
     assignment is a no-op; Location and Audio get no check at all.
     ExpansionPrefab.Load() then caches an empty prefab, so only the first
     spawn logs "Unknown loadout requested" and every later one is silent.

  4. An item placed in a slot that cannot accept it. CreateAttachmentEx just
     returns null, so the entry never spawns and nothing is logged -- it only
     shows up as a slot that is emptier than its chances suggest. Needs a slot
     map from fetch_slotmap.py (types.xml carries no slot data).

Optionally cross-checks every class name against a types.xml.

Usage:
    ./validate.py [--types /path/to/types.xml] [--slots /path/to/slotmap.json]
"""
import json
import sys
import glob
import os
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
LOADOUT_DIR = os.path.join(ROOT, "loadouts")
SETTINGS = os.path.join(ROOT, "SpatialSettings.json")
WEAPON_SLOTS = ("Shoulder", "Hands", "Melee")

errors = []
warnings = []


def walk(node, file, path, parent=None):
    """Yield (node, path, is_item, slot, parent) for every prefab node.

    is_item is False for Sets: a set's ClassName is a grouping name
    (PRIMARY, SIDEARM), not a spawnable class, so it must not be
    checked against types.xml.

    slot is the SlotName the node is attached in, or None for cargo and
    sets. An empty SlotName means auto-attach (CreateAttachment picks the
    slot), which is how optics and magazines hang off a weapon -- there
    `parent` is the class the item is hanging off.
    """
    here_class = node.get("ClassName") or parent
    for slot in node.get("InventoryAttachments", []):
        raw = slot.get("SlotName", "")
        name = raw or "(auto)"
        for n, item in enumerate(slot.get("Items", [])):
            here = f"{path}/att[{name}][{n}]"
            yield item, here, True, raw, here_class
            yield from walk(item, file, here, item.get("ClassName"))
    for n, cargo in enumerate(node.get("InventoryCargo", [])):
        here = f"{path}/cargo[{n}]"
        yield cargo, here, True, None, here_class
        yield from walk(cargo, file, here, cargo.get("ClassName"))
    for n, st in enumerate(node.get("Sets", [])):
        here = f"{path}/set[{st.get('ClassName') or n}]"
        yield st, here, False, None, here_class
        yield from walk(st, file, here, parent)


def check_slot(name, path, item, slot, parent, slots):
    """Verify an item can actually attach where the loadout puts it.

    Two cases. A non-empty SlotName is a worn slot: the class's own
    inventorySlot[] must contain it. An empty SlotName is auto-attach, used
    for optics and magazines on a weapon: the class must be accepted by the
    parent's attachments[] / magazines[] / chamberableFrom[].
    """
    cn = item.get("ClassName")
    rec = slots.get(cn)
    if not cn or rec is None:
        return  # not a class this map covers (ammo, food, ...)

    if slot:
        # weapon slots take anything wieldable by category, not by
        # inventorySlot[] -- PipeWrench declares Backpack_1 yet is a valid
        # Melee item, so checking those would be pure false positives.
        if slot in WEAPON_SLOTS:
            return
        declared = rec.get("slot")
        if not declared:
            return
        match = next((d for d in declared if d.lower() == slot.lower()), None)
        if match is None:
            errors.append(
                f"{name}: {path} '{cn}' cannot attach in slot '{slot}' "
                f"-> silently never spawns (its slot is {'/'.join(declared)})")
        elif match != slot:
            warnings.append(f"{name}: {path} slot '{slot}' should be "
                            f"'{match}' to match vanilla's spelling")
        return

    prec = slots.get(parent)
    if prec is None:
        return
    declared = rec.get("slot") or []
    accepted = [a.lower() for a in prec.get("attachments", [])]
    if any(d.lower() in accepted for d in declared):
        return
    # BI's own configs disagree on case between types.xml and CfgWeapons
    # (Mag_SV98_10Rnd vs magazines[]={"Mag_SV98_10rnd"}), so compare folded
    fits = {m.lower() for m in prec.get("magazines", [])} | \
           {a.lower() for a in prec.get("ammo", [])}
    if cn.lower() in fits:
        return
    if not declared and not prec.get("attachments"):
        return
    errors.append(
        f"{name}: {path} '{cn}' does not fit '{parent}' "
        f"-> silently never spawns ('{cn}' needs {'/'.join(declared) or '?'}, "
        f"'{parent}' accepts {'/'.join(prec.get('attachments', [])) or 'no attachments'})")


def check_loadout(file, types, slots):
    name = os.path.basename(file)
    try:
        d = json.load(open(file))
    except json.JSONDecodeError as e:
        errors.append(f"{name}: invalid JSON - {e}")
        return

    if "Chance" not in d:
        errors.append(f"{name}: root node has no explicit Chance")

    for node, path, is_item, slot, parent in walk(d, name, "root"):
        if "Chance" not in node:
            errors.append(f"{name}: {path} '{node.get('ClassName')}' "
                          f"has no explicit Chance -> will never spawn")
        cn = node.get("ClassName")
        if is_item and types is not None and cn and cn not in types:
            errors.append(f"{name}: {path} class '{cn}' not in types.xml")
        if is_item and slots is not None and slot is not None:
            check_slot(name, path, node, slot, parent, slots)

    # a set whose name is empty skips the dedupe in ExpansionPrefabObject.c,
    # so every such set spawns instead of one of them
    for st in d.get("Sets", []):
        if not st.get("ClassName"):
            warnings.append(f"{name}: unnamed set - dedupe is skipped, "
                            f"it will spawn alongside every other set")
        for slot in st.get("InventoryAttachments", []):
            if slot.get("SlotName") in WEAPON_SLOTS:
                n = len(slot.get("Items", []))
                if n > 1:
                    errors.append(
                        f"{name}: set '{st.get('ClassName')}' has {n} weapons in "
                        f"one {slot['SlotName']} slot -> AI spawns holding two. "
                        f"Split into {n} sets sharing the same set name.")

    # core slots that can come out empty
    for slot in d.get("InventoryAttachments", []):
        if slot.get("SlotName") in ("Body", "Legs", "Feet"):
            p = 1.0
            for i in slot.get("Items", []):
                p *= 1.0 - float(i.get("Chance", 0.0))
            if p > 0.001:
                warnings.append(f"{name}: {slot['SlotName']} is empty "
                                f"{p*100:.0f}% of the time")


def check_settings():
    if not os.path.exists(SETTINGS):
        errors.append("SpatialSettings.json not found")
        return
    d = json.load(open(SETTINGS))
    referenced = set()
    for key in ("Point", "Location", "Audio", "Group"):
        for entry in d.get(key, []):
            lo = entry.get("Spatial_ZoneLoadout")
            if lo is None:
                continue
            for one in (lo if isinstance(lo, list) else [lo]):
                referenced.add(one)

    on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(LOADOUT_DIR, "*.json"))}
    for r in sorted(referenced):
        if r not in on_disk:
            errors.append(f"SpatialSettings.json references '{r}' "
                          f"which is not in loadouts/")
    for o in sorted(on_disk - referenced):
        warnings.append(f"{o} is never referenced by SpatialSettings.json")
    return referenced


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--types", help="path to types.xml for class-name checking")
    ap.add_argument("--slots", help="path to slotmap.json from fetch_slotmap.py "
                                    "for slot/attachment checking")
    args = ap.parse_args()

    types = None
    if args.types:
        import xml.etree.ElementTree as ET
        types = {t.get("name") for t in ET.parse(args.types).getroot()}

    slots = json.load(open(args.slots)) if args.slots else None

    files = sorted(glob.glob(os.path.join(LOADOUT_DIR, "*.json")))
    for f in files:
        check_loadout(f, types, slots)
    referenced = check_settings()

    print(f"checked {len(files)} loadouts"
          + (f" against {len(types)} types.xml entries" if types else "")
          + (f" and {len(slots)} slotmap entries" if slots else "")
          + (f", {len(referenced)} referenced by SpatialSettings.json" if referenced else ""))
    for w in warnings:
        print(f"  warn:  {w}")
    for e in errors:
        print(f"  ERROR: {e}")
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
