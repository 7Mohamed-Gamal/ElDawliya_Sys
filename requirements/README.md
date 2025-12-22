# Requirements Files

This directory contains all Python package requirements organized by environment.

## Files

- `base.txt` - Base requirements for all environments
- `development.txt` - Development-specific requirements
- `production.txt` - Production-specific requirements  
- `security.txt` - Security-focused additional requirements
- `python312.txt` - Python 3.12 compatible versions

## Usage

```bash
# Install base requirements
pip install -r requirements/base.txt

# Install development requirements (includes base)
pip install -r requirements/development.txt

# Install production requirements (includes base)
pip install -r requirements/production.txt
```

## Compatibility

The main `requirements.txt` file in the project root is maintained for backward compatibility.