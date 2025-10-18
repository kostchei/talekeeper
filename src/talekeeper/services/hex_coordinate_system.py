import math
from typing import List, Tuple

class HexCoordinateSystem:

    DIRECTIONS = [
        (1, 0),   # E
        (1, -1),  # NE
        (0, -1),  # NW
        (-1, 0),  # W
        (-1, 1),  # SW
        (0, 1)    # SE
    ]

    DIRECTION_NAMES = ['East', 'Northeast', 'Northwest', 'West', 'Southwest', 'Southeast']

    @staticmethod
    def get_neighbor(q: int, r: int, direction: int) -> Tuple[int, int]:
        dq, dr = HexCoordinateSystem.DIRECTIONS[direction % 6]
        return (q + dq, r + dr)

    @staticmethod
    def get_all_neighbors(q: int, r: int) -> List[Tuple[int, int]]:
        return [
            HexCoordinateSystem.get_neighbor(q, r, i)
            for i in range(6)
        ]

    @staticmethod
    def get_distance(q1: int, r1: int, q2: int, r2: int) -> int:
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

    @staticmethod
    def get_direction_index(from_q: int, from_r: int, to_q: int, to_r: int) -> int:
        dq = to_q - from_q
        dr = to_r - from_r

        for i, (dir_q, dir_r) in enumerate(HexCoordinateSystem.DIRECTIONS):
            if dir_q == dq and dir_r == dr:
                return i

        return 0

    @staticmethod
    def get_direction_name(direction: int) -> str:
        return HexCoordinateSystem.DIRECTION_NAMES[direction % 6]

    @staticmethod
    def get_hexes_in_radius(center_q: int, center_r: int, radius: int) -> List[Tuple[int, int]]:
        results = []
        for q in range(center_q - radius, center_q + radius + 1):
            r1 = max(center_r - radius, center_r - q - radius)
            r2 = min(center_r + radius, center_r - q + radius)
            for r in range(r1, r2 + 1):
                results.append((q, r))
        return results

    @staticmethod
    def hex_to_pixel(q: int, r: int, hex_size: float) -> Tuple[float, float]:
        # Pointy-top axial layout: convert cube coordinates to pixel space
        x = hex_size * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
        y = hex_size * (3 / 2 * r)
        return (x, y)

    @staticmethod
    def pixel_to_hex(x: float, y: float, hex_size: float) -> Tuple[int, int]:
        # Inverse transform for pointy-top axial layout
        q = (math.sqrt(3) / 3 * x - 1 / 3 * y) / hex_size
        r = (2 / 3 * y) / hex_size

        return HexCoordinateSystem.hex_round(q, r)

    @staticmethod
    def hex_round(q: float, r: float) -> Tuple[int, int]:
        s = -q - r

        qi = round(q)
        ri = round(r)
        si = round(s)

        q_diff = abs(qi - q)
        r_diff = abs(ri - r)
        s_diff = abs(si - s)

        if q_diff > r_diff and q_diff > s_diff:
            qi = -ri - si
        elif r_diff > s_diff:
            ri = -qi - si

        return (qi, ri)
