import sys
import os

print("Python Path:")
for path in sys.path:
    print(f"  {path}")
    
print("\nLooking for core module:")
for path in sys.path:
    potential_core = os.path.join(path, 'core')
    if os.path.exists(potential_core):
        print(f"Found core module at: {potential_core}")
        print("Contents:")
        for root, dirs, files in os.walk(potential_core):
            level = root.replace(potential_core, '').count(os.sep)
            indent = ' ' * 4 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print(f"{subindent}{f}")
