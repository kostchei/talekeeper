"""
File: backend/services/encounter_service.py
Path: /backend/services/encounter_service.py

Encounter generation service implementing D&D 2024 encounter building rules with random bag system.

Pseudo Code:
1. Determine encounter difficulty using weighted random (50% easy, 40% medium, 10% hard)
2. Get XP budget for party level and chosen difficulty from database
3. Filter monsters by CR constraint (max CR = total party levels / 4)
4. Use random bag system to select monsters without immediate repeats
5. Build encounter within XP budget using selected monsters
6. Update character's random bag state in database

AI Agents: This service ensures varied encounters while respecting D&D balance guidelines.
"""

import random
import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger

from database import get_db
from models.game import GameState
from models.monsters import Monster
from models.character import Character


class EncounterService:
    """Handles encounter generation with D&D 2024 rules and random bag variety system."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_encounter(self, character_id: str, location_type: str = "dungeon") -> Dict[str, Any]:
        """
        Generate a balanced encounter for the character using random bag system.
        
        Args:
            character_id: UUID of the character
            location_type: Type of location ("dungeon", "wilderness", "urban", etc.)
            
        Returns:
            Dict containing encounter details: monsters, difficulty, total_xp, etc.
        """
        # Get character's game state and level
        game_state = self.db.query(GameState).filter(GameState.character_id == character_id).first()
        if not game_state:
            raise ValueError(f"No game state found for character {character_id}")
            
        # For now, assume single character (party size = 1)
        # TODO: Expand for party support
        party_level = game_state.character.level
        party_size = 1
        
        # Step 1: Determine encounter difficulty (50% easy, 40% medium, 10% hard)
        difficulty = self._roll_encounter_difficulty()
        
        # Step 2: Get XP budget for this difficulty
        xp_budget = self._get_xp_budget(party_level, difficulty)
        
        # Step 3: Get available monsters with CR constraints
        max_cr = self._calculate_max_cr(party_level, party_size)
        available_monsters = self._get_available_monsters(max_cr)
        
        if not available_monsters:
            logger.warning(f"No monsters available for max CR {max_cr}")
            return self._create_empty_encounter()
        
        # Step 4: Use random bag to select monsters
        selected_monsters = self._select_monsters_from_bag(
            game_state, location_type, available_monsters, xp_budget
        )
        
        if not selected_monsters:
            logger.warning(f"Could not build encounter within budget {xp_budget} XP")
            return self._create_empty_encounter()
        
        # Step 5: Build encounter details
        encounter = self._build_encounter_details(selected_monsters, difficulty, xp_budget)
        
        # Step 6: Update random bag state
        self._update_random_bag_state(game_state, location_type, selected_monsters)
        
        logger.info(f"Generated {difficulty} encounter: {len(selected_monsters)} monsters, "
                   f"{encounter['total_xp']} XP (budget: {xp_budget})")
        
        return encounter
    
    def _roll_encounter_difficulty(self) -> str:
        """Roll encounter difficulty: 50% easy, 40% medium, 10% hard."""
        roll = random.random()
        if roll < 0.5:
            return "easy"
        elif roll < 0.9:  # 0.5 to 0.9 = 40%
            return "medium" 
        else:
            return "hard"
    
    def _get_xp_budget(self, party_level: int, difficulty: str) -> int:
        """Get XP budget from database for given level and difficulty."""
        # Map difficulty names to column names
        difficulty_column = {
            "easy": "easy_xp",
            "medium": "medium_xp", 
            "hard": "hard_xp"
        }
        
        column = difficulty_column.get(difficulty, "medium_xp")
        
        # Query the XP budget table
        result = self.db.execute(
            text(f"SELECT {column} FROM encounter_xp_budgets WHERE party_level = :level"),
            {"level": party_level}
        ).first()
        
        if not result:
            logger.warning(f"No XP budget found for level {party_level}, using default")
            # Fallback values for level 1
            defaults = {"easy": 50, "medium": 75, "hard": 100}
            return defaults.get(difficulty, 75)
        
        return result[0]
    
    def _calculate_max_cr(self, party_level: int, party_size: int) -> float:
        """Calculate maximum CR allowed: total levels / 4."""
        total_levels = party_level * party_size
        max_cr = total_levels / 4.0
        
        # Round to nearest valid CR (0.125, 0.25, 0.5, 1, 2, etc.)
        if max_cr <= 0.125:
            return 0.125
        elif max_cr <= 0.25:
            return 0.25
        elif max_cr <= 0.5:
            return 0.5
        else:
            return float(int(max_cr))  # Round down to nearest integer
    
    def _get_available_monsters(self, max_cr: float) -> List[Monster]:
        """Get all monsters with CR <= max_cr."""
        return self.db.query(Monster).filter(Monster.challenge_rating <= max_cr).all()
    
    def _select_monsters_from_bag(self, game_state: GameState, location_type: str, 
                                 available_monsters: List[Monster], xp_budget: int) -> List[Monster]:
        """Select monsters using random bag system to ensure variety."""
        # Get current bag state
        bag_remaining = game_state.encounter_bag_remaining or {}
        bag_history = game_state.encounter_bag_history or {}
        
        # Initialize bag for this location type if empty
        if location_type not in bag_remaining or not bag_remaining[location_type]:
            monster_ids = [m.id for m in available_monsters]
            bag_remaining[location_type] = monster_ids.copy()
            logger.debug(f"Refilled encounter bag for {location_type}: {len(monster_ids)} monsters")
        
        # Get monsters available in bag
        available_ids = bag_remaining[location_type]
        bag_monsters = [m for m in available_monsters if m.id in available_ids]
        
        if not bag_monsters:
            # Emergency refill if bag is empty but no monsters available
            logger.warning(f"Encounter bag empty for {location_type}, emergency refill")
            monster_ids = [m.id for m in available_monsters]
            bag_remaining[location_type] = monster_ids.copy()
            bag_monsters = available_monsters.copy()
        
        # Build encounter within XP budget
        selected_monsters = []
        current_xp = 0
        
        # Try to build encounter using available monsters
        attempts = 0
        max_attempts = 20  # Prevent infinite loops
        
        while current_xp < xp_budget and bag_monsters and attempts < max_attempts:
            attempts += 1
            
            # Randomly select a monster from bag
            monster = random.choice(bag_monsters)
            
            # Check if adding this monster would exceed budget
            if current_xp + monster.xp_value <= xp_budget:
                selected_monsters.append(monster)
                current_xp += monster.xp_value
                
                # Remove monster from available bag monsters for this encounter
                # but don't remove from bag state yet - we'll do that after encounter is built
                bag_monsters.remove(monster)
            else:
                # Try smaller monsters only
                bag_monsters = [m for m in bag_monsters if m.xp_value <= (xp_budget - current_xp)]
        
        return selected_monsters
    
    def _build_encounter_details(self, monsters: List[Monster], difficulty: str, xp_budget: int) -> Dict[str, Any]:
        """Build the complete encounter details dictionary."""
        total_xp = sum(m.xp_value for m in monsters)
        
        return {
            "monsters": [
                {
                    "id": m.id,
                    "name": m.name,
                    "challenge_rating": float(m.challenge_rating) if m.challenge_rating else 0.25,
                    "xp_value": m.xp_value or 50,
                    "armor_class": m.armor_class or 10,
                    "hit_points": m.hit_points or 1,
                    "size": m.size or "medium",
                    "type": m.type or "humanoid",
                    "alignment": m.alignment or "neutral",
                    "speed": m.speed or {"walk": 30},
                    "strength": m.strength or 10,
                    "dexterity": m.dexterity or 10,
                    "constitution": m.constitution or 10,
                    "intelligence": m.intelligence or 10,
                    "wisdom": m.wisdom or 10,
                    "charisma": m.charisma or 10,
                    "saving_throws": m.saving_throws or {},
                    "skills": m.skills or {},
                    "damage_resistances": m.damage_resistances or [],
                    "damage_immunities": m.damage_immunities or [],
                    "condition_immunities": m.condition_immunities or [],
                    "senses": m.senses or {},
                    "languages": m.languages or [],
                    "actions": m.actions or [],
                    "reactions": m.reactions or [],
                    "legendary_actions": m.legendary_actions or [],
                    "ai_script": m.ai_script or "basic_melee",
                    "special_abilities": []  # For frontend display
                }
                for m in monsters
            ],
            "difficulty": difficulty,
            "total_xp": total_xp,
            "xp_budget": xp_budget,
            "encounter_type": "combat",
            "monster_count": len(monsters)
        }
    
    def _update_random_bag_state(self, game_state: GameState, location_type: str, 
                                selected_monsters: List[Monster]) -> None:
        """Update the character's random bag state after encounter selection."""
        bag_remaining = game_state.encounter_bag_remaining or {}
        bag_history = game_state.encounter_bag_history or {}
        
        # Remove selected monsters from bag
        if location_type in bag_remaining:
            for monster in selected_monsters:
                if monster.id in bag_remaining[location_type]:
                    bag_remaining[location_type].remove(monster.id)
        
        # Add to history
        if location_type not in bag_history:
            bag_history[location_type] = []
        
        for monster in selected_monsters:
            if monster.id not in bag_history[location_type]:
                bag_history[location_type].append(monster.id)
        
        # Update game state
        game_state.encounter_bag_remaining = bag_remaining
        game_state.encounter_bag_history = bag_history
        self.db.commit()
        
        logger.debug(f"Updated bag state: {len(bag_remaining.get(location_type, []))} remaining, "
                    f"{len(bag_history.get(location_type, []))} in history")
    
    def _create_empty_encounter(self) -> Dict[str, Any]:
        """Create an empty encounter when generation fails."""
        return {
            "monsters": [],
            "difficulty": "easy",
            "total_xp": 0,
            "xp_budget": 0,
            "encounter_type": "none",
            "monster_count": 0,
            "error": "Could not generate encounter"
        }


def get_encounter_service(db: Session = None) -> EncounterService:
    """Dependency injection for encounter service."""
    if db is None:
        db = next(get_db())
    return EncounterService(db)