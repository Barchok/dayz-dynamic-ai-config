# Weapon audit — grading, classes, calibers

Source of truth for **how rare a gun is** and therefore how heavily it should be weighted in a
loadout, plus the trademark-safe display-name → class mapping and verified calibers.

Two independent ground truths back this file, and neither is guesswork:

| What | Source | Verified |
|---|---|---|
| Rarity / where it spawns | server `types.xml` | byte-identical to stock BI Central Economy |
| Caliber / magazine / optics | vanilla `CfgWeapons` | `magazines[]`, `chamberableFrom[]`, `attachments[]` |

## Provenance — the economy is stock

The server's `types.xml` is **byte-identical** to Bohemia's published Central Economy for
`dayzOffline.chernarusplus`:

```
md5  03b42b7188f7ced6ec42b21cccf7714d   ExpansionMod-Source/types.xml
md5  03b42b7188f7ced6ec42b21cccf7714d   BohemiaInteractive/DayZ-Central-Economy@master
```

So every grade below is **vanilla-accurate**, not server-specific, and matches what any Chernarus
player's instincts are calibrated against. Re-check after a game update with:

```sh
curl -s https://raw.githubusercontent.com/BohemiaInteractive/DayZ-Central-Economy/master/dayzOffline.chernarusplus/db/types.xml | md5
```

## How to read the economy fields

| Field | Meaning | Effect on rarity |
|---|---|---|
| `nominal` | target number of this item **alive on the map at once** | the primary signal — lower is rarer |
| `min` | floor that triggers restock | high `min`/`nominal` ratio = aggressively topped up |
| `<value>` | which loot **tier** (T1 coast → T4 NW military) | **absent = no tier restriction**, not "never spawns" |
| `<usage>` | which building/area category | narrow usage concentrates it |
| `lifetime` | seconds before despawn | short = faster churn, same standing count |
| `deloot="1"` | **also** spawns at heli crashes and military convoys | additive — does not remove normal loot |

Two traps worth stating plainly, because both are easy to get backwards:

- **No `<value>` tag means unrestricted tier.** `Crowbar`, `Pipe` and `BaseballBat` carry no
  `<value>` and are everywhere in game, which settles it.
- **`deloot="1"` is additive.** It adds crash/convoy sites on top of normal loot; it does not make
  the gun event-only.

## Rarity grades

Grades are banded on `nominal`, because that is literally how many exist. Spawn breadth
(`tier` × `usage`) tells you *where* they are and is listed alongside — a low-nominal gun confined
to one tier is concentrated where geared players farm, while the same nominal spread across all
tiers is thin everywhere.

**S** ≤2 · **A** 3–5 · **B** 6–12 · **C** 13–30 · **D** 31+

