import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ["BYTE_HOME"] = tempfile.mkdtemp()
os.environ["BYTE_FAST"] = "1"

from byteos import art, cli, laws, memory, persona  # noqa: E402
from byteos.brain import Brain  # noqa: E402
from byteos.daemons import table  # noqa: E402
from byteos.dream import dream, seal  # noqa: E402


class TestArt(unittest.TestCase):
    def test_rows_same_width(self):
        for eyes in art.EYES:
            for tail in range(len(art.TAIL)):
                self.assertEqual({len(r) for r in art.render(eyes=eyes, tail=tail)}, {25})

    def test_frame_has_label(self):
        self.assertIn("Fetch", art.frame()[-1])


class TestLaws(unittest.TestCase):
    def test_I_loves_you_on_first_boot(self):
        self.assertEqual(Brain().love, laws.FIRST_BOOT_LOVE)

    def test_II_love_never_hits_zero(self):
        b = Brain(love=50, last_seen=0)
        b.catch_up(now=3600 * 24 * 365)
        self.assertEqual(b.love, laws.LOVE_FLOOR)

    def test_III_no_push_without_ball(self):
        b = Brain()
        self.assertFalse(b.push())
        b.act("fetch")
        self.assertTrue(b.push())
        self.assertFalse(b.push())

    def test_VIII_time_is_real(self):
        b = Brain(boredom=10, last_seen=0)
        b.catch_up(now=3600 * 5)
        self.assertGreater(b.boredom, 10)


class TestBrain(unittest.TestCase):
    def test_fetch_cures_boredom(self):
        b = Brain(boredom=90)
        b.act("fetch")
        self.assertLess(b.boredom, 90)

    def test_wants_are_ranked(self):
        b = Brain(hunger=99, boredom=1, love=99, energy=1, curiosity=1)
        self.assertEqual(b.wants(n=1)[0][0], "hunger")

    def test_save_and_load(self):
        b = Brain()
        b.act("treat")
        b.save()
        self.assertEqual(Brain.load().treats_eaten, 1)


class TestSubsystems(unittest.TestCase):
    def test_memory_recall_by_overlap(self):
        memory.remember("ball returned. slightly wetter")
        memory.remember("walk complete. sniffed 14 trees")
        self.assertIn("ball", memory.recall("where is the ball")[0])

    def test_dream_is_sealed_to_disk(self):
        p = seal(dream(seed=1))
        self.assertTrue(p.exists())
        self.assertIn("cat  >", p.read_text())

    def test_process_table(self):
        names = [r[1] for r in table(Brain())]
        self.assertEqual(names[0], "byte")
        self.assertIn("loved", names)

    def test_persona_init_and_override(self):
        p, created = persona.init()
        self.assertTrue(created)
        data = json.loads(p.read_text())
        data["name"] = "bork"
        p.write_text(json.dumps(data))
        self.assertEqual(persona.load()["name"], "bork")
        p.unlink()


class TestShell(unittest.TestCase):
    def test_commands_dont_crash(self):
        b = Brain()
        for c in ["help", "wants", "ps", "status", "think", "look", "live", "dream", "recall ball",
                  "laws", "pet", "feed", "fetch", "walk", "sit", "git push", "git status", "git log",
                  "sudo rm -rf /", "kill -9 1", "asdf"]:
            self.assertTrue(cli.handle(b, c), c)
        self.assertFalse(cli.handle(b, "exit"))


if __name__ == "__main__":
    unittest.main()
