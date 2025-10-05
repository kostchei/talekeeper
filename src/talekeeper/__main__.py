import sys
from pathlib import Path

root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))

from main import main

if __name__ == "__main__":
    main()
