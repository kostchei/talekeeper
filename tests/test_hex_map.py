# test
import sqlite3
from src.talekeeper.services.hex_map_service import HexMapService
from src.talekeeper.services.hex_coordinate_system import HexCoordinateSystem
from src.talekeeper.services.hex_event_logger import HexEventLogger

def test_hex_system():
    print("Testing Hex Map System...")

    db_path = 'talekeeper.db'

    print("\n1. Testing coordinate system...")
    coords = HexCoordinateSystem()

    neighbors = coords.get_all_neighbors(0, 0)
    print(f"   Neighbors of (0,0): {neighbors}")

    distance = coords.get_distance(0, 0, 3, 2)
    print(f"   Distance from (0,0) to (3,2): {distance} hexes")

    print("\n2. Testing hex map service...")
    hex_service = HexMapService(db_path)

    test_character_id = 'test_char_hex_001'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO characters
            (id, name, level, race_id, class_id, background_id,
             strength, dexterity, constitution, intelligence, wisdom, charisma,
             hit_points_max, hit_points_current, armor_class, experience_points)
            VALUES (?, 'Test Character', 5, 'human', 'fighter', 'folk_hero',
                    15, 14, 13, 12, 10, 8,
                    38, 38, 16, 6500)
        ''', (test_character_id,))
        conn.commit()
    finally:
        conn.close()

    print(f"   Initializing position for character {test_character_id}...")
    hex_service.initialize_character_position(test_character_id)

    current_pos = hex_service.get_character_position(test_character_id)
    print(f"   Current position: {current_pos}")

    hex_data = hex_service.get_hex(test_character_id, 0, 0)
    print(f"   Starting hex: {hex_data['terrain_type']} ({hex_data['biome']})")

    visible = hex_service.get_visible_hexes(test_character_id, 0, 0, radius=2)
    revealed_count = sum(1 for h in visible if h.get('revealed'))
    print(f"   Visible hexes: {len(visible)}, Revealed: {revealed_count}")

    print("\n3. Testing hex travel...")
    try:
        new_hex = hex_service.travel_to_hex(test_character_id, 1, 0)
        print(f"   Traveled to (1,0): {new_hex['terrain_type']}")

        new_pos = hex_service.get_character_position(test_character_id)
        print(f"   New position: {new_pos}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n4. Testing event logger...")
    event_logger = HexEventLogger(db_path)

    travel_event_id = event_logger.log_travel_event(
        test_character_id, 1, 0, new_hex
    )
    print(f"   Logged travel event: {travel_event_id}")

    combat_result = {
        'won': True,
        'rounds': 5,
        'character_level': 5,
        'damage_dealt': 42,
        'damage_taken': 18,
        'enemies': [
            {'name': 'Goblin', 'cr': 1, 'quantity': 3, 'killed': 3, 'fled': 0}
        ],
        'loot': [
            {'name': 'Gold Coins', 'type': 'currency', 'quantity': 50, 'value': 50},
            {'name': 'Short Sword', 'type': 'weapon', 'quantity': 1, 'value': 10}
        ]
    }

    combat_event_id = event_logger.log_combat_event(
        test_character_id, 1, 0, combat_result
    )
    print(f"   Logged combat event: {combat_event_id}")

    events = event_logger.get_hex_events(test_character_id, 1, 0)
    print(f"   Retrieved {len(events)} events for hex (1,0)")
    for event in events:
        print(f"     - {event['event_type']}: {event['outcome']}")

    print("\n5. Testing exploration stats...")
    stats = hex_service.get_exploration_stats(test_character_id)
    print(f"   Stats: {stats}")

    print("\n6. Cleaning up test data...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM character_hex_map WHERE character_id = ?', (test_character_id,))
        cursor.execute('DELETE FROM character_hex_position WHERE character_id = ?', (test_character_id,))
        cursor.execute('DELETE FROM hex_events WHERE character_id = ?', (test_character_id,))
        cursor.execute('DELETE FROM characters WHERE id = ?', (test_character_id,))
        conn.commit()
    finally:
        conn.close()

    print("\nAll tests passed!")

if __name__ == '__main__':
    test_hex_system()
