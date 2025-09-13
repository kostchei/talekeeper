#!/usr/bin/env python
"""
Dead code and duplication analyzer for TaleKeeper project.
This tool scans the codebase to identify potentially unused code and duplications.
"""

import ast
import os
import re
from collections import defaultdict
from typing import Set, Dict, List, Tuple
import hashlib

class DeadCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.defined_functions = set()
        self.defined_classes = set()
        self.defined_methods = defaultdict(set)
        self.function_calls = set()
        self.class_references = set()
        self.imports = set()
        self.imported_names = set()
        self.current_class = None
        
    def visit_ClassDef(self, node):
        self.defined_classes.add(node.name)
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node):
        if self.current_class:
            self.defined_methods[self.current_class].add(node.name)
        else:
            self.defined_functions.add(node.name)
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        if self.current_class:
            self.defined_methods[self.current_class].add(node.name)
        else:
            self.defined_functions.add(node.name)
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.function_calls.add(node.func.attr)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.class_references.add(node.id)
        self.generic_visit(node)
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
            self.imported_names.add(alias.asname if alias.asname else alias.name)
            
    def visit_ImportFrom(self, node):
        module = node.module or ''
        for alias in node.names:
            self.imports.add(f"{module}.{alias.name}")
            self.imported_names.add(alias.asname if alias.asname else alias.name)

