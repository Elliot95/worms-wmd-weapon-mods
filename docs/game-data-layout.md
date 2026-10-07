# Worms W.M.D. - on-disk data layout

Reconnaissance notes. Everything here was verified against a live install on
2026-10-07, not taken from documentation.

## Install

Steam appid **327030**. The install is **5.37 GB** at:

```
<SteamLibrary>\steamapps\common\WormsWMD
```

where `<SteamLibrary>` is any Steam library root, not necessarily the one beside
Steam itself - check `steamapps\libraryfolders.vdf` for the list.
`appmanifest_327030.acf` sits in that library's `steamapps\` with
`StateFlags 4` (fully installed).

Worth checking for orphans: if the game was ever moved between libraries,
a partial copy can be left behind in the old one holding `CommonData/`,
`WorkshopContent/` and `WorkshopLevels/`. It is not read by the game, and
`WorkshopLevels` alone can be over a gigabyte. Compare timestamps against the
library named in `libraryfolders.vdf` to tell which is live.

## Top-level directories

| Dir | Size | Notes |
|---|---|---|
| `wads/` | 3.20 GB | `uidata_0/1/2.wad` - ~1 GB each |
| `DataPC/` | 1.05 GB | `Bundles/`, `Objects/`, `Language/` |
| `WorkshopLevels/` | 1.27 GB | Subscribed custom maps |
| `uidata/` | 614 MB | `video/` |
| `Audio/` | 438 MB | |
| `CommonData/` | 754 KB | `scripts.rpg`, `Scripts/SceneScript.xss` |
| `WorkshopContent/` | 3.3 MB | Custom hats - `.ugc` + `CustomUGC.udf` + `.tga` |

## Bundles - `DataPC/Bundles/`

20 files. Per-theatre bundles (`England`, `Hell`, `Space`, `Jungle`, `Mexico`,
`China`, `Russia`, `Usa`, `France`, `Fort`) plus `In-Game.bdl`,
`SuperBundle.bdl`, `Core.bdl`, `Startup.bdl`, `WorldSystem.bdl`, `Font.bdl`,
`DevOnly.bdl`, and loose `.xom` files.

### Where the weapons are - and are NOT

An ASCII scan for weapon names makes `In-Game.bdl` look like the weapon
bundle (`Weapon`=324, `Grenade`=714, `Sheep`=330, `Bazooka`=69). **That read is
wrong.** A full-file TYPE scan plus string-context inspection shows what those
hits actually are.

All 48 XOM classes declared in `In-Game.bdl` are rendering, mesh, and
animation types - `XShader`, `XTextureMap`, `XGeometry`, `XMeshDescriptor`,
`XPsSkinShape`, `XAnimClipLibrary`, `XJointTransform`. **There is no weapon,
stat, or gameplay class anywhere in it.**

The weapon-name strings are art references:

```
//t17proj4/Main/Art/Weapons/Textures/WE_Bazooka_01.tga   <- source texture path
WE_HolyHandGrenade_01Shape                               <- mesh / shape name
BackingShape_Minigun_Mat                                 <- material name
AimBazooka  AimGrenade  AimHHG  AimMinigun  AimShotgun   <- animation clips
```

(`//t17proj4/...` is Team17's internal build share, left in the shipped data.)

Every weapon-name hit sits in the payload, none in the header schema.

**Conclusion:** bundles hold weapon *art and animation*, not weapon *stats*.
That splits the work in two:

| Mod type | Target |
|---|---|
| Models, textures, animation | `DataPC/Bundles/In-Game.bdl` |
| Damage, radius, fuse, ammo, behaviour | **not in the bundles** - see below |

### Hunting the stats - `scripts.rpg` is the prime suspect

`CommonData/scripts.rpg` (713 KB) is the leading candidate: named "scripts",
sits beside the plain-text `SceneScript.xss`, and is high-entropy with no
readable strings - so encrypted or compressed. Secondary candidates are the
13 MB of loose strings in `Worms W.M.D.exe` and `wads/uidata_*.wad`.

Until `scripts.rpg` is cracked, stat modding has no confirmed entry point.
Art-side modding does.

## The XOM container format

`Core.bdl` is only 374 bytes, which makes it the ideal format specimen. Its
header, ASCII-rendered:

```
MOIK ... TYPE ... XBaseResourceDescriptor
         TYPE ... XCustomDescriptor
         TYPE ... XGraphSet
         GUID ... SCHM ... STRS ... MovieInstance
```

Observations:

- Magic is **`MOIK`** - the Team17 XOM container, same lineage as Worms 4:
  Mayhem and Worms Ultimate Mayhem. Community XOM tooling for those games is
  therefore a plausible starting reference.
- Section-tagged layout: repeated `TYPE` blocks declare class names
  (`XBaseResourceDescriptor`, `XCustomDescriptor`, `XGraphSet`), then `GUID`,
  `SCHM` (schema), `STRS` (string table).
- It is **schema-carrying**: `SCHM` + the `TYPE` declarations mean a reader can
  be written generically rather than hardcoding per-file offsets. This is the
  single most useful property for this project.

### Open questions

- [ ] Exact `TYPE`/`SCHM`/`STRS` binary field layout (offsets, widths, endianness)
- [ ] Are `.bdl` files plain XOM containers, or XOM wrapped in an archive?
- [ ] Which XOM class holds weapon stats, and its field names
- [ ] Repacking: does the game validate bundle checksums?

## Other files

- **`CommonData/scripts.rpg`** (713 KB) - high-entropy, no readable strings.
  Encrypted or compressed. Not a quick win.
- **`CommonData/Scripts/SceneScript.xss`** (22 KB) - **plain text**, readable.
  A render-pipeline DSL (`Define Surface 'DRS_Depth' Format 'DEPTH32' ...`),
  deferred-rendering setup. Not weapons, but proof the engine reads
  human-editable script files.
- **`CommonData/local.cfg`** - plain-text launch/display settings
  (`/W:2560`, `/H:1440`, `/VSYNC:1`, `/AA:Fxaa`, `/WIN`, `/WaterQuality:High`).
  Trivially editable.

## Workshop content shape

A custom hat, as the game stores it:

```
WorkshopContent/
  <id>.ugc                  # item metadata
  <id>.png                  # thumbnail
  <id>/CustomUGC.udf        # ~1.1 KB descriptor
  <id>/ImportedHat_<hash>.tga  # 66,086 B - fixed size, so fixed dimensions
```

Custom maps follow the same pattern under `WorkshopLevels/` with
`Landscape_<hash>.bkw` payloads (134-335 MB each).

`CustomUGC.udf` at ~1 KB is a small, probably readable descriptor - worth
dumping early, since it reveals how the game expects user content to declare
itself.
