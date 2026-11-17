#!/usr/bin/env python3
"""page_gate camera_warnings (DESIGN.md One-Camera Rule): fail-on-bad and pass-on-good, no browser needed.

    python3 scripts/tests/test_page_gate_camera.py
"""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import page_gate as pg

class Camera(unittest.TestCase):
    def test_bad(self):
        self.assertTrue(pg.camera_warnings(".t{transform: perspective(1500px) rotateX(55deg)}"))   # wrong tilt
        self.assertTrue(pg.camera_warnings(".t{transform: perspective(1500px) rotateX(38deg) rotateY(20deg)}"))  # yaw
        self.assertTrue(pg.camera_warnings(".t{transform: perspective(1500px) rotateX(38deg)}"))   # no reduced-motion flat
    def test_good(self):
        ok = ".t{transform: perspective(1500px) rotateX(38deg)} @media (prefers-reduced-motion: reduce){.t{transform:none}}"
        self.assertEqual(pg.camera_warnings(ok), [])
        self.assertEqual(pg.camera_warnings(".f{transform: perspective(70vh) rotateX(64deg)}"), [])  # floor plane, a ground
        self.assertEqual(pg.camera_warnings(".t{transform: rotateX(0deg)}"), [])

if __name__ == "__main__":
    unittest.main()
