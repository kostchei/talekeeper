# Skill Challenge System Implementation Plan

## Overview
Implementation of a D&D 2024 skill challenge system allowing players to attempt various challenges using multiple skills with escalating difficulty and meaningful consequences.

## Core Requirements

### Challenge Structure
- **Success Condition**: 3 successes before 3 failures
- **DC Escalation**: Each repeated skill use increases DC by 1 for that challenge instance
- **Information Transparency**:
  - 75% of time: success rewards revealed
  - 25% of time: success rewards hidden
  - 50% of time: failure consequences revealed
  - 100% of time: refusal consequences known

### Challenge Definition Format
```json
{
  "name": "Challenge Name",
  "skills": ["Skill1", "Skill2", "Skill3"],
  "success": ["Reward1", "Reward2"],
  "failure": ["Penalty1", "Penalty2"],
  "refuse": ["Cost1", "Cost2"]
}
```

## Database Schema

### New Tables

#### skill_challenge_templates
```sql
CREATE TABLE skill_challenge_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    base_dc INTEGER NOT NULL DEFAULT 14,
    skills_json TEXT NOT NULL, -- JSON array of skill names
    success_options_json TEXT NOT NULL, -- JSON array of success outcomes
    failure_options_json TEXT NOT NULL, -- JSON array of failure outcomes
    refuse_options_json TEXT NOT NULL, -- JSON array of refusal outcomes
    min_level INTEGER DEFAULT 1,
    max_level INTEGER DEFAULT 20,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### skill_challenge_sessions
```sql
CREATE TABLE skill_challenge_sessions (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    template_id TEXT NOT NULL,
    challenge_name TEXT NOT NULL,
    base_dc INTEGER NOT NULL,
    current_successes INTEGER DEFAULT 0,
    current_failures INTEGER DEFAULT 0,
    skill_usage_json TEXT DEFAULT '{}', -- JSON object tracking DC increases per skill
    success_revealed BOOLEAN DEFAULT TRUE,
    failure_revealed BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    outcome TEXT, -- 'success', 'failure', 'refused'

    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES skill_challenge_templates(id)
);
```

#### skill_challenge_attempts
```sql
CREATE TABLE skill_challenge_attempts (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    ability_modifier INTEGER NOT NULL,
    proficiency_bonus INTEGER NOT NULL,
    dc INTEGER NOT NULL,
    roll_result INTEGER NOT NULL,
    total_result INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    attempt_order INTEGER NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES skill_challenge_sessions(id) ON DELETE CASCADE
);
```

## Core Implementation Files

### 1. services/skill_challenge_manager.py
**Purpose**: Core skill challenge mechanics and session management

```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
import random
from uuid import uuid4

@dataclass
class SkillChallengeTemplate:
    id: str
    name: str
    skills: List[str]
    success_options: List[str]
    failure_options: List[str]
    refuse_options: List[str]
    base_dc: int = 14

@dataclass
class SkillChallengeSession:
    id: str
    character_id: str
    template: SkillChallengeTemplate
    successes: int = 0
    failures: int = 0
    skill_usage: Dict[str, int] = field(default_factory=dict)
    success_revealed: bool = True
    failure_revealed: bool = True
    is_active: bool = True

class SkillChallengeManager:
    def create_session(character_id: str, template: SkillChallengeTemplate) -> SkillChallengeSession
    def attempt_skill(session_id: str, skill_name: str, character_data: dict) -> SkillAttemptResult
    def get_skill_dc(session_id: str, skill_name: str) -> int
    def check_completion(session_id: str) -> Optional[str]
    def apply_outcome(session_id: str, outcome: str, character_data: dict) -> None
```

### 2. encounter_pane/skill_challenge_widget.py
**Purpose**: UI widget for skill challenge interface

Key components:
- Challenge description display
- Available skills as clickable cards
- Success/failure tracker (3/3 display)
- DC indicator per skill
- Refuse/Accept buttons
- Roll result display
- Outcome application interface

### 3. services/skill_challenge_rewards.py
**Purpose**: Handle reward and penalty application

```python
class SkillChallengeRewards:
    def apply_success_reward(character_data: dict, reward: str) -> dict
    def apply_failure_penalty(character_data: dict, penalty: str) -> dict
    def apply_refuse_cost(character_data: dict, cost: str) -> dict
