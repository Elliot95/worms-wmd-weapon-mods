# Can weapon behaviour be modded?

Short answer: **not through data files.** Weapon behaviour is compiled into
`Worms W.M.D.exe`. Changing it means patching the binary.

This page records how that was established, so nobody re-treads it.

## What was ruled out

| Candidate | Result |
|---|---|
| `.bdl` bundles | **No.** Zero bundles declare a weapon/payload XOM class. All 48 classes in `In-Game.bdl` are render/mesh/animation. Its weapon strings are art paths and animation clips. |
| `wads/*.wad` | **No.** No payload class names present. |
| `CommonData/scripts.rpg` | **Encrypted.** See below. |
| Anywhere else on disk | **No.** `BananaBombPayload`, `PoisonPayload`, `GasGrenadePayload` and `kPayload_BananaBomb` appear in **exactly one file** on the whole install: the exe. |

## `scripts.rpg` is encrypted, not compressed

713 KB, and the exe references both `/scripts.rpg` and a `/Scripts/*.txt` tree
that does **not** exist as loose files - so it is very likely the archive
holding them (`Equip/Defaults.txt`, `Crates.txt`, `SchemeOptions.txt`,
`WeaponPanel.txt`, `AI/WeaponPriorityWeights.txt`, and ~30 more).

Measured:

- Shannon entropy **7.9997 bits/byte** (max is 8.0)
- All 256 byte values present, near-uniform (top byte 0.412% vs 0.391% uniform)
- zlib / raw deflate / gzip / bz2 / lzma all fail at offset 0
- No zlib, gzip, bzip2, xz or lz4 header anywhere in the file
- Index of coincidence **0.0039** at strides 1/2/4/8/16/32 - i.e. identical to
  random, so **not** a short repeating XOR

That is a real cipher. The key must be in the exe, since the game decrypts at
runtime, but recovering it is disassembly work.

Note: even decrypted, those configs look like loadout / UI / AI-weighting data,
**not** payload physics. `FlameBurnRadius1` and `PoisonMaxRadius` are reflection
strings in the exe, next to compiled values.

## The payload enum

91 entries extracted to [`../data/weapons/payload-enum.json`](../data/weapons/payload-enum.json).

> **Caveat:** that order is *string-table* order. It usually matches enum order
> but is **not** verified against the enum's numeric values. Confirm in a
> disassembler before trusting an index.

Relevant indices:

| Index | Payload |
|---|---|
| 6 | `kPayload_BananaBomb` |
| 7 | `kPayload_BananaFragment` |
| 15 | `kPayload_Poison` (the lingering gas cloud) |
| 20 | `kPayload_FlameThrower` |
| 22 | `kPayload_OilFire` (lingering flames) |
| 33 | `kPayload_GasGrenade` |
| 73 | `kPayload_TurkeyBomb` |

## The combination pattern already exists in-game

The engine already supports "base weapon + lingering area effect". These ship
as **crafted** weapons (W.M.D. has a crafting system; `BananaBombSeeds` is an
ingredient):

| Payload | Pattern |
|---|---|
| `kPayload_PoisonedDynamite` (37) | explosive **+ gas** |
| `kPayload_StinkingCarpetBomb` (42) | explosive **+ gas** |
| `kPayload_BarbecuedSheep` (38) | animal **+ fire** |
| `kPayload_SuperFlatulenceSheep` (41) | animal **+ gas** |
| `kPayload_SuperBananaBomb` (45) | banana, upgraded (bigger - *not* gas or fire) |

So a gas-dropping or flame-dropping banana is not a new mechanic - it is a
recombination of parts that already exist. There is just no data-level way to
author the combination, and no shipped banana variant that does it.

## What a real implementation would take

1. Load the exe in Ghidra / IDA.
2. Find `BananaBombPayload`'s detonation routine - the C++ RTTI string
   `?AVBananaBombPayload@@` gives the vtable, which gives the methods.
3. Find where it spawns `kPayload_BananaFragment` (7) and change the constant
   to `kPayload_Poison` (15) or `kPayload_OilFire` (22).
4. Use `PoisonedDynamite` as the reference implementation - it already does
   explosive-spawns-gas, so its routine shows the expected call shape.
5. Patch, and keep the original exe.

### Practical caveats

- **Steam will revert it.** "Verify integrity of game files" restores the exe.
- **Multiplayer will desync** - other players do not have your change. Treat
  this as single-player only.
- Patching a vtable constant is not guaranteed to be enough; the fragment count,
  spawn velocities and fuse are likely set in the same routine and may need
  adjusting for the result to behave sensibly.

## Easiest path that needs no modding

Crafting. `PoisonedDynamite`, `StinkingCarpetBomb`, `BarbecuedSheep` and
`SuperFlatulenceSheep` are obtainable in-game and already deliver
explosive-plus-gas and animal-plus-fire behaviour.
