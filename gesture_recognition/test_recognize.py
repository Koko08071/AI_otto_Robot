import unittest
from unittest.mock import Mock

from recognize import StableGesture, confirmation_frames, detect_finger_gun, detections


class StableGestureTests(unittest.TestCase):
    def test_fast_confirmation_keeps_ambiguous_gestures_conservative(self):
        self.assertEqual(confirmation_frames(("ok",), 3), 2)
        self.assertEqual(confirmation_frames(("stop",), 3), 2)
        self.assertEqual(confirmation_frames(("fist",), 3), 3)
        self.assertEqual(confirmation_frames(("finger_gun",), 3), 3)
        self.assertEqual(confirmation_frames(("ok", "fist"), 3), 3)
        tracker = StableGesture(3)
        self.assertFalse(tracker.update(("ok",), 2))
        self.assertTrue(tracker.update(("ok",), 2))

    def test_requires_consecutive_frames_and_emits_transitions(self):
        tracker = StableGesture(3)
        self.assertFalse(tracker.update(("fist",)))
        self.assertFalse(tracker.update(("palm",)))
        self.assertFalse(tracker.update(("fist",)))
        self.assertFalse(tracker.update(("fist",)))
        self.assertTrue(tracker.update(("fist",)))
        self.assertFalse(tracker.update(("fist",)))
        self.assertFalse(tracker.update(()))
        self.assertFalse(tracker.update(()))
        self.assertTrue(tracker.update(()))

    def test_multiple_hands_deduplicate_and_ignore_no_gesture(self):
        result = Mock()
        result.boxes.cls.tolist.return_value = [1, 0, 1, 2]
        result.boxes.conf.tolist.return_value = [0.9, 0.8, 0.95, 0.7]
        labels, scores = detections(result, {0: "no_gesture", 1: "fist", 2: "three_gun"})
        self.assertEqual(labels, ("fist", "three_gun"))
        self.assertEqual(scores["fist"], 0.95)

    def test_one_hand_keeps_only_highest_confidence_overlapping_action(self):
        result = Mock()
        result.boxes.cls.tolist.return_value = [0, 1, 2]
        result.boxes.conf.tolist.return_value = [0.70, 0.92, 0.80]
        result.boxes.xyxy.tolist.return_value = [
            [10, 10, 110, 110],
            [12, 12, 108, 108],
            [250, 10, 350, 110],
        ]
        labels, scores = detections(result, {0: "point", 1: "fist", 2: "like"})
        self.assertEqual(labels, ("fist", "like"))
        self.assertEqual(scores["fist"], 0.92)

    def test_dataset_three_gun_is_not_used_as_camera_facing_trigger(self):
        result = Mock()
        result.boxes.cls.tolist.return_value = [0]
        result.boxes.conf.tolist.return_value = [0.91]
        result.boxes.xyxy.tolist.return_value = [[10, 10, 100, 100]]
        detected, score = detect_finger_gun(result, {0: "three_gun"})
        self.assertFalse(detected)
        self.assertEqual(score, 0.0)

    def test_like_alone_does_not_trigger(self):
        result = Mock()
        result.boxes.cls.tolist.return_value = [0]
        result.boxes.conf.tolist.return_value = [0.8]
        result.boxes.xyxy.tolist.return_value = [[0, 0, 100, 100]]
        detected, _ = detect_finger_gun(result, {0: "like"})
        self.assertFalse(detected)

        result.boxes.cls.tolist.return_value = [0, 1]
        result.boxes.conf.tolist.return_value = [0.9, 0.8]
        result.boxes.xyxy.tolist.return_value = [[0, 0, 100, 100], [10, 10, 90, 90]]
        detected, score = detect_finger_gun(result, {0: "point", 1: "like"})
        self.assertTrue(detected)
        self.assertEqual(score, 0.9)

    def test_point_alone_is_the_application_trigger(self):
        result = Mock()
        result.boxes.cls.tolist.return_value = [0]
        result.boxes.conf.tolist.return_value = [0.88]
        result.boxes.xyxy.tolist.return_value = [[10, 10, 100, 100]]
        detected, score = detect_finger_gun(result, {0: "point"})
        self.assertTrue(detected)
        self.assertEqual(score, 0.88)

    def test_point_is_a_gun_even_when_the_box_is_vertical(self):
        result = Mock()
        result.boxes.cls.tolist.return_value = [0]
        result.boxes.conf.tolist.return_value = [0.88]
        result.boxes.xyxy.tolist.return_value = [[10, 10, 90, 180]]
        detected, _ = detect_finger_gun(result, {0: "point"})
        self.assertTrue(detected)

    def test_low_confidence_point_does_not_trigger_gun(self):
        result = Mock()
        result.boxes.cls.tolist.return_value = [0]
        result.boxes.conf.tolist.return_value = [0.60]
        result.boxes.xyxy.tolist.return_value = [[10, 10, 100, 100]]
        detected, _ = detect_finger_gun(result, {0: "point"})
        self.assertFalse(detected)

    def test_highest_confidence_action_controls_trigger(self):
        result = Mock()
        result.boxes.cls.tolist.return_value = [0, 1]
        result.boxes.conf.tolist.return_value = [0.70, 0.88]
        result.boxes.xyxy.tolist.return_value = [[10, 10, 100, 100], [12, 12, 98, 98]]
        detected, _ = detect_finger_gun(result, {0: "point", 1: "fist"})
        self.assertFalse(detected)


if __name__ == "__main__":
    unittest.main()
