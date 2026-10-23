import os
import tempfile
import unittest

os.environ["BYTE_HOME"] = tempfile.mkdtemp()
os.environ["BYTE_FAST"] = "1"

from byteos import art  # noqa: E402
from byteos.brain import Brain  # noqa: E402
from byteos import cli  # noqa: E402


class TestArt(unittest.TestCase):
    def test_rows_same_width(self):
        for eyes in art.EYES:
            for tail in range(len(art.TAIL)):
                rows = art.render(eyes=eyes, tail=tail)
                self.assertEqual({len(r) for r in rows}, {25})

    def test_frame_has_label(self):
        self.assertIn("Fetch", art.frame()[-1])


class TestBrain(unittest.TestCase):
    def test_time_makes_him_want_things(self):
        b = Brain(boredom=10, last_seen=0)
        b.catch_up(now=3600 * 5)
        self.assertGreater(b.boredom, 10)

    def test_love_fades_without_you(self):
        b = Brain(love=90, last_seen=0)
        b.catch_up(now=3600 * 5)
        self.assertLess(b.love, 90)

    def test_fetch_cures_boredom(self):
        b = Brain(boredom=90)
        b.act("fetch")
        self.assertLess(b.boredom, 90)
        self.assertEqual(b.balls_fetched, 1)

    def test_wants_are_ranked(self):
        b = Brain(hunger=99, boredom=1, love=99, energy=1, curiosity=1)
        self.assertEqual(b.wants(n=1)[0][0], "hunger")

    def test_save_and_load(self):
        b = Brain()
        b.act("treat")
        b.save()
        self.assertEqual(Brain.load().treats_eaten, 1)


class TestShell(unittest.TestCase):
    def test_commands_dont_crash(self):
        b = Brain()
        for c in ["help", "wants", "status", "think", "look", "pet", "feed", "fetch",
                  "walk", "sit", "git push", "sudo rm -rf /", "asdf"]:
            self.assertTrue(cli.handle(b, c))
        self.assertFalse(cli.handle(b, "exit"))


if __name__ == "__main__":
    unittest.main()
