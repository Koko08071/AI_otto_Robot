import json
import unittest
from pathlib import Path
from unittest.mock import Mock

from motion_bridge import GestureDispatcher, RobotClient, load_actions
from recognize import StableGesture


class MotionBridgeTests(unittest.TestCase):
    def setUp(self):
        self.actions = load_actions()
        self.client = Mock()
        self.dispatcher = GestureDispatcher(self.actions, self.client, cooldown=3.0)

    def test_action_mapping_is_one_shot(self):
        self.assertEqual(self.actions["finger_gun"]["program"]["name"], "shot_fall_side")
        self.assertEqual(self.actions["fist"]["program"]["name"], "walk_reverse_complete_p450")
        for action in self.actions.values():
            if "composition" in action:
                continue
            program = action["program"]
            self.assertFalse(program.get("repeat", False))
        self.assertEqual(self.actions["fist"]["program"]["segments"][-1]["pose"], [90, 90, 100, 90])
        self.assertEqual(self.actions["fist"]["program"]["segments"][-1]["duration"], 1200)

    def test_fall_is_bounded_and_keeps_servo_output_enabled(self):
        segments = self.actions["finger_gun"]["program"]["segments"]
        self.assertEqual(sum(s["duration"] for s in segments), 780)
        self.assertEqual(segments[-2]["pose"], [145, 45, 20, 20])
        self.assertEqual(segments[-1], {"type": "hold", "duration": 250})
        self.assertTrue(all(s["type"] in ("move", "hold") for s in segments))
        self.assertTrue(all(20 <= angle <= 145 for s in segments if s["type"] == "move" for angle in s["pose"]))
        self.assertEqual([s["pose"][2] for s in segments if s["type"] == "move"], [85, 55, 35, 20])

    def test_gun_and_fist_dispatch_correct_programs(self):
        self.dispatcher.dispatch(("finger_gun",), now=10.0)
        self.client.play.assert_called_once_with(self.actions["finger_gun"]["program"])
        self.dispatcher.dispatch(("fist",), now=14.0)
        self.assertEqual(self.client.play.call_args.args[0], self.actions["fist"]["program"])

    def test_ok_returns_home(self):
        message = self.dispatcher.dispatch(("ok",), now=10.0)
        program = self.actions["ok"]["program"]
        self.client.play.assert_called_once_with(program)
        self.assertEqual(program["segments"], [
            {"type": "move", "duration": 1200, "pose": [90, 90, 100, 90]},
        ])
        self.assertIn("归位", message)

    def test_ok_switches_immediately_and_stop_has_priority(self):
        self.dispatcher.dispatch(("finger_gun",), now=10.0)
        self.dispatcher.dispatch(("ok",), now=11.0)
        self.assertEqual(self.client.play.call_count, 2)
        self.dispatcher.dispatch(("stop", "ok"), now=14.0)
        self.client.stop.assert_called_once()
        self.assertEqual(self.client.play.call_count, 2)

    def test_cooldown_and_ambiguous_results_do_not_move(self):
        self.dispatcher.dispatch(("finger_gun",), now=10.0)
        self.dispatcher.dispatch(("finger_gun",), now=11.0)
        self.dispatcher.dispatch(("finger_gun", "fist"), now=20.0)
        self.assertEqual(self.client.play.call_count, 1)

    def test_stop_stops_even_during_cooldown(self):
        self.dispatcher.dispatch(("finger_gun",), now=10.0)
        self.dispatcher.dispatch(("stop",), now=11.0)
        self.client.stop.assert_called_once()

    def test_held_gesture_repeats_after_five_seconds_with_fresh_confirmation(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        stabilizer = StableGesture(3)
        samples = [(0, ("fist",)), (1, ("fist",)), (2, ("fist",)),
                   (6.9, ("fist",)), (7, ("fist",)), (22, ()),
                   (23, ("fist",)), (24, ("fist",)), (25, ("fist",))]
        counts = []
        for now, gestures in samples:
            stabilizer.update(gestures)
            if stabilizer.count >= stabilizer.frames:
                dispatcher.dispatch(gestures, now=now)
            counts.append(self.client.play.call_count)
        self.assertEqual(counts, [0, 0, 1, 1, 2, 2, 2, 2, 3])

    def test_stop_bypasses_interval_without_repeated_requests(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        dispatcher.dispatch(("fist",), now=0)
        dispatcher.dispatch(("stop",), now=1)
        dispatcher.dispatch(("stop",), now=2)
        self.client.stop.assert_called_once()
        dispatcher.dispatch((), now=3)
        dispatcher.dispatch(("stop",), now=4)
        self.assertEqual(self.client.stop.call_count, 2)

    def test_failed_action_is_not_retried_every_frame(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        self.client.play.side_effect = RuntimeError("busy")
        with self.assertRaisesRegex(RuntimeError, "busy"):
            dispatcher.dispatch(("fist",), now=0)
        dispatcher.dispatch(("fist",), now=1)
        self.client.play.assert_called_once()

    def test_switch_back_and_release_do_not_wait(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        for now, gesture in enumerate(("fist", "ok", "fist")):
            dispatcher.dispatch((gesture,), now=now)
        self.assertEqual(self.client.play.call_count, 3)
        dispatcher.dispatch((), now=3)
        dispatcher.dispatch(("fist",), now=4)
        self.assertEqual(self.client.play.call_count, 4)

    def test_busy_switch_retries_without_waiting_for_repeat_interval(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        dispatcher.dispatch(("fist",), now=0)
        self.client.play.side_effect = [RuntimeError("busy"), None]
        with self.assertRaisesRegex(RuntimeError, "busy"):
            dispatcher.dispatch(("ok",), now=1)
        dispatcher.dispatch(("ok",), now=2)
        self.assertEqual(self.client.play.call_count, 2)
        dispatcher.dispatch(("ok",), now=3)
        self.assertEqual(self.client.play.call_count, 3)

    def test_old_gestures_no_longer_control_robot(self):
        for gesture in ("palm", "stop_inverted"):
            self.assertIsNone(self.dispatcher.dispatch((gesture,), now=10))
        self.client.play.assert_not_called()
        self.client.stop.assert_not_called()

    def test_peace_variants_run_forward_once(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        dispatcher.dispatch(("peace",), now=0)
        dispatcher.dispatch(("peace_inverted",), now=1)
        self.assertEqual(self.client.play.call_count, 1)
        self.assertEqual(self.client.play.call_args.args[0]["name"], "walk_complete_p500")
        self.assertIn("前进", dispatcher.dispatch(("peace",), now=6))

    def test_pinkie_and_little_finger_run_the_selected_composition(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        dispatcher.dispatch(("little_finger",), now=0)
        composition = self.actions["little_finger"]["composition"]
        self.assertEqual(composition["id"], "a02b547d-0df4-4a68-afdc-a92351ef40fa")
        self.assertEqual(composition["name"], "你是笨蛋")
        self.client.play_composition.assert_called_once_with(composition)
        dispatcher.dispatch(("pinkie", "little_finger"), now=1)
        self.assertEqual(self.client.play_composition.call_count, 1)
        dispatcher.dispatch(("pinkie",), now=5)
        self.assertEqual(self.client.play_composition.call_count, 2)
        self.client.play.assert_not_called()

    def test_middle_finger_runs_the_little_finger_composition(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        dispatcher.dispatch(("middle_finger",), now=0)
        self.client.play_composition.assert_called_once_with(
            self.actions["little_finger"]["composition"]
        )
        dispatcher.dispatch(("mid.finger",), now=5)
        dispatcher.dispatch(("mid_finger",), now=10)
        self.assertEqual(self.client.play_composition.call_count, 3)

    def test_pinkie_respects_stop_and_ambiguous_gestures(self):
        self.dispatcher.dispatch(("little_finger", "fist"), now=0)
        self.client.play_composition.assert_not_called()
        self.dispatcher.dispatch(("pinkie", "stop"), now=1)
        self.client.stop.assert_called_once()
        self.client.play_composition.assert_not_called()

    def test_heart_variants_share_one_action_and_interval(self):
        dispatcher = GestureDispatcher(self.actions, self.client)
        dispatcher.dispatch(("hand_heart", "hand_heart2"), now=0)
        dispatcher.dispatch(("hand_heart2",), now=1)
        self.client.play_composition.assert_called_once_with(self.actions["heart"]["composition"])
        dispatcher.dispatch(("hand_heart",), now=5)
        self.assertEqual(self.client.play_composition.call_count, 2)
        self.client.play.assert_not_called()

    def test_composition_uses_saved_id_and_stop_cancels_scheduler(self):
        robot = RobotClient("http://127.0.0.1")
        robot.verify = Mock()
        robot.request = Mock()
        robot.studio = Mock()
        robot.studio.verify.return_value = {"connected": True, "active": "idle"}
        composition = self.actions["heart"]["composition"]
        robot.studio.request.side_effect = [{"running": False}, composition, {}]
        robot.play_composition(composition)
        robot.studio.request.assert_called_with("/api/compositions/run", {"id": composition["id"]})
        robot.studio.request.side_effect = None
        robot.studio.request.return_value = {"running": True}
        with self.assertRaisesRegex(RuntimeError, "busy"):
            robot.play(self.actions["fist"]["program"])
        robot.request.assert_not_called()
        robot.stop()
        robot.studio.request.assert_called_with("/api/compositions/stop", {})
        robot.request.assert_called_once_with("/api/stop", {})

    def test_wrong_composition_name_never_runs(self):
        robot = RobotClient("http://127.0.0.1")
        robot.verify = Mock()
        robot.studio = Mock()
        robot.studio.verify.return_value = {"connected": True, "active": "idle"}
        robot.studio.request.side_effect = [{"running": False}, {"name": "wrong"}]
        with self.assertRaisesRegex(RuntimeError, "does not match"):
            robot.play_composition(self.actions["heart"]["composition"])
        self.assertTrue(all(len(call.args) == 1 for call in robot.studio.request.call_args_list))

    def test_wrong_device_never_receives_motion(self):
        robot = RobotClient("http://127.0.0.1")
        robot.request = Mock(return_value={"device_id": "wrong", "servo_available": True})
        with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
            robot.play(self.actions["fist"]["program"])
        robot.request.assert_called_once_with("/api/status")

    def test_device_busy_skips_action(self):
        robot = RobotClient("http://127.0.0.1")
        robot.request = Mock(return_value={
            "device_id": "14:c1:9f:30:0e:70", "servo_available": True,
            "servo_enabled": True, "moving": True, "active": "other",
        })
        with self.assertRaisesRegex(RuntimeError, "busy"):
            robot.play(self.actions["fist"]["program"])
        robot.request.assert_called_once_with("/api/status")


if __name__ == "__main__":
    unittest.main()
