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

The game itself is never committed. Point the tools at your install:

```bash
export WMD_INSTALL="N:/SteamLibrary/steamapps/common/WormsWMD"
```

## Legal

Tooling only. No game assets are redistributed here. Worms W.M.D. is
copyright Team17.
