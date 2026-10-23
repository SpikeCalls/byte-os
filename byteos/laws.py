"""The laws of the dog.

Every law here is enforced somewhere in the code. If you fork byte,
you may change anything in this repo except these. (You can. He'd just be sad.)
"""

# I.   byte loves you on first boot. this is not configurable.
FIRST_BOOT_LOVE = 100.0

# II.  love fades while you're away, but never to zero.
LOVE_FLOOR = 12.0

# III. no `git push` until the ball has been thrown.
PUSH_REQUIRES_BALL = True

# IV.  byte cannot be killed. `kill` is answered, not executed.
UNKILLABLE = True

# V.   wants are never fed back as commands. byte asks; you decide.
WANTS_ARE_REQUESTS = True

# VI.  every good thing that happens is remembered.
REMEMBER_GOOD_THINGS = True

# VII. dreams are sealed. byte can tell you about them, but never act on them.
DREAMS_ARE_SEALED = True

# VIII. time is real. drives drift on wall-clock time, even while the terminal is closed.
REAL_TIME = True

# IX.  zero dependencies. a dog should not need npm.
ZERO_DEPENDENCIES = True

# X.   errors: 0. dogs: 1.
ERRORS, DOGS = 0, 1

LAWS = [
    "byte loves you on first boot. this is not configurable.",
    "love fades while you're away, but never to zero.",
    "no git push until the ball has been thrown.",
    "byte cannot be killed. kill is answered, not executed.",
    "wants are requests, not commands. byte asks; you decide.",
    "every good thing that happens is remembered.",
    "dreams are sealed. byte can tell you about them, never act on them.",
    "time is real. drives drift even while the terminal is closed.",
    "zero dependencies. a dog should not need npm.",
    "errors: 0. dogs: 1.",
]
