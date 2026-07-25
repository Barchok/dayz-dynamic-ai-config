# Weapon reference — classes, calibers, tier placement

Reference for the guns used across the loadouts: the trademark-safe **display name → config class**
mapping (the thing that trips everyone up), caliber, magazine, and which tier(s) each sits in. Every
class here is verified present in the server's `types.xml`.

## Display name ↔ config class (the traps)

In-game display names are trademark-safe and do **not** match config classes. Loadouts and `types.xml`
use the class. Always resolve display → class before editing a loadout — a wrong name won't crash, it
just silently never spawns.

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

## Roster by tier placement

`Tiers` = which loadout files spawn the gun. Internal-mag guns take loose ammo in cargo (no external
magazine).

### Pistols & sidearms
| Display | Class | Ammo | Magazine | Tiers |
|---|---|---|---|---|
| Revolver | `Magnum` | .357 | internal | Civilian |
| Deagle | `Deagle` | .357 | `Mag_Deagle_9rnd` | Civilian |
| IJ-70 | `MakarovIJ70` | .380 | `Mag_IJ70_8Rnd` | Survivor, Raider, Gorka, Soviet, East, Hazmat |
| Mlock-91 | `Glock19` | 9mm | `Mag_Glock_15Rnd` | Raider |
| CR-75 | `CZ75` | 9mm | `Mag_CZ75_15Rnd` | Raider, Gorka, East |
| FX-45 | `FNX45` | .45 | `Mag_FNX45_15Rnd` | West |
| Kolt 1911 | `Colt1911` | .45 | `Mag_1911_7Rnd` | Survivor, West |
| Longhorn | `Longhorn` | .308 | internal | Survivor |

### SMGs
| Display | Class | Ammo | Magazine | Tiers |
|---|---|---|---|---|
| SG5-K | `MP5K` | 9mm | `Mag_MP5_30Rnd` | Raider |
| Bizon | `PP19` | .380 | `Mag_PP19_64Rnd` | Soviet |
| RAK-37 | `PM73Rak` | .380 | `Mag_PM73_25Rnd` | Survivor |

### Shotguns
| Display | Class | Ammo | Magazine | Tiers |
|---|---|---|---|---|
| single-barrel | `Izh18Shotgun` | 12ga | internal | Civilian |
| BK-43 double | `Izh43Shotgun` | 12ga | internal 2rd | Survivor |
| BK-133 pump | `Mp133Shotgun` | 12ga | internal | Raider |
| Vaiga | `Saiga` | 12ga | `Mag_Saiga_8Rnd` | Hunter |
| R12 | `R12` | 12ga | internal | Hunter |

### Assault rifles
| Display | Class | Ammo | Magazine | Tiers |
|---|---|---|---|---|
| KA-M | `AKM` | 7.62×39 | `Mag_AKM_30Rnd` (Drum75/Palm30) | Raider, Gorka, Soviet, Hazmat |
| KA-101 | `AK101` | 5.56 | `Mag_AK101_30Rnd` | East |
| KA-74 | `AK74` | 5.45 | `Mag_AK74_30Rnd` (45Rnd) | Raider, Gorka, East |
| KAS-74U | `AKS74U` | 5.45 | `Mag_AK74_30Rnd` | Raider, Soviet, East, Hazmat |
| M4-A1 | `M4A1` | 5.56 | `Mag_STANAG_30Rnd` | West, Hazmat, Elite |
| M16-A2 | `M16A2` | 5.56 | `Mag_STANAG_30Rnd` | West |
| AUR A1 / AX | `Aug` / `AugShort` | 5.56 | `Mag_Aug_30Rnd` | West |
| LE-MAS | `FAMAS` | 5.56 | `Mag_FAMAS_25Rnd` | West |
| SVAL | `ASVAL` | 9×39 | `Mag_VAL_20Rnd` | East, Elite |
| Vikhr | `Vikhr` | 9×39 | `Mag_Vikhr_30Rnd` | Hunter |

### Battle rifles
| Display | Class | Ammo | Magazine | Tiers |
|---|---|---|---|---|
| LAR | `FAL` | .308 | `Mag_FAL_20Rnd` | Elite |
| SCR-17 | `SCARH` / `SCARH_Black` | .308 | `Mag_SCARH_20Rnd` (`_Black`) | Elite |

### Bolt-action & marksman
| Display | Class | Ammo | Magazine | Tiers |
|---|---|---|---|---|
| SK 59/66 | `SKS` | 7.62×39 | internal 10rd | Survivor, Raider, Gorka, Soviet |
| CR-527 | `CZ527` | 7.62×39 | `Mag_CZ527_5rnd` | Survivor, Raider |
| Repeater | `Repeater` | .357 | internal | Survivor |
| BK-18 | `Izh18` | 7.62×39 | internal | Survivor |
| Sporter 22 | `Ruger1022` | .22 | `Mag_Ruger1022_15Rnd` | Survivor |
| Mosin 91/30 | `Mosin9130` | 7.62×54 | internal | Survivor, Hunter |
| Blaze | `B95` | .308 | internal 2rd | Hunter |
| M70 Tundra | `Winchester70` | .308 | internal | Hunter |
| Scout | `Scout` | .308 | `Mag_Scout_5Rnd` | Hunter, West |
| SSG 82 | `SSG82` | 5.45 | `Mag_SSG82_5rnd` | Hunter |
| VSD | `SVD` | 7.62×54 | `Mag_SVD_10Rnd` | Gorka, Soviet, East, Hazmat |
| VSS | `VSS` | 9×39 | `Mag_VSS_10Rnd` | East, Elite |
| DMR | `M14` | .308 | `Mag_M14_20Rnd` | Elite |
| SV-98 | `SV98` | 7.62×54 | `Mag_SV98_10Rnd` | Elite |

## Ground-truth method

Pull the definitive weapon + magazine class list from the **server's own
`mpmissions/…/db/types.xml`** (`<type name="…">` with `<category name="weapons"/>`), and read each
gun's `<value name="TierN"/>` + `<usage>` to place it at its real loot tier. Public repos (BI Central
Economy, Expansion GitHub) lag the Workshop build and miss new guns — `types.xml` is the only ground
truth. Casing matters when searching (`Mag_Aug_30Rnd`, not `Mag_AUG_30Rnd`), though the engine itself
resolves class names case-insensitively at spawn.
