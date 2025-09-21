# TaleKeeper Optimization Report

## Database Query Optimization

### 1. SELECT * Queries Found
- **condition_manager.py:325**: `SELECT * FROM character_conditions` - Should specify needed columns
- **feat_effects.py:43**: `SELECT * FROM feats` - Loading all feats, could be filtered by character
- **equipment.py:24/117**: Equipment queries using SELECT * - Could optimize for specific use cases

### 2. Optimization Recommendations
```sql
-- Instead of: SELECT * FROM character_conditions WHERE character_id = ?
-- Use: SELECT condition_type, source, duration_type, duration_remaining FROM character_conditions WHERE character_id = ?

-- Instead of: SELECT * FROM feats
-- Use: SELECT id, name, description, prerequisites FROM feats WHERE character_meets_prerequisites = 1

-- Equipment queries could include indexes on item_type and name columns
```

## Code Duplication Analysis

### 1. Subclass Manager Duplication
- **SubclassManager** (services/subclass_manager.py) - Legacy system
- **EnhancedSubclassManager** (services/enhanced_subclass_manager.py) - New system
- **Recommendation**: Consolidate into single system, maintain backward compatibility

### 2. Rage Implementation Duplication
Found rage-related functions in multiple files:
- `services/barbarian_abilities.py` - Core implementation
- `action_cards/action_panel.py` - UI integration
- `core/class_features.py` - Class feature definition
- `services/enhanced_subclass_manager.py` - Subclass integration

**Recommendation**: Centralize rage logic in BarbarianAbilitiesService, use dependency injection

### 3. Condition System Integration
Multiple files implement condition checking:
- `services/condition_manager.py` - Core system
- `services/condition_stat_service.py` - Stat calculations
- Various UI panels duplicate condition display logic

## Performance Improvements

### 1. Database Connection Pooling
Current: Each service creates its own connection
Recommended: Implement connection pooling or singleton database manager

### 2. Caching Opportunities
- Character features loaded multiple times per combat round
- Subclass definitions re-parsed on each access
- Condition effects calculated repeatedly

### 3. UI Responsiveness
- Action card generation happens synchronously
- Monster turn processing blocks UI
- Large character sheets cause layout recalculation

## Memory Usage Optimization

### 1. Lazy Loading
- Load subclass features only when needed
- Cache frequently accessed character data
- Unload unused monster data after encounters

### 2. Object Lifecycle
- Condition objects created unnecessarily in validation
- Combat state objects persist beyond combat end
- Action cards recreated on every UI update

## Implementation Priority

### High Priority
1. **Database Query Optimization** - Immediate performance gains
2. **Subclass Manager Consolidation** - Reduces maintenance burden
3. **Action Card Caching** - Improves UI responsiveness

### Medium Priority
1. **Rage Logic Centralization** - Code quality improvement
2. **Connection Pooling** - Moderate performance gain
3. **Combat State Cleanup** - Memory usage improvement

### Low Priority
1. **Condition Display Consolidation** - UI consistency
2. **Monster Data Lifecycle** - Minor memory savings
3. **Feature Loading Optimization** - Edge case performance

## Configuration Options Needed

### 1. Performance Settings
```python
PERFORMANCE_CONFIG = {
    "enable_action_card_caching": True,
    "condition_cache_size": 100,
    "database_connection_pool_size": 5,
    "ui_update_throttle_ms": 16  # 60fps max
}
```

### 2. Debug Options
```python
DEBUG_CONFIG = {
    "log_database_queries": False,
    "show_performance_metrics": False,
    "trace_condition_applications": False,
    "validate_action_economy": True
}
```

### 3. Feature Toggles
```python
FEATURE_CONFIG = {
    "use_enhanced_subclass_manager": True,
    "enable_condition_immunity_optimization": True,
    "use_cached_monster_data": True,
    "parallel_combat_processing": False
}
```

## Debug Commands Recommendations

### 1. Performance Analysis
- `/debug performance` - Show timing metrics
- `/debug memory` - Display memory usage
- `/debug queries` - Log database queries
- `/debug cache` - Show cache hit/miss ratios

### 2. System State
- `/debug conditions <character>` - Show all active conditions
- `/debug economy <character>` - Display action economy state
- `/debug features <character>` - List available features
- `/debug combat` - Show combat state

### 3. Testing Utilities
- `/test rage <character>` - Test rage mechanics
- `/test conditions <character>` - Apply test conditions
- `/test economy reset` - Reset action economy
- `/test features reload` - Reload character features

## Next Steps

1. **Implement database query optimization** (Stage 4.2)
2. **Add performance monitoring tools** (Stage 4.2)
3. **Create configuration system** (Stage 4.2)
4. **Implement debug commands** (Stage 4.2)
5. **Consolidate duplicate systems** (Stage 4.2)
6. **Update documentation** (Stage 4.3)
7. **Create release notes** (Stage 4.3)