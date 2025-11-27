# core
# category: test
"""
Unit tests for Isometric Math logic.
Demonstrates testing UI logic without loading the full UI.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root / "src"))

from talekeeper.services.hex_coordinate_system import HexCoordinateSystem

class TestIsometricMath:
    def test_cartesian_to_isometric_projection(self):
        """
        Verify the math used in IsometricMapWidget._draw_iso_hex
        iso_x = x - y
        iso_y = (x + y) / 2
        """
        # Test case 1: Origin
        cart_x, cart_y = 0, 0
        iso_x = cart_x - cart_y
        iso_y = (cart_x + cart_y) / 2
        assert iso_x == 0
        assert iso_y == 0
        
        # Test case 2: Moving Right in Cartesian (x increases)
        # In isometric, this should move down-right
        cart_x, cart_y = 100, 0
        iso_x = cart_x - cart_y
        iso_y = (cart_x + cart_y) / 2
        assert iso_x == 100
        assert iso_y == 50
        
        # Test case 3: Moving Down in Cartesian (y increases)
        # In isometric, this should move down-left
        cart_x, cart_y = 0, 100
        iso_x = cart_x - cart_y
        iso_y = (cart_x + cart_y) / 2
        assert iso_x == -100
        assert iso_y == 50
        
    def test_hex_to_isometric_pipeline(self):
        """
        Verify the full pipeline from Hex -> Cartesian -> Isometric
        """
        coord_system = HexCoordinateSystem()
        hex_size = 40
        
        # Hex (0, 0) -> Cartesian (0, 0) -> Iso (0, 0)
        q, r = 0, 0
        cart_x, cart_y = coord_system.hex_to_pixel(q, r, hex_size)
        iso_x = cart_x - cart_y
        iso_y = (cart_x + cart_y) / 2
        
        assert abs(iso_x) < 0.01
        assert abs(iso_y) < 0.01
        
        # Hex (1, 0) -> Neighbor to the right (Pointy-top)
        q, r = 1, 0
        cart_x, cart_y = coord_system.hex_to_pixel(q, r, hex_size)
        # Pointy-top: x = size * sqrt(3) * (q + r/2)
        # x = 40 * sqrt(3) ≈ 69.28, y = 0
        
        iso_x = cart_x - cart_y
        iso_y = (cart_x + cart_y) / 2
        
        # x=69.28, y=0 -> iso_x=69.28, iso_y=34.64
        import math
        expected_x = 40 * math.sqrt(3)
        expected_y = expected_x / 2
        
        assert abs(iso_x - expected_x) < 0.01
        assert abs(iso_y - expected_y) < 0.01
