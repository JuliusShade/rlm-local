# Troubleshooting Fixes Applied

## Issues Fixed

### 1. ModuleNotFoundError: No module named 'src'

**Error Message**:
```
Traceback (most recent call last):
  File "examples\simple_query.py", line 9, in <module>
    from src.rlm import RLMController
ModuleNotFoundError: No module named 'src'
```

**Root Cause**:
The example files had incorrect path setup: `sys.path.insert(0, "../src")`

When you want to import `from src.rlm`, you need to add the **project root** (not the `src` directory) to the Python path.

**Fix Applied**:
Changed all example files to use proper path resolution:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rlm import RLMController
```

**Files Updated**:
- `examples/simple_query.py`
- `examples/complex_analysis.py`
- `examples/code_refactoring.py`
- `test_basic.py`

---

### 2. Windows Unicode Encoding Errors

**Error Message**:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u25b6' in position 9: character maps to <undefined>
```

**Root Cause**:
Windows terminals use cp1252 encoding by default, which doesn't support Unicode symbols like:
- `▶` (U+25B6) - used for stage markers
- `✓` (U+2713) - used for checkmarks
- `├─` (U+251C, U+2500) - used for tree branches
- `→` (U+2192) - used for arrows

**Fix Applied**:
Updated logging to use ASCII-safe symbols on Windows:

| Unicode | Windows ASCII | Purpose |
|---------|--------------|---------|
| `▶` | `>` | Stage start marker |
| `✓` | `[OK]` | Completion marker |
| `├─` | `+-` | Tree branch |
| `│` | `|` | Tree pipe |
| `→` | `->` | Arrow/direction |

**Files Updated**:
- `src/utils/logging.py` - Updated `stage()` and `recursion_tree()` methods
- `src/rlm/stages/reasoner.py` - Replaced all `→` with `->`

**Implementation**:
```python
# Use ASCII-safe symbols for Windows
if sys.platform == 'win32':
    branch = "+-"
    pipe = "|"
    arrow = "->"
else:
    branch = "├─"
    pipe = "│"
    arrow = "→"
```

---

## How to Run Examples Now

All examples should now work correctly on Windows:

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run any example
python examples/simple_query.py
python examples/complex_analysis.py
python examples/code_refactoring.py

# Or with uv
uv run python examples/simple_query.py
```

---

## Output Differences

### Unix/macOS Output:
```
▶ Planner
✓ Planner complete

├─ [depth 0] [SIMPLE] Question
│  → Answer preview...
```

### Windows Output:
```
> Planner
[OK] Planner complete

+- [depth 0] [SIMPLE] Question
|  -> Answer preview...
```

Both outputs are functionally identical, just using ASCII-safe characters on Windows.

---

## Prevention

These fixes ensure cross-platform compatibility:

1. **Always use `pathlib.Path`** for path resolution
2. **Check `sys.platform`** before using Unicode symbols
3. **Test on Windows** if you use special characters in console output
4. **Use ASCII-safe alternatives** for terminal symbols

---

## Verification

To verify all fixes are working:

```bash
# Run basic tests
python test_basic.py

# All tests should pass:
# [PASS] Client Connection
# [PASS] Simple Completion
# [PASS] Full RLM Pipeline
```

---

## Additional Notes

### Why Not Force UTF-8 on Windows?

We could force UTF-8 encoding with:
```python
sys.stdout.reconfigure(encoding='utf-8')
```

However, this:
- Doesn't work on older Python versions
- May cause issues with some terminals
- Requires chcp 65001 in cmd.exe

**Using ASCII-safe symbols is more reliable** across all Windows configurations.

### Performance Impact

Zero performance impact - the platform check `sys.platform == 'win32'` is done once during logger initialization.

---

All issues are now resolved and the RLM system runs smoothly on Windows! 🎉
