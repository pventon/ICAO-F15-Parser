import unittest

from Utilities.Utils import Utils


class UtilsTest(unittest.TestCase):

    # Method Utils().is_degree_semantics()
    def test_is_degree_semantics_01(self):
        self.assertEqual(True, Utils().is_degree_semantics("0", 90))
        self.assertEqual(True, Utils().is_degree_semantics("89", 90))
        self.assertEqual(True, Utils().is_degree_semantics("90", 90))
        self.assertEqual(False, Utils().is_degree_semantics("91", 90))

    # Method Utils().is_degree_minute_semantics()
    # 2 Digit Latitude value
    def test_is_degree_minute_semantics_01(self):
        self.assertEqual(True, Utils().is_degree_minute_semantics("0000", 90, 2))
        self.assertEqual(True, Utils().is_degree_minute_semantics("8900", 90, 2))
        self.assertEqual(True, Utils().is_degree_minute_semantics("9000", 90, 2))
        self.assertEqual(False, Utils().is_degree_minute_semantics("9100", 90, 2))
        self.assertEqual(True, Utils().is_degree_minute_semantics("8959", 90, 2))
        self.assertEqual(False, Utils().is_degree_minute_semantics("9001", 90, 2))

    # 3 Digit Latitude value
    def test_is_degree_minute_semantics_02(self):
        self.assertEqual(True, Utils().is_degree_minute_semantics("00000", 180, 3))
        self.assertEqual(True, Utils().is_degree_minute_semantics("17900", 180, 3))
        self.assertEqual(True, Utils().is_degree_minute_semantics("18000", 180, 3))
        self.assertEqual(False, Utils().is_degree_minute_semantics("18100", 180, 3))
        self.assertEqual(True, Utils().is_degree_minute_semantics("17959", 180, 3))
        self.assertEqual(False, Utils().is_degree_minute_semantics("18001", 180, 3))

    # Method Utils().speed_of_sound_at_altitude()
    def test_speed_of_sound_at_altitude_01(self):
        self.assertAlmostEqual(Utils().speed_of_sound_at_altitude(0.0), 340.121, places=3)
        self.assertAlmostEqual(Utils().speed_of_sound_at_altitude(9000.0), 303.9362, places=4)
        self.assertAlmostEqual(Utils().speed_of_sound_at_altitude(10000.0), 299.646, places=3)
        self.assertAlmostEqual(Utils().speed_of_sound_at_altitude(11000.0), 295.2936, places=4)
        self.assertAlmostEqual(Utils().speed_of_sound_at_altitude(12000.0), 295.2936, places=4)

    # Method Utils().mach_to_ms_speed()
    def test_mach_to_ms_speed_01(self):
        self.assertAlmostEqual(Utils().mach_to_ms_speed(0.5, 0), 1.715, places=3)
        self.assertAlmostEqual(Utils().mach_to_ms_speed(0.82, 0), 2.813, places=3)
        self.assertAlmostEqual(Utils().mach_to_ms_speed(0.5, 10000), 1.498, places=3)
        self.assertAlmostEqual(Utils().mach_to_ms_speed(0.82, 10000), 2.457, places=3)
        self.assertAlmostEqual(Utils().mach_to_ms_speed(1.0, 10000), 2.996, places=3)

    # Method Utils().get_bearing_distance_projected_point()
    # 111319.492 is the distance in meters at the equator for 1 degree arc.
    # Earth circumference in meters 40,075,017, 90 degrees = 40,075,017 / 4 = 10,018,754.25
    def test_get_bearing_distance_projected_point_01(self):
        result = Utils().get_bearing_distance_projected_point(0.0, 0.0, 90.0, 111319.492)
        self.assertAlmostEqual(result[0], 0.0, places=3)
        self.assertAlmostEqual(result[1], 1.0, places=3)

        result = Utils().get_bearing_distance_projected_point(0.0, 0.0, -90.0, 111319.492)
        self.assertAlmostEqual(result[0], 0.0, places=3)
        self.assertAlmostEqual(result[1], -1.0, places=3)

        result = Utils().get_bearing_distance_projected_point(0.0, 0.0, 180.0, 111319.492)
        self.assertAlmostEqual(result[0], -1.007, places=3)
        self.assertAlmostEqual(result[1], 0.0, places=3)

        result = Utils().get_bearing_distance_projected_point(0.0, 0.0, -180.0, 111319.492)
        self.assertAlmostEqual(result[0], -1.007, places=3)
        self.assertAlmostEqual(result[1], 0.0, places=3)

        result = Utils().get_bearing_distance_projected_point(1.0, 1.0, 90.0, 111319.492)
        self.assertAlmostEqual(result[0], 1.0, places=3)
        self.assertAlmostEqual(result[1], 2.0, places=3)

        result = Utils().get_bearing_distance_projected_point(1.0, 1.0, 180.0, 111319.492)
        self.assertAlmostEqual(result[0], -0.007, places=3)
        self.assertAlmostEqual(result[1], 1.0, places=3)

        result = Utils().get_bearing_distance_projected_point(0.0, 0.0, 90.0, 10018754.25)
        self.assertAlmostEqual(result[0], -0.0, places=3)
        self.assertAlmostEqual(result[1], 90.0, places=3)

        result = Utils().get_bearing_distance_projected_point(0.0, 0.0, 90.0, 20037508.5)
        self.assertAlmostEqual(result[0], -0.0, places=3)
        self.assertAlmostEqual(result[1], -180.0, places=3)

    # Method Utils().get_bearing_distance_between_points()
    # 111319.492 is the distance in meters at the equator for 1 degree arc.
    # Earth circumference in meters 40,075,017, 90 degrees = 40,075,017 / 4 = 10,018,754.25
    def test_get_bearing_distance_between_points_01(self):
        result = Utils().get_bearing_distance_between_points(0.0, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(result[0], 90.0, places=3)
        self.assertAlmostEqual(result[1], 111319.491, places=3)

        result = Utils().get_bearing_distance_between_points(0.0, 0.0, 1.0, 0.0)
        self.assertAlmostEqual(result[0], 0.0, places=3)
        self.assertAlmostEqual(result[1], 110574.389, places=3)

        result = Utils().get_bearing_distance_between_points(0.0, 0.0, 0.0, -1.0)
        self.assertAlmostEqual(result[0], -90.0, places=3)
        self.assertAlmostEqual(result[1], 111319.491, places=3)

        result = Utils().get_bearing_distance_between_points(0.0, 0.0, -1.0, 0.0)
        self.assertAlmostEqual(result[0], 180.0, places=3)
        self.assertAlmostEqual(result[1], 110574.389, places=3)


if __name__ == '__main__':
    unittest.main()
