"""
File: backend/routers/combat.py
Path: /backend/routers/combat.py

Pseudo Code:
1. Start combat: roll initiative, create encounter, setup turn order
2. Process actions: validate turn, execute action, update state, check win/lose
3. Get state: return current combat status, participants, turn order
4. End combat: calculate XP/loot, award rewards, update character
5. Skip turns: advance turn order, handle timeouts

Combat System Router
Handles all combat-related operations including encounters, turn management, and actions.

AI Agents: Key endpoints:
- POST /start - Initialize new combat encounter
- POST /action - Process player combat actions
- GET /state - Get current combat state
- POST /end - End combat and calculate rewards
- GET /turn-order - Get initiative order
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
import json
from loguru import logger
from datetime import datetime

from database import get_db, GameQueries
from models.character import Character
from models.combat import (
    CombatEncounter, CombatAction, CombatState, CombatParticipant,
    CombatActionRequest, CombatActionResponse, CombatStateResponse,
    EncounterStartRequest, EncounterEndResponse
)
from models.monsters import Monster
from services.combat_engine import CombatEngine
from services.dice import DiceRoller

router = APIRouter()
dice = DiceRoller()

@router.post("/start", response_model=Dict[str, Any])
async def start_combat(
    encounter_data: EncounterStartRequest,
    db: Session = Depends(get_db)
):
    """
    Initialize a new combat encounter.
    
    Creates combat state, rolls initiative, and sets up turn order.
    
    AI Agents: Extend for:
    - Environmental hazards
    - Surprise rounds
    - Multiple monster groups
    """
    try:
        engine = CombatEngine(db)
        
        # Validate character exists
        character = db.get(Character, encounter_data.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Validate monsters exist
        monsters = []
        for monster_id in encounter_data.monster_ids:
            monster = db.get(Monster, monster_id)
            if not monster:
                raise HTTPException(status_code=404, detail=f"Monster {monster_id} not found")
            monsters.append(monster)
        
        # Create combat encounter
        encounter = CombatEncounter(
            id=uuid4(),
            character_id=encounter_data.character_id,
            location=encounter_data.location or "Unknown",
            environment_effects=encounter_data.environment_effects or {},
            is_active=True,
            started_at=datetime.utcnow()
        )
        
        db.add(encounter)
        db.flush()  # Get encounter ID
        
        # Roll initiative for all participants
        participants = []
        
        # Character initiative
        char_init_bonus = GameQueries.ability_modifier(character.dexterity)
        char_initiative = dice.roll("1d20") + char_init_bonus
        
        char_participant = CombatParticipant(
            encounter_id=encounter.id,
            character_id=character.id,
            monster_id=None,
            initiative=char_initiative,
            current_hp=character.current_hit_points,
            max_hp=character.max_hit_points,
            armor_class=character.armor_class,
            conditions=[],
            position=encounter_data.character_position or "melee",
            is_active=True
        )
        participants.append(char_participant)
        
        # Monster initiatives
        for i, monster in enumerate(monsters):
            monster_init_bonus = GameQueries.ability_modifier(monster.dexterity)
            monster_initiative = dice.roll("1d20") + monster_init_bonus
            
            monster_participant = CombatParticipant(
                encounter_id=encounter.id,
                character_id=None,
                monster_id=monster.id,
                initiative=monster_initiative,
                current_hp=monster.hit_points,
                max_hp=monster.hit_points,
                armor_class=monster.armor_class,
                conditions=[],
                position=encounter_data.monster_positions[i] if i < len(encounter_data.monster_positions) else "melee",
                is_active=True
            )
            participants.append(monster_participant)
        
        # Sort by initiative (highest first, then dexterity modifier)
        participants.sort(key=lambda p: (p.initiative, 
                                       GameQueries.ability_modifier(character.dexterity) if p.character_id else 
                                       GameQueries.ability_modifier(monsters[0].dexterity)), reverse=True)
        
        # Add participants to database
        for participant in participants:
            db.add(participant)
        
        # Create initial combat state
        combat_state = CombatState(
            encounter_id=encounter.id,
            current_round=1,
            current_turn=0,
            turn_order=[p.id for p in participants],
            actions_taken=[],
            combat_log=[f"Combat started! Initiative order determined."]
        )
        
        db.add(combat_state)
        db.commit()
        
        # Get turn order with participant details
        turn_order = []
        for participant in participants:
            if participant.character_id:
                turn_order.append({
                    "type": "character",
                    "id": str(participant.character_id),
                    "name": character.name,
                    "initiative": participant.initiative,
                    "hp": participant.current_hp,
                    "max_hp": participant.max_hp,
                    "ac": participant.armor_class,
                    "position": participant.position
                })
            else:
                monster = next(m for m in monsters if m.id == participant.monster_id)
                turn_order.append({
                    "type": "monster",
                    "id": str(participant.monster_id),
                    "name": monster.name,
                    "initiative": participant.initiative,
                    "hp": participant.current_hp,
                    "max_hp": participant.max_hp,
                    "ac": participant.armor_class,
                    "position": participant.position
                })
        
        return {
            "encounter_id": str(encounter.id),
            "round": 1,
            "turn": 0,
            "current_actor": turn_order[0] if turn_order else None,
            "turn_order": turn_order,
            "combat_log": ["Combat started! Initiative order determined."],
            "message": f"Combat begins! {turn_order[0]['name'] if turn_order else 'Unknown'} goes first."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting combat: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to start combat")

@router.post("/action", response_model=CombatActionResponse)
async def process_combat_action(
    action_data: CombatActionRequest,
    db: Session = Depends(get_db)
):
    """
    Process a combat action from player or AI.
    
    Handles attacks, spells, movement, and other combat actions.
    Validates action economy and updates combat state.
    
    AI Agents: Extend for:
    - Spell casting with components and slots
    - Complex reactions and opportunity attacks
    - Environmental interactions
    """
    try:
        engine = CombatEngine(db)
        
        # Get combat state
        encounter = db.get(CombatEncounter, action_data.encounter_id)
        if not encounter or not encounter.is_active:
            raise HTTPException(status_code=404, detail="Active combat encounter not found")
        
        combat_state = db.execute(
            select(CombatState).where(CombatState.encounter_id == encounter.id)
        ).scalar_one_or_none()
        
        if not combat_state:
            raise HTTPException(status_code=404, detail="Combat state not found")
        
        # Get current actor
        turn_order = combat_state.turn_order
        current_participant_id = turn_order[combat_state.current_turn]
        
        current_participant = db.execute(
            select(CombatParticipant).where(CombatParticipant.id == current_participant_id)
        ).scalar_one_or_none()
        
        if not current_participant:
            raise HTTPException(status_code=404, detail="Current participant not found")
        
        # Validate it's the correct actor's turn
        actor_id = action_data.actor_id
        if current_participant.character_id and str(current_participant.character_id) != str(actor_id):
            raise HTTPException(status_code=400, detail="Not your turn")
        elif current_participant.monster_id and str(current_participant.monster_id) != str(actor_id):
            raise HTTPException(status_code=400, detail="Not this monster's turn")
        
        # Process the action
        result = await engine.process_action(
            encounter_id=encounter.id,
            actor_participant=current_participant,
            action_type=action_data.action_type,
            target_id=action_data.target_id,
            action_details=action_data.action_details
        )
        
        # Update combat log
        combat_log = combat_state.combat_log.copy() if combat_state.combat_log else []
        combat_log.extend(result["log_entries"])
        combat_state.combat_log = combat_log
        
        # Check if any participants are defeated
        defeated_participants = []
        active_participants = db.execute(
            select(CombatParticipant).where(
                and_(CombatParticipant.encounter_id == encounter.id, CombatParticipant.is_active == True)
            )
        ).scalars().all()
        
        for participant in active_participants:
            if participant.current_hp <= 0:
                participant.is_active = False
                defeated_participants.append(participant)
                
                if participant.character_id:
                    combat_log.append(f"{participant.character.name} has fallen!")
                else:
                    monster = db.get(Monster, participant.monster_id)
                    combat_log.append(f"{monster.name} has been defeated!")
        
        # Check for combat end conditions
        character_alive = any(p.character_id and p.is_active and p.current_hp > 0 for p in active_participants)
        monsters_alive = any(p.monster_id and p.is_active and p.current_hp > 0 for p in active_participants)
        
        combat_ended = False
        victory = False
        
        if not character_alive:
            # Character defeated
            encounter.is_active = False
            encounter.ended_at = datetime.utcnow()
            combat_ended = True
            victory = False
            combat_log.append("Defeat! The character has fallen.")
            
        elif not monsters_alive:
            # All monsters defeated
            encounter.is_active = False
            encounter.ended_at = datetime.utcnow()
            combat_ended = True
            victory = True
            combat_log.append("Victory! All enemies have been defeated.")
        
        # Advance turn if not combat ended
        if not combat_ended:
            combat_state.current_turn = (combat_state.current_turn + 1) % len(turn_order)
            
            # New round if we've cycled through all participants
            if combat_state.current_turn == 0:
                combat_state.current_round += 1
                combat_log.append(f"Round {combat_state.current_round} begins!")
        
        # Record the action
        action_record = CombatAction(
            encounter_id=encounter.id,
            actor_participant_id=current_participant.id,
            action_type=action_data.action_type,
            target_participant_id=action_data.target_id,
            action_details=action_data.action_details,
            result=result,
            round_number=combat_state.current_round,
            timestamp=datetime.utcnow()
        )
        
        db.add(action_record)
        combat_state.combat_log = combat_log
        
        db.commit()
        
        # Prepare response
        response_data = {
            "success": True,
            "action_result": result,
            "combat_ended": combat_ended,
            "victory": victory if combat_ended else None,
            "current_round": combat_state.current_round,
            "current_turn": combat_state.current_turn,
            "combat_log": combat_log[-5:],  # Last 5 entries
            "participants_status": []
        }
        
        # Add participant status
        for participant in active_participants:
            if participant.character_id:
                char = db.get(Character, participant.character_id)
                response_data["participants_status"].append({
                    "type": "character",
                    "id": str(participant.character_id),
                    "name": char.name,
                    "hp": participant.current_hp,
                    "max_hp": participant.max_hp,
                    "conditions": participant.conditions,
                    "is_active": participant.is_active
                })
            else:
                monster = db.get(Monster, participant.monster_id)
                response_data["participants_status"].append({
                    "type": "monster",
                    "id": str(participant.monster_id),
                    "name": monster.name,
                    "hp": participant.current_hp,
                    "max_hp": participant.max_hp,
                    "conditions": participant.conditions,
                    "is_active": participant.is_active
                })
        
        return CombatActionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing combat action: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process combat action")

@router.get("/state/{encounter_id}", response_model=CombatStateResponse)
async def get_combat_state(
    encounter_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get current combat state including turn order and participant status.
    
    AI Agents: Use for:
    - UI updates
    - AI decision making
    - Combat state persistence
    """
    try:
        encounter = db.get(CombatEncounter, encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="Combat encounter not found")
        
        combat_state = db.execute(
            select(CombatState).where(CombatState.encounter_id == encounter.id)
        ).scalar_one_or_none()
        
        if not combat_state:
            raise HTTPException(status_code=404, detail="Combat state not found")
        
        # Get all participants
        participants = db.execute(
            select(CombatParticipant).where(CombatParticipant.encounter_id == encounter.id)
        ).scalars().all()
        
        # Build participant details
        participant_details = []
        for participant in participants:
            if participant.character_id:
                character = db.get(Character, participant.character_id)
                participant_details.append({
                    "id": str(participant.id),
                    "type": "character",
                    "entity_id": str(participant.character_id),
                    "name": character.name,
                    "initiative": participant.initiative,
                    "current_hp": participant.current_hp,
                    "max_hp": participant.max_hp,
                    "armor_class": participant.armor_class,
                    "conditions": participant.conditions,
                    "position": participant.position,
                    "is_active": participant.is_active
                })
            else:
                monster = db.get(Monster, participant.monster_id)
                participant_details.append({
                    "id": str(participant.id),
                    "type": "monster",
                    "entity_id": str(participant.monster_id),
                    "name": monster.name,
                    "initiative": participant.initiative,
                    "current_hp": participant.current_hp,
                    "max_hp": participant.max_hp,
                    "armor_class": participant.armor_class,
                    "conditions": participant.conditions,
                    "position": participant.position,
                    "is_active": participant.is_active
                })
        
        # Get current actor
        current_actor = None
        if combat_state.turn_order and encounter.is_active:
            current_participant_id = combat_state.turn_order[combat_state.current_turn]
            current_actor = next((p for p in participant_details if p["id"] == str(current_participant_id)), None)
        
        return CombatStateResponse(
            encounter_id=encounter.id,
            is_active=encounter.is_active,
            current_round=combat_state.current_round,
            current_turn=combat_state.current_turn,
            current_actor=current_actor,
            participants=participant_details,
            combat_log=combat_state.combat_log or [],
            environment_effects=encounter.environment_effects or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting combat state: {e}")
        raise HTTPException(status_code=500, detail="Failed to get combat state")

@router.post("/end/{encounter_id}", response_model=EncounterEndResponse)
async def end_combat(
    encounter_id: UUID,
    force_end: bool = False,
    db: Session = Depends(get_db)
):
    """
    End combat encounter and calculate rewards.
    
    Calculates XP based on defeated monsters and awards loot.
    
    AI Agents: Extend for:
    - Complex XP calculations (CR-based)
    - Magic item identification
    - Milestone leveling
    """
    try:
        encounter = db.get(CombatEncounter, encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="Combat encounter not found")
        
        if not encounter.is_active and not force_end:
            raise HTTPException(status_code=400, detail="Combat is already ended")
        
        # Get participants
        participants = db.execute(
            select(CombatParticipant).where(CombatParticipant.encounter_id == encounter.id)
        ).scalars().all()
        
        character_participant = next((p for p in participants if p.character_id), None)
        if not character_participant:
            raise HTTPException(status_code=404, detail="Character not found in combat")
        
        character = db.get(Character, character_participant.character_id)
        monster_participants = [p for p in participants if p.monster_id and not p.is_active]
        
        # Calculate XP from defeated monsters
        total_xp = 0
        defeated_monsters = []
        
        for monster_participant in monster_participants:
            monster = db.get(Monster, monster_participant.monster_id)
            xp_value = monster.experience_value if hasattr(monster, 'experience_value') else monster.challenge_rating * 100
            total_xp += xp_value
            defeated_monsters.append({
                "name": monster.name,
                "cr": monster.challenge_rating,
                "xp": xp_value
            })
        
        # Award XP to character
        old_xp = character.experience_points
        character.experience_points += total_xp
        
        # Check for level up
        leveled_up = False
        old_level = character.level
        
        # Simple XP table for levels 1-3 (MVP scope)
        xp_table = {1: 0, 2: 300, 3: 900, 4: 2700}
        next_level_xp = xp_table.get(character.level + 1, float('inf'))
        
        if character.experience_points >= next_level_xp and character.level < 3:
            leveled_up = True
            character.level += 1
            
            # Increase HP (average + CON modifier)
            from models.classes import Class
            char_class = db.get(Class, character.class_id)
            con_mod = GameQueries.ability_modifier(character.constitution)
            hp_increase = (char_class.hit_die // 2 + 1) + con_mod
            character.max_hit_points += max(1, hp_increase)
            character.current_hit_points += max(1, hp_increase)
            
            # Update proficiency bonus
            character.proficiency_bonus = GameQueries.get_proficiency_bonus(character.level)
        
        # Generate loot (simple implementation)
        loot_generated = []
        for monster_participant in monster_participants:
            monster = db.get(Monster, monster_participant.monster_id)
            # Simple loot: gold based on CR
            gold_amount = dice.roll(f"{monster.challenge_rating}d4") * 10
            if gold_amount > 0:
                loot_generated.append({
                    "type": "currency",
                    "name": "Gold Pieces",
                    "amount": gold_amount
                })
        
        # End the encounter
        encounter.is_active = False
        encounter.ended_at = datetime.utcnow()
        
        # Update character HP from combat damage
        character.current_hit_points = character_participant.current_hp
        
        db.commit()
        
        return EncounterEndResponse(
            encounter_id=encounter.id,
            victory=len(defeated_monsters) > 0,
            xp_gained=total_xp,
            total_xp=character.experience_points,
            leveled_up=leveled_up,
            old_level=old_level,
            new_level=character.level,
            defeated_monsters=defeated_monsters,
            loot_generated=loot_generated,
            character_final_hp=character.current_hit_points
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending combat: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to end combat")

@router.get("/turn-order/{encounter_id}")
async def get_turn_order(
    encounter_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get initiative order for combat encounter.
    
    AI Agents: Use for displaying turn order in UI.
    """
    try:
        combat_state = db.execute(
            select(CombatState).where(CombatState.encounter_id == encounter_id)
        ).scalar_one_or_none()
        
        if not combat_state:
            raise HTTPException(status_code=404, detail="Combat state not found")
        
        # Get participant details in turn order
        turn_order = []
        for participant_id in combat_state.turn_order:
            participant = db.execute(
                select(CombatParticipant).where(CombatParticipant.id == participant_id)
            ).scalar_one_or_none()
            
            if not participant:
                continue
                
            if participant.character_id:
                character = db.get(Character, participant.character_id)
                turn_order.append({
                    "type": "character",
                    "id": str(participant.character_id),
                    "name": character.name,
                    "initiative": participant.initiative,
                    "is_current": combat_state.current_turn == len(turn_order)
                })
            else:
                monster = db.get(Monster, participant.monster_id)
                turn_order.append({
                    "type": "monster",
                    "id": str(participant.monster_id),
                    "name": monster.name,
                    "initiative": participant.initiative,
                    "is_current": combat_state.current_turn == len(turn_order)
                })
        
        return {
            "round": combat_state.current_round,
            "current_turn": combat_state.current_turn,
            "turn_order": turn_order
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting turn order: {e}")
        raise HTTPException(status_code=500, detail="Failed to get turn order")

@router.post("/{encounter_id}/skip-turn")
async def skip_turn(
    encounter_id: UUID,
    actor_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Skip current actor's turn.
    
    AI Agents: Use for:
    - Dodging actions
    - Delaying turns
    - AI timeout handling
    """
    try:
        encounter = db.get(CombatEncounter, encounter_id)
        if not encounter or not encounter.is_active:
            raise HTTPException(status_code=404, detail="Active combat encounter not found")
        
        combat_state = db.execute(
            select(CombatState).where(CombatState.encounter_id == encounter.id)
        ).scalar_one_or_none()
        
        if not combat_state:
            raise HTTPException(status_code=404, detail="Combat state not found")
        
        # Advance turn
        turn_order = combat_state.turn_order
        combat_state.current_turn = (combat_state.current_turn + 1) % len(turn_order)
        
        # New round if we've cycled through all participants
        if combat_state.current_turn == 0:
            combat_state.current_round += 1
            
        # Update combat log
        combat_log = combat_state.combat_log.copy() if combat_state.combat_log else []
        combat_log.append(f"Turn skipped. Round {combat_state.current_round}, Turn {combat_state.current_turn + 1}")
        combat_state.combat_log = combat_log
        
        db.commit()
        
        return {
            "success": True,
            "message": "Turn skipped",
            "current_round": combat_state.current_round,
            "current_turn": combat_state.current_turn
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error skipping turn: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to skip turn")