| Grade | Gun | nominal | min | tier | usage | also | Loadouts |
|---|---|---|---|---|---|---|---|
| S | `SCARH_Black` | 0 | 0 | any | — | **never spawns as loot** | Elite |
| S | `Aug` | 1 | 1 | any | ContaminatedArea | toxic-zone only | West |
| S | `M4A1` | 1 | 1 | any | ContaminatedArea | toxic-zone only | Elite, Hazmat, West |
| S | `Scout` | 1 | 1 | any | Prison | — | Hunter, West |
| S | `ASVAL` | 2 | 1 | T4 | Military | — | East, Elite |
| S | `FAL` | 2 | 1 | any | ContaminatedArea | toxic-zone only | Elite |
| S | `M14` | 2 | 1 | T4 | Military | — | Elite |
| S | `SV98` | 2 | 1 | T4 | Military | — | Elite, GhillieSniper |
| A | `AKM` | 3 | 2 | T4 | Military | — | Gorka, Hazmat, Raider, Soviet |
| A | `SCARH` | 3 | 1 | any | Military | heli/convoy | Elite |
| A | `AK101` | 4 | 2 | T3,T4 | Military | — | East |
| A | `AK74` | 4 | 2 | any | Military | heli/convoy | East, Gorka, Raider |
| A | `AugShort` | 4 | 3 | T3,T4 | Military | — | West |
| A | `FAMAS` | 4 | 3 | any | Military | heli/convoy | West |
| A | `M16A2` | 4 | 2 | T3,T4 | Military | — | West |
| A | `SVD` | 4 | 2 | any | Military | heli/convoy | East, Gorka, Hazmat, Soviet |
| A | `Vikhr` | 4 | 2 | T2,T3 | Military | — | Hunter |
| A | `Winchester70` | 4 | 2 | T3,T4 | Hunting | — | GhillieSniper, Hunter |
| A | `PM73Rak` | 5 | 4 | any | Police | heli/convoy | Survivor |
| B | `R12` | 6 | 5 | T3,T4 | Police | — | Hunter |
| B | `VSS` | 6 | 4 | T3,T4 | Military | — | East, Elite |
| B | `AKS74U` | 8 | 5 | T3 | Military | — | East, Hazmat, Raider, Soviet |
| B | `MP5K` | 8 | 6 | T2,T3 | Military | — | Raider |
| B | `SKS` | 8 | 6 | any | Military | heli/convoy | Gorka, Raider, Soviet, Survivor |
| B | `Mp133Shotgun` | 10 | 8 | T3,T4 | Police | — | Raider |
| B | `PP19` | 10 | 8 | T2,T3 | Military | — | Soviet |
| B | `SSG82` | 12 | 10 | T3,T4 | Police | — | Hunter |
| B | `Saiga` | 12 | 10 | T2,T3 | Military | — | Hunter |
| C | `FNX45` | 14 | 12 | T2,T3,T4 | Military | — | West |
| C | `Longhorn` | 15 | 10 | T2,T3 | Hunting | — | Survivor |
| C | `Mosin9130` | 17 | 15 | T3,T4 | Town,Village | — | Hunter, Survivor |
| C | `B95` | 18 | 14 | T3,T4 | Hunting | — | Hunter |
| C | `CZ75` | 20 | 18 | T1,T2 | Military | — | East, GhillieSniper, Gorka, Raider |
| C | `CZ527` | 25 | 23 | T2,T3 | Farm | — | Raider, Survivor |
| C | `Deagle` | 25 | 23 | T1,T2 | Town | — | Civilian |
| C | `Magnum` | 25 | 20 | T1 | Town | — | Civilian |
| C | `Colt1911` | 26 | 22 | T1,T2 | Military | — | Survivor, West |
| C | `Izh43Shotgun` | 30 | 26 | T2,T3 | Farm | — | Survivor |
| C | `Repeater` | 30 | 24 | T2,T3 | Farm | — | Survivor |
| D | `Ruger1022` | 35 | 25 | T1,T2 | Town,Village | — | Survivor |
| D | `Glock19` | 40 | 35 | T1,T2 | Police | — | Raider |
| D | `Izh18` | 50 | 47 | T2,T3 | Farm,Village | — | Survivor |
| D | `Izh18Shotgun` | 55 | 50 | T2,T3 | Town,Village | — | Civilian |
| D | `MakarovIJ70` | 70 | 60 | T1,T2 | Town,Village | — | Civilian, East, GhillieSniper, Gorka, Raider, Soviet |

## Findings to sanity-check against play experience

These are the places where the data says something surprising. **Flag anything that contradicts what
you actually see in game** — that's the check this file exists for.

1. **`SCARH_Black` has `nominal 0`.** It cannot spawn as loot at all. Only Elite AI can ever have
   one, so it is effectively an AI-exclusive weapon. Intentional or not, it is a give-away tell.
2. **`Aug`, `M4A1` and `FAL` are `ContaminatedArea`-only.** Not T4 military. They come from toxic
   zones exclusively, which makes them far harder to obtain than `nominal 1–2` alone suggests, and
   arguably the most prestigious guns on the map.
