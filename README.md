# worms-wmd-weapon-mods

Tooling for building **Worms W.M.D.** weapon mods on PC, aimed at the
replication-heavy part of the job: generating many weapon variants from a
small number of templates instead of hand-editing each one.

## Why this exists

Weapon definitions in Worms W.M.D. live in Team17's **XOM** typed-object
containers, packed inside `.bdl` bundles. Authoring a weapon by hand is
repetitive and error-prone. The goal here is:

1. **Read** the game's existing weapon definitions into plain JSON/YAML.
2. **Template** them, so a family of weapons is one spec plus a table of values.
3. **Write** valid XOM data back out, ready to pack.

## Status

Early. Nothing is implemented yet. What exists is verified reconnaissance of
the game's on-disk data layout - see [`docs/game-data-layout.md`](docs/game-data-layout.md).

## Layout

| Path | Purpose |
|---|---|
| `docs/` | Findings on the game's file formats |
| `tools/wmdmod/` | Python package - XOM read/write, templating |
| `data/weapons/` | Weapon specs we author (source of truth, committed) |
| `out/` | Generated artifacts (gitignored) |

## Getting started

Requires Python 3.10+. The game itself is never committed - point the tools
at your own install.

PowerShell:

```powershell
$env:WMD_INSTALL = "D:\SteamLibrary\steamapps\common\WormsWMD"
python tools\probe.py
```

bash:

```bash
export WMD_INSTALL="/d/SteamLibrary/steamapps/common/WormsWMD"
python tools/probe.py
```

If you do not know which library holds it, look for `appmanifest_327030.acf`
under each root listed in `steamapps/libraryfolders.vdf`.

`probe.py` prints each bundle's XOM section structure and class inventory.

## Legal

Tooling only. No game assets are redistributed here. Worms W.M.D. is
copyright Team17.
