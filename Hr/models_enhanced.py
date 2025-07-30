# Temporary stub file to prevent import errors
# The actual models are now in the Hr.models package

# Import the actual models from the main models package
from .models import *

# For backward compatibility, create aliases for any models that might be imported
# This prevents ImportError while we transition to the new structure
