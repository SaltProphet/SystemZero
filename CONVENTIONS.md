# System//Zero Code Conventions

## Naming Standards

### Files
- **Python files**: snake_case (e.g., `tree_normalizer.py`, `drift_event.py`)
- **Module directories**: snake_case (e.g., `core/accessibility/`, `interface/api/`)
- **Test files**: `test_<module>.py` (e.g., `test_drift.py`, `test_normalization.py`)
- **Configuration files**: snake_case or UPPERCASE (e.g., `settings.yaml`, `ROADMAP`)
- **Backup/version files**: **NOT ALLOWED** — use version control instead (removed 5 legacy files)

### Classes
- **Public classes**: PascalCase (e.g., `TreeNormalizer`, `DriftEvent`, `Matcher`)
- **Private classes**: `_PrivateClass` (prefix with underscore)
- **Dataclass models**: PascalCase with descriptive names (e.g., `CaptureRequest`, `TemplateResponse`)

### Functions & Methods
- **Public functions**: snake_case (e.g., `generate_signature()`, `normalize_tree()`)
- **Private functions**: `_private_function()` (prefix with underscore)
- **Async functions**: prefixed with async, still snake_case (e.g., `async_capture()`)
- **Property accessors**: snake_case (e.g., `@property def node_count()`)

### Variables
- **Constants**: UPPERCASE_WITH_UNDERSCORES (e.g., `MAX_DRIFT_THRESHOLD`, `REQUIRED_NODES`)
- **Instance variables**: snake_case (e.g., `self.tree_data`, `self.signatures`)
- **Loop variables**: single letter or snake_case descriptive (e.g., `for i in range()` or `for node_id in nodes`)
- **Local variables**: snake_case (e.g., `matched_template`, `drift_score`)

### Imports
- **Order**: stdlib → third-party → local (PEP 8)
- **Style**: explicit imports preferred over `import *`
- **Organization**: grouped by source, no excessive blank lines

```python
# ✓ CORRECT
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.normalization import TreeNormalizer, SignatureGenerator
from core.drift import Matcher, DriftEvent
```

## Module Structure

### `__init__.py` Exports
Each module must explicitly export its public API via `__all__`:

```python
# core/drift/__init__.py
from .matcher import Matcher
from .diff_engine import DiffEngine
from .drift_event import DriftEvent
from .change import Change
from .transition_checker import TransitionChecker, TransitionResult

__all__ = [
    "Matcher",
    "DiffEngine", 
    "DriftEvent",
    "Change",
    "TransitionChecker",
    "TransitionResult",
]
```

### Import Paths
**Preferred**: `from core.drift import Matcher` (via `__all__` re-exports)  
**Avoid**: `from core.drift.matcher import Matcher` (internal structure)

## Documentation

### Docstrings
- **Style**: Google-style docstrings (3-line minimum)
- **Classes**: Describe purpose and key attributes
- **Functions**: Include Args, Returns, Raises sections
- **Examples**: Provide for complex functions

```python
def generate_signature(tree: Dict[str, Any]) -> str:
    """Generate SHA256 signature for normalized tree.
    
    Args:
        tree: Normalized accessibility tree dictionary
        
    Returns:
        40-character SHA256 hex string
        
    Raises:
        ValueError: If tree structure is invalid
    """
    pass
```

### Comments
- **Inline comments**: Explain *why*, not *what* (code is self-documenting)
- **Block comments**: Summarize complex logic sections
- **TODO/FIXME**: Include with context (e.g., `# TODO: optimize for 1000+ node trees`)

## Code Organization

### File Size Guidelines
- **Modules**: <500 LOC (split large modules)
- **Classes**: <300 LOC (use composition)
- **Methods**: <50 LOC (extract helpers)

### Cyclomatic Complexity
- Target: <10 per function
- Avoid deeply nested conditionals (max 3 levels)
- Use early returns to reduce nesting

### Type Hints
- **Required**: All function parameters and returns
- **Optional types**: Use `Optional[T]` for nullable values
- **Collections**: Use `List[T]`, `Dict[K, V]`, `Tuple[T, ...]`
- **Unions**: Use `Union[A, B]` or `A | B` (Python 3.10+)

