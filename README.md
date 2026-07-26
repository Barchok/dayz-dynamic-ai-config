# Dynamic AI — tuned config (Chernarus)

### Make your empty server feel like a full one.

Most DayZ AI configs give you bullet sponges in identical outfits, standing where you left them,
carrying a bandage and an AKM. This one is built around a different question: *what would it feel like
if the server were actually populated?*

The answer turns out to be **restraint plus consequence**. AI here are rare in open country — you can
cross a valley and meet nobody, which is exactly what makes the times you *do* meet someone matter.
Their gear tracks the map's real loot economy, so a coast encounter is a scruffy freshie with a
shotgun and a northern one might be a plate-carrier team with optics. Points of interest are a
lottery, not a script: an airfield might hold a NATO squad, a Gorka patrol, raiders picking over the
bones — or nobody at all. **Lingering is what gets you found.** And if you fire a shot near somewhere
that matters, something hears it and comes looking.

The result reads as *players*, not spawns: trends you can learn, never truths you can count on. Deaths
feel like your own bad call rather than a bot ambush.

**What's inside:** a three-layer spawn model (regional gear tiers · POI encounters · gunfire response),
ten hand-authored loadouts spanning drifter to spec-ops, faction infighting so AI fight each other and
not just you, and a set of documented knobs to tune the whole thing to your taste. Every design choice
below is explained, and several are verified against the mod's source rather than guessed at.

Built for **solo and small-squad** play on Chernarus.

---

Custom config for the **DayZ-Dynamic-AI-Addon** (Spatial AI, by Dolphin) built on DayZ Expansion AI.

Claude Code generated, with input to shape look & feel of a PvP server.

Currently still a project in progress getting played by myself, so I keep the details fuzzy to myself.


**Scope: tuned for solo / small-squad play, not a populated server.** `PlayerChecks` is set to `-1`, so
one spawn attempt fires per wave regardless of headcount — otherwise a duo standing together generates
double a solo's pressure, which is very noticeable. `MaxAI` (20 patrols) and `CleanupTimer` (20 min) are
sized on the assumption of a handful of players. If player counts grow, revisit `MaxAI`,
`CleanupTimer`, `PlayerChecks`, and the spawn timers together.

> Built blind on purpose: exact zone coordinates live only in `SpatialSettings.json`.
> This README stays at the tier/knob level so you can tune feel without learning where AI sit.

## Requirements & licensing

This repo is **100% original work** — every loadout is authored from scratch (item class-names are
facts from the base game; the curation is ours). It contains **no DayZ Expansion files** and
redistributes none. You supply the mod stack yourself:

- **DayZ Expansion (Core / AI)** — required dependency, installed via the Workshop. It's licensed
  CC BY-NC-ND by the Expansion team; we don't ship or modify any of their content.
- **DayZ-Dynamic-AI-Addon (Spatial AI)** — the addon these settings drive.

Everything in this repo is MIT (see `LICENSE`). It replaces Expansion's generated loadouts entirely,
so you don't need theirs at runtime once the zones point at these.

## Files

| File | Deploy to |
|---|---|
| `SpatialSettings.json` | `<profile>/ExpansionMod/AI/Spatial/SpatialSettings.json` |
| `loadouts/*.json` | `<profile>/ExpansionMod/Loadouts/` |
| `validate.py` | — run before deploying, see below |

