"""
Bridge module to load the monolithic Hr/api/serializers.py file even when a
package named Hr/api/serializers/ exists. This avoids name collisions.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

__all__ = []

# Path to the monolithic serializers.py that defines CompanySerializer, etc.
mono_path = pathlib.Path(__file__).resolve().parent / 'serializers.py'

if mono_path.exists():
    spec = importlib.util.spec_from_file_location('Hr.api._mono_serializers', str(mono_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        # Ensure relative imports inside serializers.py resolve against Hr.api
        mod.__package__ = 'Hr.api'
        # Optionally register in sys.modules so others can import it too
        sys.modules['Hr.api._mono_serializers'] = mod
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        for name in dir(mod):
            if not name.startswith('_'):
                globals()[name] = getattr(mod, name)
                __all__.append(name)