3. **`Scout` is the rarest gun in the game, jointly with `Aug` and `M4A1`.** `nominal 1` — exactly
   one exists in the world at a time — and it is the **only weapon in the entire economy with
   `usage=Prison`**, so it spawns in one narrow building category and nowhere else. It is currently
   in both Hunter *and* West at flat odds.
4. **`SVD` vs `AKM` is genuinely close on paper** — nominal 4 vs 3. SVD spreads across all tiers plus
   crash sites; AKM is confined to T4 military. If SVD feels much rarer than AKM in play, the likely
   cause is that SVD's 4 copies are spread thin over every military point while AKM's 3 are
   concentrated where people farm, plus SVD gets hoarded on sight. **Worth confirming from
   experience** — it drives how hard we weight SVD down.
5. **`AK74`, `FAMAS`, `SKS`, `SCARH`, `PM73Rak` carry `deloot="1"`** and no tier, so they turn up at
   crashes and convoys as well as normal military loot.

### Where the AI out-supply the world

Rarity inflation only actually matters for guns players *want*. A gun that is rare **and** weak is
harmless to hand out — see the threat axis below — so read this table together with that one.

For grade-S guns the AI are the dominant source on the server, which inverts the loot economy: a gun
the map holds one or two of is being handed out on a double-digit percentage of spawns.

| Gun | nominal | AI carry rate today |
|---|---|---|
| `Scout` | 1 | Hunter 12.5% · West 16.7% |
| `M4A1` | 1 | Hazmat 25% · West 16.7% · Elite 13.9% |
| `Aug` | 1 | West 16.7% |
| `FAL` | 2 | Elite 17.6% |
| `SV98` | 2 | Elite 13.9% · GhillieSniper 8% |
| `M14` | 2 | Elite 13.9% |
| `ASVAL` | 2 | Elite 13.9% · East 10% |
| `SCARH_Black` | **0** | Elite 6.5% |

`M4A1` in Hazmat is the one that is arguably *correct* despite the numbers — it is
`ContaminatedArea`-only loot and Hazmat is the toxic-zone faction, so it reads as lore-accurate.
The rest are candidates for weighting down.

## Threat — the second axis

**Rarity is not power, and for some guns the two point in opposite directions.** A `Scout` is the
rarest rifle in the game and one of the least dangerous things an AI can hold: bolt-action, 5-round
magazine, intermediate caliber. An `M4A1` is equally rare and vastly more lethal. Weighting a loadout
on rarity alone would get this exactly backwards.

Fire modes and capacity below are read from `modes[]` and `count`/`chamberSize` in `CfgWeapons` —
verified, not remembered. **Projectile damage is not available**: it lives in `CfgAmmo` under
`Bullet_*`, which the config mirror does not publish, so the caliber grouping is mechanical
(what it chambers) and the threat tier is *judgement* built on top. That tier is the column to
correct from play experience.

**Damage per shot dominates rate of fire.** With a full-power cartridge the first hit decides the
fight, so a bolt-action in 7.62×54 is not meaningfully safer than a semi-auto in the same round —
fire rate only starts to matter once the first shot misses. Grading on action type alone puts `SV98`
and `SVD` in different worlds despite being the same cartridge at the same capacity, which is wrong.

Both axes below are verified: caliber from `chamberableFrom[]`, action from `modes[]`.

| Action ↓ · Caliber → | full-power<br>.308 · 7.62×54 | intermediate<br>5.56 · 5.45 · 7.62×39 | 9×39 AP | pistol | shotgun | rimfire |
|---|---|---|---|---|---|---|
| **full-auto** | `FAL` `SCARH` `SCARH_Black` | `M4A1` `AK101` `AK74` `AKM` `AKS74U` `Aug` `AugShort` `FAMAS` | `ASVAL` `VSS` `Vikhr` | `PP19` `MP5K` `PM73Rak` | `Saiga` | — |
| **burst** | — | `M16A2` | — | — | — | — |
| **semi-auto** | `SVD` `M14` | `SKS` | — | `Deagle` | `R12` | `Ruger1022` |
| **single-shot** | `SV98` `Mosin9130` `Winchester70` `B95` | `Scout` `CZ527` `SSG82` `Izh18` | — | `Magnum` `Repeater` | `Izh18Shotgun` `Izh43Shotgun` `Mp133Shotgun` | — |

