# Sasha Callum thumbs (Glove80)

QWERTY keymap for the [MoErgo Layout Editor](https://my.moergo.com/glove80/#/edit). No home-row mods, no hold-tap.

Uses the MoErgo JSON envelope and Magic layer. The factory test `&to 3` on Magic `RH C6R6` is cleared so it cannot jump into Mods R.

| Thumb | Hold | Alone |
| --- | --- | --- |
| 1 left T1+T4 | Cursor | — |
| 2 left T2+T5 | ModsL | — |
| 3 right T2+T5 | ModsR | — |
| 4 right T1+T4 | — | Space |
| 2+3 | Symbol (both held; not sticky) | |
| 1+3 | Number (both held; not sticky) | |
| Magic corners | Magic | LED indicators |

Both thumb clusters (`T1`/`T2` and `T4`/`T5`) do the same two jobs per hand.

## Import

1. Open [my.moergo.com](https://my.moergo.com/glove80/#/edit) and log in.
2. Settings → enable **Local Backup and Restore**.
3. Start a new layout (or open the editor workspace).
4. Bottom left → **Import** → choose `keymap.json`.
5. Check the seven layers and thumb keys.
6. **Save and Build**, flash the `.uf2`.

**Custom Defined Behaviors** holds the conditional layers (Symbol / Number). Don’t clear it.

## Layers

Higher number wins when two layers are held.

0. **QWERTY** — letters
1. **ModsL** — left home row GUI Alt Ctrl Shift; `Q`–`T` = F1–F5, `G` = F11
2. **ModsR** — right home row Shift Ctrl Alt GUI; `Y`–`P` = F6–F10, `H` = F12
3. **Cursor** — arrows on `HJKL`, Tab / Bspc / Enter
4. **Symbol** — same symbol wells as the old layout
5. **Number** — numpad on the right (`Y` = `%`); no `*` `/` `.`
6. **Magic** — Bluetooth, RGB, bootloader (name must stay `Magic`)