class DuplicationDetector:
    def __init__(self):
        self.code_blocks = defaultdict(list)
        self.duplicate_threshold = 5  # minimum lines for duplication
        
    def extract_code_blocks(self, content: str, filepath: str):
        """Extract meaningful code blocks for duplication detection."""
        lines = content.split('\n')
        
        # Extract function/method bodies
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
                
                if end_line - start_line >= self.duplicate_threshold:
                    block_lines = lines[start_line:end_line]
                    block_text = '\n'.join(block_lines)
                    
                    # Normalize whitespace and remove comments for comparison
                    normalized = self._normalize_code(block_text)
                    if len(normalized.split('\n')) >= self.duplicate_threshold:
                        block_hash = hashlib.md5(normalized.encode()).hexdigest()
                        self.code_blocks[block_hash].append({
                            'file': filepath,
                            'name': node.name,
                            'start_line': start_line + 1,
                            'end_line': end_line,
                            'code': block_text[:200]  # First 200 chars for preview
                        })
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison."""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Normalize whitespace
        lines = []
        for line in code.split('\n'):
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
        
        return '\n'.join(lines)
    
    def find_duplicates(self) -> Dict[str, List]:
        """Find duplicate code blocks."""
        duplicates = {}
        for block_hash, locations in self.code_blocks.items():
            if len(locations) > 1:
                duplicates[block_hash] = locations
        return duplicates

def analyze_project(project_path: str):
    """Analyze the entire project for dead code and duplications."""
    
    # Collect all Python files
    python_files = []
    for root, dirs, files in os.walk(project_path):
        # Skip test files and __pycache__
        if '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                python_files.append(filepath)
    
    # Analyze each file
    all_analyzers = {}
    duplication_detector = DuplicationDetector()
    file_contents = {}
    
    print(f"Analyzing {len(python_files)} Python files...")
    
    for filepath in python_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                file_contents[filepath] = content
                
            tree = ast.parse(content)
            analyzer = DeadCodeAnalyzer()
            analyzer.visit(tree)
            all_analyzers[filepath] = analyzer
            
            # Check for duplications
            duplication_detector.extract_code_blocks(content, filepath)
            
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
    
    # Aggregate results across all files
    all_defined_functions = set()
    all_defined_classes = set()
    all_function_calls = set()
    all_class_references = set()
    all_imports = set()
    
    for filepath, analyzer in all_analyzers.items():
        all_defined_functions.update(analyzer.defined_functions)
        all_defined_classes.update(analyzer.defined_classes)
        all_function_calls.update(analyzer.function_calls)
        all_class_references.update(analyzer.class_references)
        all_imports.update(analyzer.imports)
    
    # Find potentially unused code
    unused_functions = all_defined_functions - all_function_calls
    unused_classes = all_defined_classes - all_class_references
    
    # Filter out special methods and test files
    special_methods = {'__init__', '__str__', '__repr__', '__eq__', '__hash__', 
                      '__lt__', '__le__', '__gt__', '__ge__', '__enter__', '__exit__',
                      'setUp', 'tearDown', 'setUpClass', 'tearDownClass'}
    
    unused_functions = {f for f in unused_functions if not f.startswith('_') or f in special_methods}
    
    # Find test files and standalone scripts that might have "unused" main functions
    test_files = [f for f in python_files if 'test' in os.path.basename(f).lower() or 
                  f.endswith(('create_fighter_test_characters.py', 'create_one_fighter.py',
                           'fix_fighter_action_surge.py', 'update_fighter_resources.py',
                           'setup_equipment_choices.py'))]
    
    # Generate report
    report = []
    report.append("=" * 80)
    report.append("DEAD CODE AND DUPLICATION ANALYSIS REPORT")
    report.append("=" * 80)
    
    # Report potentially unused functions
    report.append("\n### POTENTIALLY UNUSED FUNCTIONS ###")
    for filepath, analyzer in all_analyzers.items():
        file_unused = analyzer.defined_functions & unused_functions
        if file_unused and filepath not in test_files:
            report.append(f"\n{filepath}:")
            for func in sorted(file_unused):
                # Find line number
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if f"def {func}(" in line:
                            report.append(f"  - {func} (line {i})")
                            break
    
    # Report potentially unused classes
    report.append("\n### POTENTIALLY UNUSED CLASSES ###")
    for filepath, analyzer in all_analyzers.items():
        file_unused = analyzer.defined_classes & unused_classes
        if file_unused and filepath not in test_files:
            report.append(f"\n{filepath}:")
            for cls in sorted(file_unused):
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if f"class {cls}" in line:
                            report.append(f"  - {cls} (line {i})")
                            break
    
    # Report duplications
    duplicates = duplication_detector.find_duplicates()
    if duplicates:
        report.append("\n### DUPLICATE CODE BLOCKS ###")
        for i, (block_hash, locations) in enumerate(duplicates.items(), 1):
            report.append(f"\nDuplication #{i}:")
            for loc in locations:
                report.append(f"  - {loc['file']}:{loc['start_line']}-{loc['end_line']} ({loc['name']})")
            report.append(f"  Preview: {locations[0]['code'][:100]}...")
    
    # Check for duplicate imports
    report.append("\n### REDUNDANT IMPORTS ###")
    import_count = defaultdict(list)
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith(('import ', 'from ')):
                        import_count[line.strip()].append((filepath, i))
        except:
            pass
    
    for import_line, locations in import_count.items():
        if len(locations) > 5:  # Same import in more than 5 files
            report.append(f"\n'{import_line}' imported in {len(locations)} files")
    
    return '\n'.join(report), all_analyzers, file_contents

def mark_dead_code(report: str, analyzers: dict, file_contents: dict):
    """Mark suspected dead code with comments for testing."""
    
    # Parse the report to identify dead code locations
    dead_functions = defaultdict(list)
    dead_classes = defaultdict(list)
    
    lines = report.split('\n')
    current_file = None
    in_unused_functions = False
    in_unused_classes = False
    
    for line in lines:
        if "POTENTIALLY UNUSED FUNCTIONS" in line:
            in_unused_functions = True
            in_unused_classes = False
        elif "POTENTIALLY UNUSED CLASSES" in line:
            in_unused_functions = False
            in_unused_classes = True
        elif "DUPLICATE CODE BLOCKS" in line or "REDUNDANT IMPORTS" in line:
            in_unused_functions = False
            in_unused_classes = False
        elif line.endswith('.py:'):
            current_file = line.strip().rstrip(':')
        elif line.strip().startswith('- ') and current_file:
            match = re.match(r'- (\w+) \(line (\d+)\)', line.strip())
            if match:
                name, line_num = match.groups()
                if in_unused_functions:
                    dead_functions[current_file].append((name, int(line_num)))
                elif in_unused_classes:
                    dead_classes[current_file].append((name, int(line_num)))
    
    # Create modified versions with comments
    modified_files = {}
    
    for filepath in dead_functions.keys() | dead_classes.keys():
        if filepath not in file_contents:
            continue
            
        lines = file_contents[filepath].split('\n')
        
        # Mark dead functions
        for func_name, line_num in dead_functions.get(filepath, []):
            if 0 < line_num <= len(lines):
                # Add comment before the function
                indent = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
                comment = ' ' * indent + f"# POTENTIAL_DEAD_CODE: Function '{func_name}' appears unused"
                lines.insert(line_num - 1, comment)
        
        # Mark dead classes  
        for class_name, line_num in dead_classes.get(filepath, []):
            if 0 < line_num <= len(lines):
                # Add comment before the class
                indent = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
                comment = ' ' * indent + f"# POTENTIAL_DEAD_CODE: Class '{class_name}' appears unused"
                lines.insert(line_num - 1, comment)
        
        modified_files[filepath] = '\n'.join(lines)
    
    return modified_files

if __name__ == "__main__":
    import sys
    
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    print("Starting dead code analysis...")
    report, analyzers, file_contents = analyze_project(project_path)
    
    # Save report
    with open('dead_code_report.txt', 'w') as f:
        f.write(report)
    
    print("\nReport saved to dead_code_report.txt")
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    
    # Print summary
    lines = report.split('\n')
    for line in lines[:50]:  # First 50 lines for summary
        print(line)
    
    if '--mark' in sys.argv:
        print("\nMarking dead code with comments...")
        modified_files = mark_dead_code(report, analyzers, file_contents)
        
        for filepath, content in modified_files.items():
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"Marked {len(modified_files)} files with POTENTIAL_DEAD_CODE comments")
        print("Run the application and tests to verify if the code is truly dead")