```python
def match_template(
    tree: Dict[str, Any],
    templates: List[Dict[str, Any]],
    threshold: float = 0.8
) -> Optional[Tuple[Dict[str, Any], float]]:
    """Match tree against templates."""
    pass
```

## Testing Conventions

### Test File Organization
- **Structure**: Mirror `systemzero/` in `tests/`
- **Naming**: `test_<module>.py` (e.g., `test_drift.py`)
- **Classes**: Group related tests in classes (e.g., `TestMatcher`, `TestDiffEngine`)
- **Methods**: `test_<feature>_<scenario>` (e.g., `test_similarity_score_perfect_match`)

### Test Standards
- **Assertions**: Use descriptive assertion messages
- **Fixtures**: Define in `conftest.py` or `fixtures/` modules
- **Mocking**: Use `unittest.mock` for external dependencies
- **Coverage**: Target >90% (currently at 91.5% for Phase 6)

### Example Test
```python
class TestMatcher:
    def test_similarity_score_perfect_match(self):
        """Should return 1.0 for identical trees."""
        tree1 = {"name": "root", "children": []}
        tree2 = {"name": "root", "children": []}
        
        score = Matcher().similarity_score(tree1, tree2)
        
        assert score == 1.0, "Identical trees must score 1.0"
```

## Error Handling

### Exception Hierarchy
- **Custom exceptions**: Define in `core/utils/exceptions.py`
- **Naming**: `<Feature>Error` or `<Feature>Exception`
- **HTTP endpoints**: Map to appropriate status codes

```python
class TemplateValidationError(ValueError):
    """Raised when template YAML is invalid."""
    pass

class DriftDetectionError(RuntimeError):
    """Raised when drift analysis fails."""
    pass
```

### Exception Usage
- **Raise early**: Validate inputs at function boundaries
- **Provide context**: Include variable values in exception messages
- **Never silently fail**: Log or raise, never pass silently

```python
# ✓ CORRECT
if not template.get("screen_id"):
    raise TemplateValidationError(
        f"Template missing required 'screen_id' field: {template}"
    )

# ✗ WRONG
if not template.get("screen_id"):
    pass  # Silent failure
```

## Git Conventions

### Commit Messages
- **Format**: `<type>(<scope>): <subject>`
- **Types**: feat, fix, docs, style, refactor, test, chore
- **Scope**: affected module (drift, api, logging, etc.)
- **Subject**: imperative mood, <50 chars

```
feat(drift): add deep-nesting support for 1000+ node trees
fix(api): handle rate limit errors in middleware
docs(README): add deployment instructions
```

### Branches
- **Feature**: `feature/<name>` (e.g., `feature/phase7-benchmarks`)
- **Bugfix**: `fix/<issue>` (e.g., `fix/hash-chain-verification`)
- **Main**: `main` (production-ready, always deployable)

## Phase 6 Hygiene Audit Results

### Cleanup Completed
✅ Removed 5 backup/version files from `systemzero/core/drift/`:
- `diff_engine.py.backup` (removed)
- `diff_engine_old.py` (removed)
- `diff_engine_new.py` (removed)
- `drift_event_old.py` (removed)
- `drift_event_new.py` (removed)

### Naming Compliance
✅ All files follow snake_case convention  
✅ All classes use PascalCase  
✅ All functions/methods use snake_case  
✅ All constants use UPPERCASE_WITH_UNDERSCORES  
✅ Module exports properly documented in `__all__`  

### Import Quality
✅ All `__init__.py` files explicitly define exports  
✅ No `from module import *` statements  
✅ Imports follow PEP 8 ordering (stdlib → third-party → local)  

### Test Coverage
✅ 166 tests passing (91.5% code coverage)  
✅ Test naming follows `test_<feature>_<scenario>` convention  
✅ All test classes properly grouped and documented  

## Phase 7 Readiness
- **Code hygiene**: ✅ Clean (no backups, consistent naming)
- **Documentation**: ✅ Comprehensive (docstrings, READMEs, inline comments)
- **Testing**: ✅ Comprehensive (91.5% coverage, 166 tests)
- **Security**: ✅ Audited (auth, rate limiting, input validation)
- **Dependencies**: ✅ Vetted (see SECURITY.md for details)

---
**Last Updated**: Phase 6.6 (Jan 2025)  
**Maintainers**: SaltProphet  
**Status**: Ready for Phase 7 development
