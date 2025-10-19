# test
import os
import glob

def add_category_to_test_files():
    test_files = glob.glob('tests/**/*.py', recursive=True)
    count = 0

    for filepath in test_files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if already has category comment
        if content.startswith('# category:') or content.startswith('#test'):
            print(f"Already categorized: {filepath}")
            continue

        # Add test category comment at the top
        new_content = f"#test\n{content}"

        with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(new_content)

        print(f"Added 'test' to {filepath}")
        count += 1

    print(f"\nTotal test files categorized: {count}")

if __name__ == '__main__':
    add_category_to_test_files()
