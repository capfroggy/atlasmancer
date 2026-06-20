import json
import unittest

from atlasmancer import generate_world
from atlasmancer.renderers.campaign import RESERVED_FOR, SCHEMA_VERSION, build_campaign


class CampaignExportTests(unittest.TestCase):
    def test_schema_has_required_top_level_keys(self):
        world = generate_world(seed="campaign", width=36, height=16, landmark_count=3)
        payload = build_campaign(world)

        for key in ("meta", "title", "map", "landmarks", "regions", "countries", "factions", "quests", "dungeons", "reserved_for"):
            self.assertIn(key, payload)

        self.assertEqual(payload["meta"]["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["meta"]["generator"], "atlasmancer")
        self.assertEqual(payload["meta"]["seed"], "campaign")

    def test_reserved_arrays_are_empty_in_v0_2(self):
        world = generate_world(seed="campaign", width=36, height=16, landmark_count=3)
        payload = build_campaign(world)

        for key in ("regions", "countries", "factions", "quests", "dungeons"):
            self.assertEqual(payload[key], [])
        self.assertEqual(payload["reserved_for"], RESERVED_FOR)

    def test_gm_block_present_for_gm_audience(self):
        world = generate_world(seed="campaign", width=36, height=16, landmark_count=3)
        payload = build_campaign(world, audience="gm")

        for landmark in payload["landmarks"]:
            self.assertIn("gm", landmark)
            self.assertIn("secret", landmark["gm"])
            self.assertIn("danger", landmark["gm"])
            self.assertIn("reward", landmark["gm"])
            self.assertIn("public", landmark)
            self.assertIn("hook", landmark["public"])

    def test_gm_block_absent_for_player_audience(self):
        world = generate_world(seed="campaign", width=36, height=16, landmark_count=3)
        payload = build_campaign(world, audience="player")

        for landmark in payload["landmarks"]:
            self.assertNotIn("gm", landmark)
            self.assertIn("public", landmark)

    def test_landmark_ids_are_stable_and_unique(self):
        world = generate_world(seed="campaign", width=36, height=16, landmark_count=5)
        payload = build_campaign(world)

        ids = [landmark["id"] for landmark in payload["landmarks"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))

    def test_same_seed_locale_and_audience_produce_same_campaign_except_created_at(self):
        first = build_campaign(generate_world(seed="campaign", width=36, height=16, landmark_count=3))
        second = build_campaign(generate_world(seed="campaign", width=36, height=16, landmark_count=3))

        first["meta"].pop("created_at")
        second["meta"].pop("created_at")
        self.assertEqual(first, second)

    def test_world_id_is_deterministic_for_same_seed(self):
        first = generate_world(seed="campaign")
        second = generate_world(seed="campaign")
        third = generate_world(seed="a-different-seed")

        self.assertEqual(first.world_id, second.world_id)
        self.assertNotEqual(first.world_id, third.world_id)

    def test_cli_writes_campaign_json(self):
        from contextlib import redirect_stdout
        from io import StringIO

        from atlasmancer.cli import main

        output = StringIO()
        with redirect_stdout(output):
            main(["--seed", "campaign-cli", "--format", "campaign", "--audience", "player"])

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["meta"]["audience"], "player")
        self.assertTrue(all("gm" not in lm for lm in payload["landmarks"]))


if __name__ == "__main__":
    unittest.main()
