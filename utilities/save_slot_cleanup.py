# core
#utility
# core
"""
Save Slot Cleanup Utility

This utility helps clean up and reorganize the save slot system by:
1. Removing orphaned save slots 
2. Consolidating characters to lower-numbered slots
3. Cleaning up empty/unused slots
4. Providing save slot statistics
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class SaveSlotCleanup:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
    
    def get_slot_statistics(self):
        """Get statistics about current save slots."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all save slots
            cursor.execute("SELECT * FROM save_slots ORDER BY slot_number")
            all_slots = cursor.fetchall()
            
            # Get occupied slots
            cursor.execute("SELECT * FROM save_slots WHERE is_occupied = 1 ORDER BY slot_number")
            occupied_slots = cursor.fetchall()
            
            # Get orphaned save slots (marked as occupied but no character)
            cursor.execute("""
                SELECT s.* FROM save_slots s 
                LEFT JOIN characters c ON s.id = c.save_slot_id 
                WHERE s.is_occupied = 1 AND c.id IS NULL
            """)
            orphaned_slots = cursor.fetchall()
            
            # Get highest slot number in use
            cursor.execute("SELECT MAX(slot_number) as max_slot FROM save_slots WHERE is_occupied = 1")
            max_slot_result = cursor.fetchone()
            max_slot = max_slot_result['max_slot'] if max_slot_result['max_slot'] else 0
            
            conn.close()
            
            return {
                'total_slots': len(all_slots),
                'occupied_slots': len(occupied_slots),
                'empty_slots': len(all_slots) - len(occupied_slots),
                'orphaned_slots': len(orphaned_slots),
                'highest_slot_used': max_slot,
                'occupied_slot_numbers': [slot['slot_number'] for slot in occupied_slots],
                'orphaned_slot_numbers': [slot['slot_number'] for slot in orphaned_slots]
            }
        
        except Exception as e:
            print(f"Error getting slot statistics: {e}")
            return None
    
    def print_statistics(self):
        """Print current save slot statistics."""
        stats = self.get_slot_statistics()
        if not stats:
            return
        
        print("\n" + "="*50)
        print("SAVE SLOT STATISTICS")
        print("="*50)
        print(f"Total save slots in database: {stats['total_slots']}")
        print(f"Occupied slots: {stats['occupied_slots']}")
        print(f"Empty slots: {stats['empty_slots']}")
        print(f"Orphaned slots (marked occupied but no character): {stats['orphaned_slots']}")
        print(f"Highest slot number used: {stats['highest_slot_used']}")
        
        if stats['occupied_slot_numbers']:
            print(f"Occupied slot numbers: {sorted(stats['occupied_slot_numbers'])}")
        
        if stats['orphaned_slot_numbers']:
            print(f"Orphaned slot numbers: {sorted(stats['orphaned_slot_numbers'])}")
        
        print("="*50)
    
    def clean_orphaned_slots(self):
        """Clean up orphaned save slots (marked as occupied but no character exists)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find orphaned slots
            cursor.execute("""
                SELECT s.slot_number FROM save_slots s 
                LEFT JOIN characters c ON s.id = c.save_slot_id 
                WHERE s.is_occupied = 1 AND c.id IS NULL
            """)
            orphaned_slots = cursor.fetchall()
            
            if not orphaned_slots:
                print("No orphaned slots found.")
                return 0
            
            # Clean up orphaned slots
            orphaned_count = 0
            for slot in orphaned_slots:
                slot_number = slot[0]
                cursor.execute("""
                    UPDATE save_slots 
                    SET is_occupied = 0, character_name = NULL, character_level = NULL 
                    WHERE slot_number = ?
                """, (slot_number,))
                print(f"Cleaned up orphaned slot {slot_number}")
                orphaned_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"Cleaned up {orphaned_count} orphaned slots.")
            return orphaned_count
            
        except Exception as e:
            print(f"Error cleaning orphaned slots: {e}")
            return 0
    
    def consolidate_slots(self, dry_run=True):
        """Consolidate characters to use lower-numbered slots."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all characters with their slot numbers, ordered by creation date (oldest first)
            cursor.execute("""
                SELECT c.id, c.name, c.level, s.slot_number, c.created_at
                FROM characters c
                JOIN save_slots s ON c.save_slot_id = s.id
                ORDER BY c.created_at ASC
            """)
            characters = cursor.fetchall()
            
            if not characters:
                print("No characters found to consolidate.")
                conn.close()
                return
            
            print(f"\nFound {len(characters)} characters to consolidate:")
            moves_needed = []
            
            # Check which characters need to be moved to lower slots
            for i, char in enumerate(characters):
                target_slot = i + 1  # Start from slot 1
                current_slot = char['slot_number']
                
                if current_slot != target_slot:
                    moves_needed.append({
                        'character_id': char['id'],
                        'character_name': char['name'],
                        'level': char['level'], 
                        'from_slot': current_slot,
                        'to_slot': target_slot
                    })
                    print(f"  {char['name']} (Level {char['level']}) - Slot {current_slot} -> Slot {target_slot}")
                else:
                    print(f"  {char['name']} (Level {char['level']}) - Slot {current_slot} (no change)")
            
            if not moves_needed:
                print("All characters are already in optimal slots!")
                conn.close()
                return
            
            if dry_run:
                print(f"\nDRY RUN: Would move {len(moves_needed)} characters to consolidate slots.")
                print("Run with dry_run=False to actually perform the moves.")
                conn.close()
                return
            
            # Perform the actual moves
            print(f"\nMoving {len(moves_needed)} characters...")
            
            for move in moves_needed:
                # Create or update target slot
                cursor.execute("""
                    INSERT OR REPLACE INTO save_slots 
                    (slot_number, is_occupied, character_name, character_level, created_at)
                    VALUES (?, 1, ?, ?, datetime('now'))
                """, (move['to_slot'], move['character_name'], move['level']))
                
                # Get the new slot ID
                cursor.execute("SELECT id FROM save_slots WHERE slot_number = ?", (move['to_slot'],))
                new_slot_id = cursor.fetchone()['id']
                
                # Update character to point to new slot
                cursor.execute("""
                    UPDATE characters SET save_slot_id = ? WHERE id = ?
                """, (new_slot_id, move['character_id']))
                
                print(f"  Moved {move['character_name']} from slot {move['from_slot']} to slot {move['to_slot']}")
            
            # Clean up now-empty slots
            cursor.execute("""
                UPDATE save_slots 
                SET is_occupied = 0, character_name = NULL, character_level = NULL 
                WHERE id NOT IN (SELECT DISTINCT save_slot_id FROM characters)
            """)
            
            conn.commit()
            conn.close()
            
            print(f"Successfully consolidated {len(moves_needed)} characters to lower-numbered slots.")
            
        except Exception as e:
            print(f"Error consolidating slots: {e}")
    
    def remove_empty_slots(self, keep_slots=10):
        """Remove empty save slots above a certain number."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete empty slots above the keep_slots threshold
            cursor.execute("""
                DELETE FROM save_slots 
                WHERE slot_number > ? AND is_occupied = 0
            """, (keep_slots,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                print(f"Removed {deleted_count} empty slots above slot {keep_slots}.")
            else:
                print(f"No empty slots found above slot {keep_slots}.")
            
            return deleted_count
            
        except Exception as e:
            print(f"Error removing empty slots: {e}")
            return 0


def main():
    """Main cleanup function."""
    print("TaleKeeper Save Slot Cleanup Utility")
    
    cleanup = SaveSlotCleanup()
    
    # Show current statistics
    cleanup.print_statistics()
    
    # Clean orphaned slots
    print("\n1. Cleaning orphaned slots...")
    orphaned_cleaned = cleanup.clean_orphaned_slots()
    
    # Show consolidation preview
    print("\n2. Checking slot consolidation...")
    cleanup.consolidate_slots(dry_run=True)
    
    # Ask user if they want to proceed with consolidation
    if orphaned_cleaned > 0:
        print(f"\nCleaned up {orphaned_cleaned} orphaned slots.")
    
    print("\nTo actually consolidate slots, run:")
    print("python utilities/save_slot_cleanup.py --consolidate")
    
    print("\nTo remove empty slots above slot 10, run:")
    print("python utilities/save_slot_cleanup.py --remove-empty")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cleanup = SaveSlotCleanup()
        
        if '--consolidate' in sys.argv:
            print("Consolidating save slots...")
            cleanup.consolidate_slots(dry_run=False)
        
        if '--remove-empty' in sys.argv:
            print("Removing empty slots...")
            cleanup.remove_empty_slots(keep_slots=10)
            
        if '--stats' in sys.argv:
            cleanup.print_statistics()
    else:
        main()