# Bridge package to expose classes from the monolithic serializers.py file.
# This avoids the package/module name collision by loading the file directly.
from __future__ import annotations

import importlib.util
import pathlib

__all__ = []  # will be populated from the monolithic module if present

try:
    base_dir = pathlib.Path(__file__).resolve().parent  # Hr/api
    mono_path = base_dir / 'serializers.py'
    if mono_path.exists():
        # Load the monolithic serializers.py as a proper submodule of Hr.api
        spec = importlib.util.spec_from_file_location('Hr.api._serializers_monolithic', str(mono_path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            # Ensure package context for relative imports like "from ..models_enhanced import ..."
            mod.__package__ = 'Hr.api'
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            for name in dir(mod):
                if not name.startswith('_'):
                    globals()[name] = getattr(mod, name)
                    __all__.append(name)
except Exception:
    # Fallback: expose nothing if loading fails
    pass

# Optionally expose analytics serializers if available
try:
    from .analytics_serializers import *  # type: ignore
except Exception:
    pass
