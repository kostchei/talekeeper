import pytest
import sqlite3
import os
import sys
sys.path.insert(0, 'src')
from talekeeper.services.beast_loot_service import BeastLootService

TEST_DB = "test_beast_loot.db"

@pytest.fixture
def setup_db():
    """Setup test database"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE monsters (
            id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            challenge_rating TEXT,
            drops_rations BOOLEAN DEFAULT 0
        )
    """)

    cursor.execute("""
        INSERT INTO monsters (id, name, type, challenge_rating, drops_rations) VALUES
        ('wolf', 'Wolf', 'beast', '1/4', 1),
        ('bear', 'Brown Bear', 'beast', '1', 1),
        ('tiger', 'Tiger', 'beast', '4', 1),
        ('goblin', 'Goblin', 'humanoid', '1/4', 0),
        ('ogre', 'Ogre', 'giant', '2', 0)
    """)

    cursor.execute("""
        CREATE TABLE character_inventory (
            character_id TEXT,
            item_name TEXT,
            quantity INTEGER
        )
    """)

    conn.commit()
    conn.close()

    yield TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_is_beast(setup_db):
    """Test beast detection"""
    service = BeastLootService(TEST_DB)

    assert service.is_beast('wolf') == True
    assert service.is_beast('bear') == True
    assert service.is_beast('goblin') == False
    assert service.is_beast('ogre') == False


def test_parse_cr(setup_db):
    """Test CR parsing"""
    service = BeastLootService(TEST_DB)

    assert service._parse_cr('1/8') == 0.125
    assert service._parse_cr('1/4') == 0.25
    assert service._parse_cr('1/2') == 0.5
    assert service._parse_cr('1') == 1.0
    assert service._parse_cr('4') == 4.0
    assert service._parse_cr('10') == 10.0


def test_cr_to_treasure(setup_db):
    """Test CR to individual treasure conversion"""
    service = BeastLootService(TEST_DB)

    assert service._cr_to_individual_treasure(0.125) == 0.5
    assert service._cr_to_individual_treasure(0.25) == 1.0
    assert service._cr_to_individual_treasure(1.0) == 2.0
    assert service._cr_to_individual_treasure(4.0) == 10.0
    assert service._cr_to_individual_treasure(10.0) == 50.0


def test_calculate_ration_drop(setup_db):
    """Test ration quantity calculation"""
    service = BeastLootService(TEST_DB)

    wolf_rations = service.calculate_ration_drop('wolf')
    assert wolf_rations == 2

    bear_rations = service.calculate_ration_drop('bear')
    assert bear_rations == 4

    tiger_rations = service.calculate_ration_drop('tiger')
    assert tiger_rations == 20


def test_generate_beast_loot(setup_db):
    """Test loot generation for beasts"""
    service = BeastLootService(TEST_DB)

    loot = service.generate_beast_loot('wolf')
    assert len(loot) == 1
    assert loot[0]['name'] == 'Beast Rations'
    assert loot[0]['quantity'] == 2
    assert loot[0]['unit_value_gp'] == 0.5
    assert loot[0]['value_gp'] == 1.0

    loot = service.generate_beast_loot('tiger')
    assert len(loot) == 1
    assert loot[0]['quantity'] == 20
    assert loot[0]['value_gp'] == 10.0

    loot = service.generate_beast_loot('goblin')
    assert len(loot) == 0


def test_add_rations_to_inventory(setup_db):
    """Test adding rations to character inventory"""
    service = BeastLootService(TEST_DB)

    success = service.add_rations_to_inventory('char_1', 5)
    assert success == True

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM character_inventory WHERE character_id = 'char_1' AND item_name = 'Beast Rations'")
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[0] == 5

    success = service.add_rations_to_inventory('char_1', 3)
    assert success == True

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM character_inventory WHERE character_id = 'char_1' AND item_name = 'Beast Rations'")
    result = cursor.fetchone()
    conn.close()

    assert result[0] == 8


def test_get_monster_name(setup_db):
    """Test getting monster name"""
    service = BeastLootService(TEST_DB)

    name = service.get_monster_name('wolf')
    assert name == 'Wolf'

    name = service.get_monster_name('bear')
    assert name == 'Brown Bear'

    name = service.get_monster_name('nonexistent')
    assert name == 'Unknown Beast'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
