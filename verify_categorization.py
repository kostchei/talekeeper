# unsure
#utility
import subprocess
import os

def run_grep_count(pattern, description):
    try:
        result = subprocess.run(
            ['grep', '-r', pattern, '--include=*.py', '.'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        count = len([line for line in result.stdout.split('\n') if line.strip()])
        print(f"{description:40} {count:5} files")
        return count
    except Exception as e:
        print(f"Error with {description}: {e}")
        return 0

def count_files(pattern, description):
    try:
        result = subprocess.run(
            ['find', '.', '-name', pattern, '-type', 'f'],
            capture_output=True,
            text=True
        )
        count = len([line for line in result.stdout.split('\n') if line.strip()])
        print(f"{description:40} {count:5} files")
        return count
    except:
        return 0

print("=" * 80)
print("TALEKEEPER CATEGORIZATION VERIFICATION")
print("=" * 80)
print()

print("CATEGORY COUNTS (by marker)")
print("-" * 80)

core_count = run_grep_count('^# category: core', 'Core files (# category: core)')
test_count = run_grep_count('^#test', 'Test files (#test)')
utility1 = run_grep_count('^#utility', 'Utility files (#utility)')
utility2 = run_grep_count('^# category: utility', 'Utility files (# category: utility)')
redundant_count = run_grep_count('^#redundant', 'Redundant files (#redundant)')
unsure_count = run_grep_count('^#unsure', 'Unsure files (#unsure)')

print()
print("TOTALS")
print("-" * 80)
total_python = count_files('*.py', 'Total Python files')
total_sql = count_files('*.sql', 'Total SQL files')

print()
print("CATEGORIZATION SUMMARY")
print("-" * 80)
categorized = core_count + test_count + utility1 + utility2 + redundant_count + unsure_count
print(f"Total categorized: {categorized}")
print(f"Total Python files: {total_python}")
print(f"Uncategorized: {total_python - categorized}")

print()
print("BREAKDOWN BY CATEGORY")
print("-" * 80)
print(f"Core:       {core_count:5} files (critical application files)")
print(f"Test:       {test_count:5} files (test suite)")
print(f"Utility:    {utility1 + utility2:5} files (scripts and tools)")
print(f"Redundant:  {redundant_count:5} files (legacy/duplicate code)")
print(f"Unsure:     {unsure_count:5} files (needs review)")

print()
print("=" * 80)
print("VERIFICATION COMMANDS")
print("=" * 80)
print()
print("Find all test files:")
print('  grep -r "^#test" --include="*.py" .')
print()
print("Find all core files:")
print('  grep -r "^# category: core" --include="*.py" .')
print()
print("Find all redundant files:")
print('  grep -r "^#redundant" --include="*.py" .')
print()
print("Find all utility files:")
print('  grep -r "^#utility\\|^# category: utility" --include="*.py" .')
print()