**Run `./validate.py` before every deploy.** All eleven loadouts must be present in
`<profile>/ExpansionMod/Loadouts/` — a loadout referenced by `SpatialSettings.json` that isn't on
disk produces naked, unarmed AI with no error in the log after the first spawn (see
[Silent failure modes](#silent-failure-modes)). Point it at your server's `types.xml` to also
class-check every item:

```sh
./validate.py --types /path/to/types.xml
```

Eleven original loadouts, tier-matched to the server's `types.xml` loot tiers (see `weapon-audit.md`):

| Loadout | Tier | Feel |
|---|---|---|
| `CivilianTierLoadout.json` | T1 drifter | Civvie clothes, melee, maybe a pistol in a bag. Weak. |
| `SurvivorTierLoadout.json` | T2 survivor | Varied civilian, SKS/CZ527/Mosin/Ruger + low-tier junk guns, knickknack pack. |
| `RaiderLoadout.json` | T2–3 raider | Scrappy militia: mixed civ/military kit, AK/SKS/MP5/shotgun, police-vest option, sidearm. |
| `GorkaMilitaryLoadout.json` | T3 military | Gorka mountain camo, AKM/AK74/SVD + drum mags. |
| `SovietMilitaryLoadout.json` | T3 military | TTsKO Soviet camo, AKM/AKS74U/SKS/PP19/SVD. |
| `EastMilitaryLoadout.json` | T3–4 operator | Modern Russian: AK101/AK74/SVD + suppressed VSS/ASVAL, plate/helmet. |
| `WestMilitaryLoadout.json` | T3–4 operator | NATO: M4/M16/AUG/FAMAS/Scout, plate carrier, ballistic helmet. |
| `HazmatLoadout.json` | NBC | NBC suit + gas mask, mixed E/W guns, anti-chem kit. Toxic zones only, small groups (1-2) with a long re-arm. |
| `EliteTierLoadout.json` | T4 top | Plate carrier, NVG chance, M4/FAL + SCARH/M14/ASVAL/VSS/SV98. Rare. |
| `GhillieSniperLoadout.json` | special | **Lone ghillie sniper.** M70 Tundra (or rare SV98) w/ scope + rifle ghillie wrap, rangefinder, binos. Always solo, holds position, spawns ~250m out overwatching the approach. |

All weapon/clothing/mag/ammo classes are verified present in the server's `types.xml`. They're vanilla
DayZ classes — if you run item mods and want modded gear, add those class names into the tier files.

`<profile>` = the server profile folder (where `ExpansionMod/` already lives).

## The model: three non-conflicting layers

Gear distribution mirrors the Chernarus **loot economy tiers** (T1 coast → T4 NW military). The mod
can't read the CE tiers directly, so the tier map is reproduced by hand.

The engine keeps **three independent state flags**, which is what lets these stack without fighting:

| Layer | Config | State | Job |
|---|---|---|---|
| Regional tier | `Point[]` | `Spatial_InZone` | Non-overlapping lattice covering ~82% of the map. Sets the loot tier wherever you stand. |
| POI encounters | `Location[]` | `Spatial_InLocation` | Proximity-triggered, hand-placed spawn points. Nests *inside* zones safely. |
| Noise response | `Audio[]` | `Spatial_InLocation` | Gunfire-activated. Someone heard you and comes hunting. |
| Fallback | `Group[]` | — | Thin roam for the ~18% lattice gaps only. |

**Verified in the mod source** (`SpatialAI.c:205`) — zone membership *hard-overrides* the roam; it's
an `if/else`, not additive:

```c
if (player.Spatial_CheckZone())  group = player.GetSpatialGroup();   // zone's own loadout list
else                             group = Spatial_GetWeightedGroup(...); // global roam
```

So a zone whose list contains no civilian entries **cannot** spawn weaksauce. That's how "no freshies
next to Tisy" is structurally enforced rather than merely improbable.

### Why the zones don't overlap (important)

`Spatial_trigger.c` `Leave()` clears `Spatial_InZone` **unconditionally** — it never checks whether
you're still inside another zone. The recovery hook (`OnStayStartServerEvent`) is gated by
`... || player.Spatial_CheckSafe() == Zone_Status`, which is always true for normal (non-safe) zones,
so it never re-claims you. **Net effect: stepping out of an overlapping/nested zone while still
physically inside a bigger one leaves you flagged out-of-zone — persistently — and you fall back to
the roam.** That was the real source of "geared area, bambi spawns".

Hence the `Point` array is a **tangent hex lattice** (radius 1800, centres 3600 apart → exactly zero
overlap, 82% coverage). Circles can't tile a plane, so the remaining ~18% are small gaps that fall
back to the roam — a *positional*, self-correcting condition, unlike the persistent dead pockets.

`Location`/`Audio` triggers use a **different** flag, so they nest inside zones freely — and since
nothing in the mod actually *reads* that flag, they don't interfere with each other either. That's why
several `Location` entries can be stacked on one POI: each rolls independently, so *who* turns up (if
anyone) varies between visits.

### How a POI actually decides (the Location layer)

1. **Rolls only happen while you are inside the trigger cylinder** — `CanSpawn()` returns false when
   `m_insiders.Count() == 0`. Approaching from outside does nothing.
2. **It re-rolls every trigger tick**, not once per visit. So a *low* `Spatial_Chance` becomes a
   **dwell** mechanic: passing through is usually safe, stopping to loot is what gets you found.
   Because of this, `Spatial_Chance` is **derived, not hand-picked** — each POI has a target
   *per-visit* occupancy and a realistic dwell time (glass + approach + loot), and the per-tick rate
   is `1-(1-target)^(1/dwell)`. Consequence worth understanding: a sprawling airfield you spend 20
   minutes clearing carries a *lower* per-tick chance than a village you cross in 8 — otherwise big
   POIs would be permanently occupied purely because you linger there. What's tuned is the odds of
   *an encounter per visit*, not per second.
3. **Trigger radius is deliberately large (420–560m) — bigger than scoping range.** This matters: if
   the radius were small you could glass a POI from a hill, see it empty (no rolls firing, because
   you're outside), walk in, and have AI materialise beside you. Instead you're already inside the
   trigger while observing, so a spawn happens *at the POI, in your optic, 300–500m out* — visible,
   and you get to decide whether to commit.
4. **Spawns land on fixed `Spatial_SpawnPosition` points** (a ring 60–135m around the POI centre,
   terrain-snapped, one picked at random). Not relative to you. Trade-off: no random pop-in, but the
   spots are learnable over time.
5. **After a spawn** that variant is locked for its `Spatial_Timer` (16–35 min) *and* stays blocked
   while its patrol is alive — so a POI won't re-arm behind you.

> **Calibration note:** the per-tick rate is the engine's `Trigger` default (the mod never sets one),
> so the occupancy figures assume ~1 roll/sec. To measure it exactly, set `"Spatial_MinTimer": -1` —
> a negative value trips the mod's hidden debug mode — and count the `Location Chance: … | random: …`
> lines in the Expansion AI log while standing in a POI. Then set `Spatial_MinTimer` back to `15`.

Tier → region (following the iZurvive tier overlay):

| Tier | Region | Zone loadout mix | Weaksauce? |
|---|---|---|---|
| T1 | S coast + E coast strip | drifter/survivor-heavy, some raider | yes — by design |
| T2 | central | survivor/raider, some military | no drifter |
| T3 | western inland | mixed military (Gorka/Soviet/West/East) + hunter | no drifter |
| TE | eastern + NE inland | Russian military-flavoured | no drifter |
| T4 | N / NW military | military + elite only | none |

Zone `Spatial_ZoneLoadout` is picked **uniform-random**, so tiers are biased by *repetition* (listing
a loadout twice ≈ double odds). **The coast now has its own drifter-heavy zones**, which is what frees
the fallback roam from having to serve both ends — the old "bambis up north vs. dead coast" tug-of-war
was one global mix trying to do two opposite jobs. Drifters sit at ~11% of the roam now, so a freshie
in a northern gap is ~0.6% of waves rather than a regular event.

Behaviour: lattice zones all **roam** (HuntMode 5) — they set *gear*, not drama. The drama lives in
the POI layer: `Location` guard pockets (HuntMode 4) and stalkers (6), and `Audio` responders that
**hunt** (1) or **stalk** (6).

**Factions & infighting:** zones/roamers are assigned across `Raiders`/`Mercenaries`/`West`/`East`,
which are mutually hostile by default — so patrols of different factions that spawn near each other
fight *each other*, not just you. That's the source of the ambient "distant firefight" texture. The
**East** faction has extra presence (heavier roaming + several eastern strongholds) so the east side
isn't all raiders.

**NBC / toxic zones:** full hazmat AI are anchored only to the two static Chernarus contaminated
areas (Pavlovo Military SW, Rify shipwreck NE) — a full NBC suit makes sense next to a permanent toxic
zone, nowhere else. If your server uses custom/extra toxic zones, move or add `NBC_*` points to match.

## Loadout design

The tiers share a **rich-cargo philosophy** — killing a geared AI should be worth looting. Every
military tier carries a food/meds/tools/grenades/optics pack plus spare mags, not an empty vest. The
low tiers (drifter/survivor) carry knickknacks (food/drink/meds/tools) so they're not empty-pocket
clones either. **Diversity** comes from wide per-slot clothing pools (picked at random per spawn) and
multi-gun weapon sets, so consecutive patrols in one area look and arm differently.

**Suppressors are deliberately rare**, matching their scarcity in the loot economy: ~1-2% of mid-tier
AI carry a bolt-on (raiders get the `ImprovisedSuppressor`), rising to ~11% at the top. Note the 9x39
rifles (`VSS`/`ASVAL`) are *integrally* suppressed, so the high tiers are quieter than the bolt-on
numbers alone suggest — their share of the weapon pool is the real dial there.

The three Russian military tiers (Gorka / Soviet / East) share an AK-family arsenal but distinct
**wardrobes** — Gorka mountain camo, TTsKO Soviet camo, modern Russian — so they read as different
units even where their gun pools overlap. `loadouts/` were generated from a data-driven builder; the
selection and arrangement are original.

## Knobs you'll actually tune

All in `SpatialSettings.json` root unless noted.

| Knob | Now | Effect |
|---|---|---|
| `Spatial_MinTimer` / `Spatial_MaxTimer` | 15 / 35 (min) | Time between spawn waves. Note waves fire on a clock, not on movement — so **camping one spot means every wave lands on you**, while travelling leaves them behind. Higher = rarer. |
| `MaxAI` | 20 | Hard cap on concurrent **patrols** (groups, not individual AI) server-wide. |
| `PlayerChecks` | -1 | **The party-size knob.** Sign and magnitude do different things: `>= 0` requires the player be a *party/group leader* (no party = no spawns at all — dangerous if you don't use Expansion parties); **negative skips that check** but the absolute value still caps how many players are processed per wave. `-1` = exactly one spawn attempt per wave no matter how many of you there are. At `-5` a duo generated *double* a solo's spawn pressure, which is a lot if you're standing together. |
| `CleanupTimer` | 20 (min) | Patrol lifetime from spawn. Also governs corpse lifetime — a body lasts `CleanupTimer` minus how long the patrol was already alive. Engaged AI defer despawn until they lose aggro; unaware AI and corpses do not. Must stay above `EngageTimer`. |
| `MinDistance` / `MaxDistance` | 200 / 350 (m) | Spawn ring around the player. Min enforced ≥120. |
| `HuntMode` (global) | 5 | Roaming behaviour (see below). |
| `Spatial_Weight` (per Group) | Drifter 18 / Raider 40 / Survivor 20 / West 5 / East 6 / Elite 2 / Militia(East) 4 | Tier mix of map-wide roamers. Drifter cut 42→18 after "too many bambis up north" — melee freshies now ~19% of roamers (was 38%), so the rare wilderness spawn skews armed. |
| `Spatial_Chance` (per Group roamer) | 0.25 | Chance a roaming wave actually spawns. 1.0 was "always someone in the open"; 0.25 = ~one wilderness patrol/100min — rare but ever-present tail. |
| `Spatial_Chance` (per Point) | 0.50–0.60 by tier | Chance a regional zone produces a patrol that wave. Rolls per wave, so nowhere is permanently dead or permanently occupied. |
| `Locations_Enabled` / `Audio_Enabled` | 1 / 1 | Enable the POI and noise-response layers. |
| `Spatial_Sensitivity` (per Audio) | 50 | Noise threshold. Firing a weapon scores **1000**; movement is single digits — so 50 = **gunfire only**. Lower it to react to sprinting. |
| `Spatial_Timer` (Location/Audio) | 20–30 (min) | Cooldown before that trigger can fire again. Stored in minutes, converted ×60000 internally. A trigger also won't re-fire while its previous patrol is still alive. |
| `Spatial_SpawnMode` (Location/Audio) | 0 | 0 = spawn at **one random** listed position (unpredictable). 1 = spawn a patrol at **every** listed position (full garrison — multiplies AI count). |
| `Spatial_MinAccuracy` / `Spatial_MaxAccuracy` | per tier | 0–1, **higher = deadlier**. Drifter 0.22–0.45 → Elite 0.55–0.78, hotspots up to 0.80. Ceiling held at 0.80 (0.85+ = aimbotty); wide min–max keeps good/bad shots. |
| `MessageType` | 0 | 0 = silent (no chat/popup). 1–2 chat, 3–4 popup, 5 popup w/ GPS. |
| `Points_Enabled` | 1 | 1 = hotspots + roaming both active. 2 = hotspots only (kills roaming). |

### HuntMode values (verified from source)

- `1` actively hunts the player  ·  `2` moves to last-known spot  ·  `3` halt
- `4` guards its spawn area (used at military hotspots)
- `5` roams around player + self (global default — "wandering players")
- `6` follows/stalks the player

## Tuning recipes

- **Too many encounters →** raise `Spatial_MinTimer`/`MaxTimer` and/or lower `MaxAI`.
- **Too many when playing as a group →** that's `PlayerChecks`; `-1` gives one attempt per wave total.
- **A POI keeps re-arming while you hold it →** raise that Location's `Spatial_Timer` (re-arm cooldown).
- **Wilderness too busy/lonely →** lower/raise the roamers' `Spatial_Chance` (0.25 now).
- **A POI feels always-occupied / always-empty →** raise/lower that tier's per-Point `Spatial_Chance`.
- **Military too common on the coast →** lower the `Operator`/`Elite` weights in the `Group` array.
- **A region's gear feels wrong →** edit that tier's `Spatial_ZoneLoadout` list; repetition biases it.
- **Want AI to actively push you at a POI →** that's the `Location`/`Audio` layer, HuntMode 1 or 6.
- **Going loud should cost more →** raise the `Audio` entries' count/accuracy, or lower `Spatial_Timer`.
- **Never want a freshie inland →** the lattice already forbids it; the residual is the ~18% gaps, so
  lower the `Drifter` roamer weight further (or its `Spatial_Chance`).
- **Ghillie sniper too rare / too common →** the `*_SNIPER` entries in `Location[]`. Currently ~4% per
  full military-base visit (~1 in 8 sessions clearing three bases). Chance is derived from a target
  per-visit probability, so scale all seven `Spatial_Chance` values by the same factor to move it.
  His accuracy is capped at 0.72 on purpose — a sniper who always lands the first shot is a death,
  not an encounter.
- **Loadout feels off →** edit the tier's loadout JSON. Chance-based entries roll independently;
  no `Chance` = guaranteed.

## JSON format rules (the engine crashes, doesn't warn)

DayZ's JSON loader access-violates on a type mismatch instead of erroring. Two non-obvious rules,
learned the hard way — match the mod's own generated file:

- **Positions are arrays, not strings:** `"Spatial_Position": [4600.0, 200.0, 10400.0]` — never
  `"4600 200 10400"`. Same for `Spatial_TriggerPosition`, and `Spatial_SpawnPosition` is an array of
  such arrays.
- **Bools are `0`/`1`, not `false`/`true`:** every `Spatial_UnlimitedReload`, `Spatial_Safe`,
  `Spatial_InVehicle`, etc.

If a boot crashes with `jsonfileloader.c` + `spatialsettings.c` in the `.RPT` stack, it's a format
mismatch here. Rename the file, boot once to regenerate the stock default, and diff against it.

## Silent failure modes

These three cost a full play session to find. None of them logs anything useful. `validate.py`
checks for all three.

**1. Every loadout node needs an explicit `Chance`.** Enforce zeroes absent *primitive* fields when
deserialising, so a node written without `"Chance"` loads as `Chance = 0`, and:

```c
bool CanSpawn() {
    if (!Chance || Chance < Math.RandomFloat(0.0, 1.0)) return false;
```

...drops it silently. Absent `ref` members (`Quantity`, `Health`) survive at their constructor value,
which is why this isn't obvious — the file half-works. Symptom: AI spawn with no shirt, no pants, no
boots and **no weapon**, while chance-carrying slots (backpack, headgear, vest) and all cargo appear
normally. You get spare magazines with no rifle. Expansion's own generated loadouts always write
every field, so their data never hits this path.

**2. One weapon per set, not many weapons in one slot.** In `ExpansionPrefabObject.c` the AI-specific
remap sends the first candidate in a `Shoulder` slot to `HANDS` and the second to `SHOULDER` — so
several weapons in one slot means the AI spawns **carrying two guns**. Stock's pattern is one weapon
per set with every set sharing a name; the `setNames` dedupe then guarantees exactly one. To keep the
armed rate when splitting a set of chance `C` into `n`, give each `1-(1-C)^(1/n)`.

**3. A missing loadout file fails open, then goes quiet.** `SpatialSettings.c` only existence-checks
`Point` loadouts, and its `loadout = "HumanLoadout.json"` fallback is a no-op (the `foreach` variable
is a copy); `Location` and `Audio` get no check at all. `ExpansionPrefab.Load()` then inserts an
**empty** prefab into its static cache *before* testing `FileExist`, so the first request returns
null and logs `Unknown loadout requested`, and every request after that is a cache hit returning the
empty prefab — applied without complaint. One missing file means naked AI for the rest of the
server's uptime, with a single line in the log at boot.

## Known limitation: spawns can appear in view

This applies to the **zone/roam layer only**. Placement (`Spatial_ValidPos`) checks just: random point
in the `MinDistance`–`MaxDistance` ring, drop to ground, reject if in water. **No line-of-sight or FOV
check** — an AI can pop in on ground you've scoped and cleared. No config fix; a real FOV check would
need a code change. Mitigation: raise `MinDistance` (rarer/farther pop-in, not eliminated).

**The `Location`/`Audio` layer does not have this problem** — those spawn at explicit
`Spatial_SpawnPosition` coordinates you choose, so they can be placed behind cover, in treelines, or
out of sight of the obvious overwatch. That's the tool for spots you actually hold.

## Caveats / verify in the field

- **Hotspot coordinates are approximate** well-known Chernarus POIs with generous radii. The `y`
  value is a rough terrain elevation — if a zone never triggers, its `y` is likely too far off the
  ground; nudge it toward the real terrain height there. Radius gives slack.
- **Faction hostility** (`Raiders`/`Mercenaries`/`West`/`East`) drives who the AI shoots at. If any
  faction reads as non-hostile on your build, swap it — this is a per-entry string.
- **Internal-mag guns** (Repeater, Izh18, B95, etc. in the low tiers) spawn without a loose magazine;
  the AI gets loose ammo in cargo. If one is ever seen standing with an empty gun, swap that slot for
  a mag-fed alternative.
- After editing, delete nothing — just restart the server; the mod reloads the JSON on boot and logs
  parse errors to the Expansion AI log.
