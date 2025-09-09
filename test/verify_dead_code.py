#!/usr/bin/env python
"""
Verify dead code assumptions by checking runtime usage.
"""

import ast
import os
import sys
import importlib.util
import inspect
from pathlib import Path

class UsageVerifier:
    def __init__(self):
        self.used_functions = set()
        self.used_classes = set()
        self.import_trace = []
        
    def check_runtime_usage(self):
        """Check if marked dead code is actually used at runtime."""
        
        # Check 1: Import all modules and track what gets loaded
        print("=== IMPORT ANALYSIS ===")
        project_path = Path(__file__).parent
        
        # Try importing main modules
        modules_to_check = [
            'services.dice',
            'services.proficiency_bonus',
            'ui.themes',
            'encounter_pane.web_form'
        ]
        
        for module_name in modules_to_check:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check if specific functions exist and are used
                    if module_name == 'services.dice':
                        funcs = ['attack_roll', 'saving_throw', 'skill_check']
                        for func in funcs:
                            if hasattr(module, func):
                                print(f"  {module_name}.{func}: EXISTS")
                                # Check if it's in __all__
                                if hasattr(module, '__all__') and func in module.__all__:
                                    print(f"    -> Exported in __all__")
                            else:
                                print(f"  {module_name}.{func}: NOT FOUND")
                                
                    elif module_name == 'services.proficiency_bonus':
                        if hasattr(module, 'get_proficiency_bonus_from_character'):
                            print(f"  {module_name}.get_proficiency_bonus_from_character: EXISTS")
                            
                    elif module_name == 'ui.themes':
                        if hasattr(module, 'get_theme_names'):
                            print(f"  {module_name}.get_theme_names: EXISTS")
                            
            except Exception as e:
                print(f"  Error importing {module_name}: {e}")
        
        # Check 2: Search for dynamic usage patterns
        print("\n=== DYNAMIC USAGE PATTERNS ===")
        
        # Check for getattr/eval usage
        patterns = [
            ('getattr', 'Dynamic attribute access'),
            ('eval', 'Dynamic code evaluation'),
            ('exec', 'Dynamic code execution'),
            ('__import__', 'Dynamic import'),
            ('importlib', 'Dynamic module loading')
        ]
        
        for root, dirs, files in os.walk(project_path):
            if '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern, desc in patterns:
                            if pattern in content:
                                # Check if it references our suspect functions
                                if any(func in content for func in ['attack_roll', 'saving_throw', 'skill_check', 'get_proficiency_bonus_from_character', 'get_theme_names']):
                                    print(f"  {os.path.relpath(filepath)}: Uses {desc} (may call marked functions)")
                                    
                    except Exception:
                        pass
        
        # Check 3: Database references
        print("\n=== DATABASE REFERENCES ===")
        
        # Check if functions are referenced in database seeds
        db_files = [
            'database/seeds/001_game_data.sql',
            'database/schema/001_initial_schema.sql'
        ]
        
        for db_file in db_files:
            filepath = project_path / db_file
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'attack_roll' in content or 'saving_throw' in content or 'skill_check' in content:
                    print(f"  {db_file}: Contains references to dice functions")
        
        # Check 4: Test usage
        print("\n=== TEST FILE USAGE ===")
        
        test_files = list(project_path.glob('test*.py')) + list((project_path / 'testing').glob('*.py'))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for func in ['attack_roll', 'saving_throw', 'skill_check', 'get_proficiency_bonus_from_character', 'get_theme_names']:
                    if func in content:
                        print(f"  {test_file.name}: Uses {func}")
                        
            except Exception:
                pass
        
        # Check 5: Duplicate function analysis
        print("\n=== DUPLICATE FUNCTIONS ===")
        
        # Check town_encounter.py for duplicate _get_character_gold
        town_encounter_path = project_path / 'encounter_pane' / 'town_encounter.py'
        if town_encounter_path.exists():
            with open(town_encounter_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count occurrences of the function definition
            count = content.count('def _get_character_gold(self)')
            if count > 1:
                print(f"  town_encounter.py: _get_character_gold defined {count} times (DUPLICATE CONFIRMED)")
                
                # Find line numbers
                lines = content.split('\n')
                occurrences = []
                for i, line in enumerate(lines, 1):
                    if 'def _get_character_gold(self)' in line:
                        occurrences.append(i)
                print(f"    Line numbers: {occurrences}")
                
                # Check which classes they belong to
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name == '_get_character_gold':
                                print(f"    Found in class: {node.name} at line {item.lineno}")

if __name__ == "__main__":
    verifier = UsageVerifier()
    verifier.check_runtime_usage()