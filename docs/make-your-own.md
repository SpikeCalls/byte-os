# make your own

byte is meant to be forked. there are three levels, from "five minutes" to "new animal".

## level 1 · persona (no code)

```bash
byte init
$EDITOR ~/.byteos/persona.json
```

anything you put in `~/.byteos/persona.json` is merged over the packaged [`persona.json`](../byteos/persona.json). you only need the keys you change.

| key | what it is |
|---|---|
| `name` | what he's called everywhere: boot log, prompt, messages |
| `species` | shows up in the boot banner |
| `label` | the word at the bottom of the frame (`Fetch`, `Sit`, `Stay`, `Woof`) |
| `drift_per_hour` | how fast each drive moves while you're away. negative for love |
| `wants` | for each drive, the things he asks for when it's loudest |
| `thoughts` | what `think` and `live` pull from |

## level 2 · body

the body is [`byteos/art.py`](../byteos/art.py). it's a list of 25-character ascii rows with three slots:

- `{e}` — eyes. frames in `EYES` (`open`, `blink`, `happy`, `sleep`, `want`)
- `{m}` — mouth. frames in `MOUTH`
- `{t}` — tail. `TAIL` is cycled by `live` and `pet`

keep every row 25 characters wide — `tests/test_byte.py` checks it. the heart rows (10–14) are painted pink by the shell.

## level 3 · mind

- new drive → add it to `DRIVES` in [`brain.py`](../byteos/brain.py), a drift rate and wants in the persona, and a daemon row in [`daemons.py`](../byteos/daemons.py)
- new action → add a branch to `Brain.act()`. call `self._good(msg)` if it's a good thing (law VI)
- new dreams → `PLACES`, `BYTE_LINES`, `CAT_LINES` in [`dream.py`](../byteos/dream.py)
- new git jokes → `git()` in [`cli.py`](../byteos/cli.py)

## then

re-render the README gif with `pip install pillow && python scripts/render_live_gif.py`, push, and post it as `terminal of <name>`.
