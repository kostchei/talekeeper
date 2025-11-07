"""
Random Selector for Species and Backgrounds

Provides random selection of species (races) and backgrounds from the
TaleKeeper database. Used for test variety in character progression testing.
"""

import sqlite3
import random
from pathlib import Path
from typing import List, Optional, Tuple


class RandomSelector:
    """Randomly selects species and backgrounds from database for test variety."""

    @staticmethod
    def _get_db_connection(db_path: str) -> sqlite3.Connection:
        """Create a database connection."""
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        return sqlite3.connect(db_path)

    @classmethod
    def get_species_list(cls, db_path: str) -> List[Tuple[str, str]]:
        """
        Get list of all available species (races) from database.

        Args:
            db_path: Path to TaleKeeper database

        Returns:
            List of tuples (id, name) for all species

        Note:
            In the database, species are stored in the 'races' table.
        """
        with cls._get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name FROM races
                ORDER BY display_order, name
            """
            )
            return cursor.fetchall()

    @classmethod
    def get_background_list(cls, db_path: str) -> List[Tuple[str, str]]:
        """
        Get list of all available backgrounds from database.

        Args:
            db_path: Path to TaleKeeper database

        Returns:
            List of tuples (id, name) for all backgrounds
        """
        with cls._get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name FROM backgrounds
                ORDER BY display_order, name
            """
            )
            return cursor.fetchall()

    @classmethod
    def get_random_species(cls, db_path: str, seed: Optional[int] = None) -> Tuple[str, str]:
        """
        Get a random species (race) from the database.

        Args:
            db_path: Path to TaleKeeper database
            seed: Optional random seed for reproducible results

        Returns:
            Tuple of (species_id, species_name)

        Raises:
            ValueError: If no species found in database
        """
        if seed is not None:
            random.seed(seed)

        species_list = cls.get_species_list(db_path)

        if not species_list:
            raise ValueError("No species found in database")

        species_id, species_name = random.choice(species_list)
        return species_id, species_name

    @classmethod
    def get_random_background(cls, db_path: str, seed: Optional[int] = None) -> Tuple[str, str]:
        """
        Get a random background from the database.

        Args:
            db_path: Path to TaleKeeper database
            seed: Optional random seed for reproducible results

        Returns:
            Tuple of (background_id, background_name)

        Raises:
            ValueError: If no backgrounds found in database
        """
        if seed is not None:
            random.seed(seed)

        background_list = cls.get_background_list(db_path)

        if not background_list:
            raise ValueError("No backgrounds found in database")

        background_id, background_name = random.choice(background_list)
        return background_id, background_name

    @classmethod
    def get_random_pair(
        cls, db_path: str, seed: Optional[int] = None
    ) -> Tuple[Tuple[str, str], Tuple[str, str]]:
        """
        Get both a random species and random background.

        Args:
            db_path: Path to TaleKeeper database
            seed: Optional random seed for reproducible results

        Returns:
            Tuple of ((species_id, species_name), (background_id, background_name))
        """
        if seed is not None:
            random.seed(seed)

        species = cls.get_random_species(db_path, seed=None)  # Already seeded above
        background = cls.get_random_background(db_path, seed=None)

        return species, background

    @classmethod
    def get_species_by_name(cls, db_path: str, name: str) -> Optional[Tuple[str, str]]:
        """
        Get species by name (case-insensitive).

        Args:
            db_path: Path to TaleKeeper database
            name: Species name to find

        Returns:
            Tuple of (species_id, species_name) if found, None otherwise
        """
        with cls._get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name FROM races
                WHERE LOWER(name) = LOWER(?)
            """,
                (name,),
            )
            result = cursor.fetchone()
            return result if result else None

    @classmethod
    def get_background_by_name(cls, db_path: str, name: str) -> Optional[Tuple[str, str]]:
        """
        Get background by name (case-insensitive).

        Args:
            db_path: Path to TaleKeeper database
            name: Background name to find

        Returns:
            Tuple of (background_id, background_name) if found, None otherwise
        """
        with cls._get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name FROM backgrounds
                WHERE LOWER(name) = LOWER(?)
            """,
                (name,),
            )
            result = cursor.fetchone()
            return result if result else None

    @classmethod
    def resolve_species(
        cls, db_path: str, species_choice: str, seed: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Resolve species choice - either specific name or "random".

        Args:
            db_path: Path to TaleKeeper database
            species_choice: Either "random" or specific species name
            seed: Optional random seed for reproducible random selection

        Returns:
            Tuple of (species_id, species_name)

        Raises:
            ValueError: If species_choice is not found
        """
        if species_choice.lower() == "random":
            return cls.get_random_species(db_path, seed)

        # Try to find by name
        result = cls.get_species_by_name(db_path, species_choice)
        if result:
            return result

        raise ValueError(f"Species not found: {species_choice}")

    @classmethod
    def resolve_background(
        cls, db_path: str, background_choice: str, seed: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Resolve background choice - either specific name or "random".

        Args:
            db_path: Path to TaleKeeper database
            background_choice: Either "random" or specific background name
            seed: Optional random seed for reproducible random selection

        Returns:
            Tuple of (background_id, background_name)

        Raises:
            ValueError: If background_choice is not found
        """
        if background_choice.lower() == "random":
            return cls.get_random_background(db_path, seed)

        # Try to find by name
        result = cls.get_background_by_name(db_path, background_choice)
        if result:
            return result

        raise ValueError(f"Background not found: {background_choice}")


if __name__ == "__main__":
    # Demo/test script
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python random_selector.py <db_path> list")
        print("  python random_selector.py <db_path> random")
        print("  python random_selector.py <db_path> find species <name>")
        print("  python random_selector.py <db_path> find background <name>")
        sys.exit(1)

    db_path = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "random"

    try:
        if command == "list":
            print("\n=== Available Species ===")
            species_list = RandomSelector.get_species_list(db_path)
            for species_id, species_name in species_list:
                print(f"  {species_id}: {species_name}")

            print("\n=== Available Backgrounds ===")
            background_list = RandomSelector.get_background_list(db_path)
            for bg_id, bg_name in background_list:
                print(f"  {bg_id}: {bg_name}")

        elif command == "random":
            species, background = RandomSelector.get_random_pair(db_path)
            print(f"\nRandom Selection:")
            print(f"  Species: {species[1]} (id: {species[0]})")
            print(f"  Background: {background[1]} (id: {background[0]})")

        elif command == "find":
            if len(sys.argv) < 5:
                print("Error: Missing arguments for find command")
                sys.exit(1)

            find_type = sys.argv[3]  # "species" or "background"
            find_name = sys.argv[4]

            if find_type == "species":
                result = RandomSelector.get_species_by_name(db_path, find_name)
                if result:
                    print(f"\nFound Species: {result[1]} (id: {result[0]})")
                else:
                    print(f"\nSpecies not found: {find_name}")

            elif find_type == "background":
                result = RandomSelector.get_background_by_name(db_path, find_name)
                if result:
                    print(f"\nFound Background: {result[1]} (id: {result[0]})")
                else:
                    print(f"\nBackground not found: {find_name}")

            else:
                print(f"Error: Unknown find type: {find_type}")
                sys.exit(1)

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
