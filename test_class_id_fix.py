"""
Test the class ID lookup fix.
"""

from core.game_engine_sqlite import GameEngineSQLite

def test_class_id_lookup():
    """Test that class name lookup returns correct IDs."""
    engine = GameEngineSQLite("talekeeper.db")
    
    # Test the class lookup directly
    classes = engine.get_available_classes_sync()
    
    print("Available classes:")
    for cls in classes:
        print(f"  {cls.name} (id: {cls.id})")
    
    # Simulate the fixed lookup
    def fixed_get_class_id(name):
        for cls in classes:
            if cls.name == name:
                return name.lower().replace(' ', '_')
        return 'fighter'  # fallback
    
    print("\nTesting class ID lookup:")
    test_names = ['Barbarian', 'Fighter', 'Cleric', 'NonExistent']
    for name in test_names:
        result = fixed_get_class_id(name)
        print(f"  '{name}' -> '{result}'")

if __name__ == "__main__":
    test_class_id_lookup()