Reading that as threat:

| Threat | Guns | Why |
|---|---|---|
| **Extreme** | `VSS` `ASVAL` · `FAL` `SCARH` `SCARH_Black` | the 9×39 pair are full-auto **and integrally suppressed** — see below; the .308 trio is full-power full-auto |
| **Very high** | `M4A1` `AK101` `AK74` `AKM` `AKS74U` `Aug` `AugShort` `FAMAS` · `Vikhr` | sustained auto |
| **High (ranged)** | `SVD` `M14` · `SV98` `Mosin9130` `Winchester70` `B95` | one hit decides it — action type is secondary |
| **High (close)** | `PP19` `MP5K` `PM73Rak` · `Saiga` | volume at short range; `Saiga` is full-auto 12ga |
| **Moderate** | `M16A2` `SKS` `R12` `Ruger1022` | limited rate or limited energy |
| **Low** | `Scout` `CZ527` `SSG82` `Izh18` · single-barrel shotguns | slow follow-up *and* no one-shot potential |
| **Minimal** | `Magnum` `Deagle` `Repeater` `MakarovIJ70` `CZ75` `Glock19` `Colt1911` `FNX45` `Longhorn` | sidearms |

Verified mechanics behind the table:

| Gun | Fire modes | Capacity | Gun | Fire modes | Capacity |
|---|---|---|---|---|---|
| `M4A1` | SemiAuto/FullAuto | 30 | `SVD` | SemiAuto | 10 |
| `AK101` `AK74` `AKM` `AKS74U` | SemiAuto/FullAuto | 30 | `M14` | SemiAuto | 10 |
| `Aug` `AugShort` | SemiAuto/Burst/FullAuto | 30 | `VSS` `ASVAL` `Vikhr` | SemiAuto/FullAuto | 10 |
| `FAMAS` | SemiAuto/Burst/FullAuto | 25 | `SKS` | SemiAuto | 10 internal |
| `FAL` | SemiAuto/FullAuto | 20 | `SV98` | Single | 10 |
| `M16A2` | SemiAuto/**Burst only** | 30 | `Scout` | **Single** | **5** |
| `PP19` | SemiAuto/FullAuto | **64** | `Winchester70` `Mosin9130` | Single | 5 internal |
| `MP5K` | SemiAuto/Burst/FullAuto | 15 | `SSG82` `CZ527` | Single | 5 |
| `PM73Rak` | **FullAuto only** | 25 | `B95` | Single/Double | 1 internal |

`SCARH` / `SCARH_Black` are absent from the config mirror entirely. Their full profile — **.308,
full-auto, 20-round magazine, generic `weaponOptics` mount** — is confirmed from play rather than
config, and matches `FAL` exactly. The class name `Mag_SCARH_20Rnd` corroborates the capacity: every
`_NNRnd` mag whose `count` *is* readable (`Mag_FAL_20Rnd`, `Mag_M14_20Rnd`) matches its name.

Because the mirror has no record of them, `validate.py --slots` would silently skip every attachment
hung off a SCAR — passing by omission. They are therefore pinned in the `OVERRIDES` table in
`fetch_slotmap.py`, which makes the check live: a `PSO1Optic` on a `SCARH` now errors.

### Detectability — why the suppressed 9×39 outrank everything

Threat isn't only damage and rate of fire. A suppressed shooter gives the player **no directional
cue**, so the first indication of contact is taking damage, and there's nothing to orient on to
return fire or break contact correctly. That is a bigger practical multiplier than a step up in
caliber, and it is exactly the "bot ambush" failure the design intent is trying to avoid — which is
a reason to keep these rare quite apart from their loot rarity.

It compounds: **9×39 is always subsonic in DayZ**, so there is no sonic crack either. Suppressor
plus subsonic removes both of the cues a player normally uses to locate a shooter. Note also that
the AP variant does more damage *to armour* but the **same damage to the player** — so `Ammo_9x39AP`
is a penetration advantage, not a damage one.

Integral suppression is config-verified, not assumed. `VSS_Base` ships silencer sound sets as its
*default* `soundSetShot[]`:

```
VSS_Base   soundSetShot[] = {"VSS_1st_silencer_SoundSet", "VSS_silencerTail_SoundSet",
                             "VSS_silencerInteriorTail_SoundSet"}
```

Every other weapon in the game ships a normal shot sound set. **`VSS` and `ASVAL` inherit that
silencer set** and accept no suppressor attachment — they don't need one.

**`Vikhr` is the exception and it matters.** It inherits the same `VSS_Base` but *overrides*
`soundSetShot[]` with `Vikhr_Shot_1st_SoundSet` — a normal report — and it is the only one of the
three that accepts `suppressorImpro`. So Vikhr is the **loud** 9×39. Grouping all three together as
"the suppressed rifles" is wrong, and it's the one currently in `HunterTierLoadout`.

| | Integrally suppressed | Accepts suppressor | Loadouts |
|---|---|---|---|
| `VSS` | **yes** | — (not needed) | East, Elite |
| `ASVAL` | **yes** | — (not needed) | East, Elite |
| `Vikhr` | no | `suppressorImpro` | Hunter |

**Open question:** whether a suppressed shot scores lower on the noise value that drives the
`Audio[]` response layer (`Spatial_Sensitivity` 50, gunfire nominally 1000). If it does, suppressed
AI-vs-AI firefights would never trigger noise responders, and the ambient "something heard you"
texture would quietly skip the high tiers. Not verified — the weapon configs carry no noise field.

### Reading the two axes together

| | Low threat | High threat |
|---|---|---|
| **Rare** | `Scout` — safe to hand out, reads as a story ("this one looted the prison") | `FAL`, `M4A1`, `Aug`, `ASVAL`, `SV98`, `M14` — **weight down hardest**: inflates the economy *and* raises lethality |
| **Common** | `Izh18`, `CZ527`, `Repeater`, single-barrel shotguns — ideal low-tier filler | `AKS74U`, `PP19`, `Saiga`, `Mosin9130` — workhorses, fine in volume at the right tier |

The top-right cell is the one that actually needs restraint. The top-left is close to free — and it
turns out to be a cell of one, `Scout`. Rare-and-harmless is much less common than it looks.

## Display name ↔ config class (the traps)

In-game display names are trademark-safe and do **not** match config classes. Loadouts and
`types.xml` use the class. Always resolve display → class before editing a loadout — a wrong name
won't crash, it just silently never spawns.

| In-game display | Config class |
|---|---|
| SCR-17 | `SCARH` / `SCARH_Black` |
| DMR | `M14` |
| SVAL | `ASVAL` |
| VSS | `VSS` |
| Vaiga | `Saiga` |
| Blaze | `B95` |
| M70 Tundra | `Winchester70` |
| SV-98 | `SV98` |
| SSG 82 | `SSG82` |
| RAK-37 | `PM73Rak` |
| Pioneer / Scout | `Scout` (renamed Steyr Scout) |
| Mlock-91 | `Glock19` |
| Kolt 1911 | `Colt1911` |
| Deagle | `Deagle` · Revolver → `Magnum` |
| BK-18 (rifle) | `Izh18` |
| BK-43 (double) | `Izh43Shotgun` · single-barrel → `Izh18Shotgun` |
| BK-133 (pump) | `Mp133Shotgun` |
| Repeater Carbine | `Repeater` |
| VSD | `SVD` |
| SG5-K | `MP5K` · USG-45 → `UMP45` |
| CR-61 Skorpion | `CZ61` · Bizon → `PP19` |
| IJ-70 | `MakarovIJ70` · FX-45 → `FNX45` |
| Sporter 22 | `Ruger1022` |
| CR-75 / CR-527 / CR-550 | `CZ75` / `CZ527` / `CZ550` |
| LAR | `FAL` |
| AUR A1 / AUR AX | `Aug` / `AugShort` |
| LE-MAS | `FAMAS` |
| KA-M / KA-101 / KA-74 / KAS-74U | `AKM` / `AK101` / `AK74` / `AKS74U` |
| SK 59/66 | `SKS` |

## Calibers and magazines

Every row read from `magazines[]` / `chamberableFrom[]` in `CfgWeapons` — not from memory.
"internal" = no external magazine, the AI needs loose ammo in cargo.

| Class | Caliber | Magazine |
|---|---|---|
| `Magnum` | .357 | internal (`Mag_357Speedloader_6Rnd`) |
| `Repeater` | .357 | internal |
| `Deagle` | .357 | `Mag_Deagle_9rnd` |
| `MakarovIJ70` | .380 | `Mag_IJ70_8Rnd` |
| `PP19` | .380 | `Mag_PP19_64Rnd` |
| `PM73Rak` | .380 | `Mag_PM73_25Rnd` / `_15Rnd` |
| `CZ75` | 9×19 | `Mag_CZ75_15Rnd` |
| `Glock19` | 9×19 | `Mag_Glock_15Rnd` |
| `MP5K` | 9×19 | `Mag_MP5_30Rnd` / `_15Rnd` |
| `Colt1911` | .45 | `Mag_1911_7Rnd` |
| `FNX45` | .45 | `Mag_FNX45_15Rnd` |
| `Ruger1022` | .22 | `Mag_Ruger1022_15Rnd` / `_30Rnd` |
| `Izh18Shotgun` · `Izh43Shotgun` · `Mp133Shotgun` · `R12` | 12ga | internal |
| `Saiga` | 12ga | `Mag_Saiga_8Rnd` / `_5Rnd` |
| `Izh18` | 7.62×39 | internal |
| `SKS` | 7.62×39 | internal (`Mag_CLIP762x39_10Rnd`) |
| `CZ527` | 7.62×39 | `Mag_CZ527_5rnd` |
| `AKM` | 7.62×39 | `Mag_AKM_30Rnd` / `_Palm30Rnd` |
| `AK74` · `AKS74U` | 5.45×39 | `Mag_AK74_30Rnd` (`_45Rnd`) |
| `SSG82` | 5.45×39 | `Mag_SSG82_5rnd` |
| `AK101` | 5.56 | `Mag_AK101_30Rnd` |
| `M4A1` · `M16A2` | 5.56 | `Mag_STANAG_30Rnd` |
| `Aug` | 5.56 | `Mag_Aug_30Rnd` **or** `Mag_STANAG_30Rnd` |
| `AugShort` | 5.56 | `Mag_Aug_30Rnd` |
| `FAMAS` | 5.56 | `Mag_FAMAS_25Rnd` |
| **`Scout`** | **5.56** | `Mag_Scout_5Rnd` |
| `Winchester70` · `B95` | .308 | internal |
| `Longhorn` | .308 | internal |
| `M14` | .308 | `Mag_M14_20Rnd` / `_10Rnd` |
| `FAL` | .308 | `Mag_FAL_20Rnd` |
| `SCARH` / `SCARH_Black` | .308 | `Mag_SCARH_20Rnd` (`_Black`) |
| `Mosin9130` | 7.62×54 | internal |
| `SVD` | 7.62×54 | `Mag_SVD_10Rnd` |
| `SV98` | 7.62×54 | `Mag_SV98_10Rnd` |
| `VSS` · `ASVAL` · `Vikhr` | 9×39 | `Mag_VSS_10Rnd` / `Mag_VAL_20Rnd` / `Mag_Vikhr_30Rnd` |

**`Scout` is 5.56, not .308.** BI rechambered it; this file said .308 until 2026-07-29, and the
loadouts were shipping `Ammo_308Win` with it in both Hunter and West.

## Optic mount categories

An optic only fits if its `inventorySlot[]` appears in the weapon's `attachments[]`. Mismatches fail
silently. `./validate.py --slots` checks this.

Matching is case-insensitive: `Aug` and `ASVAL` declare `WeaponOptics`, `M4A1` declares
`weaponOptics`, and they are the same category.

| Mount | Optics | Weapons |
|---|---|---|
| `weaponOpticsAK` | `PSO1Optic`, `PSO11Optic`, `PSO6Optic`, `KobraOptic`, `KashtanOptic`, `KazuarOptic`, `GrozaOptic` | `AKM`, `AK74`, `AK101`, `SVD`, `VSS`, `Vikhr`, `Saiga`, `PP19` |
| `weaponOptics` | `M68Optic`, `ACOGOptic`, `ACOGOptic_6x`, `MK4Optic_*`, `ReflexOptic`, `StarlightOptic`, `BUISOptic` | `M4A1`, `SV98`, `Scout`, `M14`, `FAL`, `Aug`, `ASVAL`, `MP5K`, `R12`, `SCARH`, `SCARH_Black` |
| `weaponOpticsHunting` | `HuntingOptic`, `SportingOptic` | `Winchester70`, `B95`, `CZ527`, `Ruger1022` |
| `weaponOpticsMosin` | `PUScopeOptic` | `Mosin9130`, `SKS` |
| `weaponOpticsAug` | `AugOptic`, `SSG82Optic` | `AugShort`, `SSG82` |
| `pistolOptics` | `FNP45_MRDSOptic` | `CZ75`, `FNX45`, `Glock19`, `Mp133Shotgun` |
| `weaponOpticsCrossbow` | `PistolOptic` | `Deagle` |
| **none** | — | `M16A2`, `FAMAS`, `Colt1911`, `Magnum`, `Repeater`, `Izh18`, `Izh18Shotgun`, `Izh43Shotgun`, `PM73Rak` |

Two that catch people out: **`M16A2` and `FAMAS` have no optics category at all**, so any optic on
them is a no-op — and `ASVAL` takes generic `weaponOptics` while its `VSS` sibling takes
`weaponOpticsAK`, so a `PSO1Optic` fits one and not the other.

## Method

1. **Rarity** — `types.xml`, `<type name="…">` with `<category name="weapons"/>`. Confirm the file
   still matches stock BI Central Economy by md5 before trusting the grades.
2. **Calibers, magazines, optic mounts** — `./fetch_slotmap.py`, which reads `magazines[]`,
   `chamberableFrom[]` and `attachments[]` from the vanilla configs. Weapons live in **per-weapon
   subfolders** (`weapons_firearms/sv98/config.cpp`); the folder-level `config.cpp` is a stub.
3. Casing matters when searching (`Mag_Aug_30Rnd`, not `Mag_AUG_30Rnd`), though the engine resolves
   class names case-insensitively at spawn. BI's own files disagree with themselves —
   `Mag_SV98_10Rnd` in types.xml vs `Mag_SV98_10rnd` in `magazines[]`.
4. `SCARH` / `SCARH_Black` are **absent from the config dump**. Caliber, fire mode, capacity and
   optic mount all come from play experience (.308, full-auto, 20rd, generic `weaponOptics`) and are
   pinned in `fetch_slotmap.py`'s `OVERRIDES` so the validator can check them. Anything else added
   there should carry the same provenance note.
5. **Projectile damage is not obtainable from any reachable source.** It lives in `CfgAmmo` under
   `Bullet_*`, which is shipped as `config.bin` only — not in `dz/config.cpp`, not in
   `weapons_ammunition/config.cpp` (that file defines the cartridge *items*, pointing at
   `ammo="Bullet_45ACP"` and so on, with no damage figures). [wobo.tools](https://wobo.tools/dayz/ammo)
   publishes the numbers but sits behind a Cloudflare bot challenge, so it can't be scraped —
   paste them in by hand if exact figures are ever needed. Until then the caliber *class* grouping
   above is the proxy, and it is config-derived.
