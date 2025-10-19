# core
#utility
#!/usr/bin/env python3
# core
"""
Utility to manage subclass filtering configuration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import config

def show_current_config():
    """Display current subclass filtering configuration"""
    print("Current Subclass Filtering Configuration:")
    print(f"  Filtering enabled: {config.features.release_subclass_filter}")
    print(f"  Release subclasses:")

    for class_name, subclasses in config.features.release_subclasses.items():
        if subclasses:
            print(f"    {class_name}: {subclasses}")
        else:
            print(f"    {class_name}: [none - class hidden]")

def enable_filtering():
    """Enable subclass filtering"""
    config.features.release_subclass_filter = True
    config.save_config()
    print("Subclass filtering enabled.")

def disable_filtering():
    """Disable subclass filtering"""
    config.features.release_subclass_filter = False
    config.save_config()
    print("Subclass filtering disabled - all subclasses will be shown.")

def add_subclass(class_name: str, subclass_name: str):
    """Add a subclass to the release list"""
    class_lower = class_name.lower()
    if class_lower not in config.features.release_subclasses:
        config.features.release_subclasses[class_lower] = []

    if subclass_name not in config.features.release_subclasses[class_lower]:
        config.features.release_subclasses[class_lower].append(subclass_name)
        config.save_config()
        print(f"Added {subclass_name} to {class_name} release subclasses.")
    else:
        print(f"{subclass_name} is already in {class_name} release subclasses.")

def remove_subclass(class_name: str, subclass_name: str):
    """Remove a subclass from the release list"""
    class_lower = class_name.lower()
    if class_lower in config.features.release_subclasses:
        if subclass_name in config.features.release_subclasses[class_lower]:
            config.features.release_subclasses[class_lower].remove(subclass_name)
            config.save_config()
            print(f"Removed {subclass_name} from {class_name} release subclasses.")
        else:
            print(f"{subclass_name} is not in {class_name} release subclasses.")
    else:
        print(f"{class_name} not found in release subclasses config.")

def main():
    """Main function to handle command-line arguments"""
    if len(sys.argv) < 2:
        print("Subclass Filter Management Utility")
        print("Usage:")
        print("  python manage_subclass_filter.py show")
        print("  python manage_subclass_filter.py enable")
        print("  python manage_subclass_filter.py disable")
        print("  python manage_subclass_filter.py add <class> <subclass>")
        print("  python manage_subclass_filter.py remove <class> <subclass>")
        print("")
        print("Examples:")
        print("  python manage_subclass_filter.py add paladin devotion")
        print("  python manage_subclass_filter.py remove fighter battle_master")
        return

    command = sys.argv[1].lower()

    if command == "show":
        show_current_config()
    elif command == "enable":
        enable_filtering()
    elif command == "disable":
        disable_filtering()
    elif command == "add":
        if len(sys.argv) != 4:
            print("Usage: python manage_subclass_filter.py add <class> <subclass>")
            return
        add_subclass(sys.argv[2], sys.argv[3])
    elif command == "remove":
        if len(sys.argv) != 4:
            print("Usage: python manage_subclass_filter.py remove <class> <subclass>")
            return
        remove_subclass(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: show, enable, disable, add, remove")

if __name__ == "__main__":
    main()