```

### 4. database/migrations/XXX_skill_challenges.sql
**Purpose**: Database schema migration

## Reward/Penalty System

### Success Rewards
- **Rest**: Gain benefits of short/long rest
- **Rations**: Gain food/water supplies
- **View of 2 hexes**: Exploration benefit
- **Easy Quest**: Quest difficulty modifier
- **Coin**: Gold/silver rewards
- **Items**: Equipment rewards

### Failure Penalties
- **Exhaustion**: Add exhaustion level
- **Falling damage**: HP loss (1d6 to 4d6 based on challenge)
- **Poison condition**: Apply poisoned condition
- **Hard Quest**: Quest difficulty modifier
- **Rations**: Lose food/water supplies
- **HP Loss**: Direct hit point damage

### Implementation Details
- **Damage**: Apply directly to current HP, log in encounter panel
- **Conditions**: Use existing condition system
- **Items**: Add/remove from character inventory
- **Rest Benefits**: Restore HP, spell slots, class resources

## UI Integration

### Encounter Panel Integration
1. Add "Skill Challenge" to encounter type dropdown
2. Replace monster display with skill challenge widget
3. Integrate with existing combat action system
4. Use existing logging system for results

### Skill Cards Display
- Grid layout showing available skills
- Each card shows: Skill Name, Ability, Current DC
- Disabled state for unavailable skills
- Visual feedback for success/failure tracking

### Information Display
- Challenge name and description
- Success condition (if revealed): "Success: Rest, Rations, or View of 2 hexes"
- Failure warning (if revealed): "Failure: Exhaustion, Falling damage, or Poison"
- Refusal cost: "Refuse: Costs 1 ration"
- Progress tracker: "Successes: 2/3, Failures: 1/3"

## Challenge Templates

### Example Challenges
```json
[
  {
    "name": "Scaling and Climbing",
    "skills": ["Athletics", "Acrobatics", "Survival"],
    "success": ["Rest", "Rations", "View of 2 hexes"],
    "failure": ["Exhaustion", "Falling damage", "Poison condition"],
    "refuse": ["Rations"]
  },
  {
    "name": "Access to Ancient Lore",
    "skills": ["Investigation", "Arcana", "History"],
    "success": ["Easy Quest", "Coin"],
    "failure": ["Hard Quest", "Rations"],
    "refuse": ["None"]
  },
  {
    "name": "Navigating Social Intrigue",
    "skills": ["Persuasion", "Deception", "Insight"],
    "success": ["Coin", "Information", "Ally"],
    "failure": ["Enemy", "Reputation loss"],
    "refuse": ["Coin"]
  }
]
```

## XP Integration
- Use existing XP system from encounter_generator.py
- Success: Full XP based on challenge difficulty
- Failure: Half XP (learning experience)
- Refusal: No XP awarded

## Testing Strategy

### Unit Tests
- Skill challenge template loading
- DC escalation mechanics
- Success/failure tracking
- Reward application
- Database operations

### Integration Tests
- UI interaction flow
- Character data updates
- Logging system integration
- Save/load functionality

### Test Data
- Create test challenge templates
- Mock character data for various levels
- Test edge cases (all failures, all same skill, etc.)

## Implementation Priority

### Phase 1: Core System
1. Database schema and migration
2. SkillChallengeManager service
3. Basic UI widget
4. Template loading system

### Phase 2: Rewards & Penalties
1. Reward application system
2. Penalty application system
3. Character data integration
4. Logging integration

### Phase 3: UI Polish
1. Improved visual design
2. Animation feedback
3. Better information display
4. Mobile-friendly layout

### Phase 4: Content & Testing
1. 20+ challenge templates
2. Comprehensive testing
3. Performance optimization
4. Documentation

## Technical Considerations

### Performance
- Cache loaded templates
- Efficient database queries
- Minimal UI updates during rolls

### Data Integrity
- Validate skill names against character abilities
- Ensure proper transaction handling
- Handle concurrent access safely

### Extensibility
- Plugin system for custom rewards
- Configurable challenge parameters
- Mod support for additional templates

## File Structure
```
TaleKeeper/
├── services/
│   ├── skill_challenge_manager.py
│   ├── skill_challenge_rewards.py
│   └── skill_challenge_templates.py
├── encounter_pane/
│   ├── skill_challenge_widget.py
│   └── skill_challenge_cards.py
├── database/
│   ├── migrations/
│   │   └── XXX_skill_challenges.sql
│   └── seeds/
│       └── skill_challenge_templates.json
├── test/
│   ├── services/
│   │   ├── test_skill_challenge_manager.py
│   │   └── test_skill_challenge_rewards.py
│   └── encounter_pane/
│       └── test_skill_challenge_widget.py
└── docs/
    └── SKILL_CHALLENGE_IMPLEMENTATION.md
```

This implementation maintains compatibility with existing TaleKeeper systems while adding robust skill challenge functionality that enhances exploration and non-combat encounters.