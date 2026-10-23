# architecture

byte has no event loop and no background process. everything is derived from two numbers: the state on disk and the current time.

## lifecycle of a command

```
$ byte fetch
   │
   ├─ Brain.load()            read ~/.byteos/state.json (or a fresh, loving brain — law I)
   ├─ Brain.catch_up(now)     drift every drive by rate × hours since last_seen (law VIII)
   ├─ cli.handle("fetch")     route the verb
   │    └─ Brain.act("fetch") boredom −40, energy −20, balls_since_push +1
   │         └─ _good(msg)    memory.remember(msg) (law VI)
   └─ Brain.save()            write state, last_seen = now
```

## why no daemon process

the daemons in `ps` are real in the sense that matters: each one is a drift rate applied to elapsed time. a dog that only exists when you open the terminal, but has been wanting things the whole time — that's the point.

## wants vs actions

`Brain.wants()` returns strings. nothing in the codebase turns a want into an action (law V). the only path to changing byte's state is a verb typed by a human.

## memory

`memory.log` is append-only. `recall(query)` scores each line by the number of shared non-stopwords with the query and returns the best matches, newest first on ties.

## dreams

`dream()` is a pure function of a seed. `seal()` writes it to `dreams/` and returns the path. nothing ever reads that folder (law VII).

## live mode

`byte live` deep-copies the brain and simulates 10 minutes of drift per second on the copy, redrawing in place with ANSI cursor movement. the real dog keeps real time.
