"""Put the modules under test on the import path.

pytest adds this directory to sys.path, but the code being tested lives one level
up, so each test file can just `import interfaces` and so on.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
