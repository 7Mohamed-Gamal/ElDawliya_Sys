"""
Script to create migrations for the HR app
"""

import os
import sys
import django
import subprocess

def create_migrations():
    """Create migrations for the HR app"""
    print("Creating migrations for the HR app...")
    try:
        # Use subprocess to run the command and capture output
        result = subprocess.run(
            ["python", "manage.py", "makemigrations", "Hr"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print("Migrations created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating migrations: {e}")
        print(e.stdout)
        print(e.stderr)

def apply_migrations():
    """Apply migrations for the HR app"""
    print("Applying migrations for the HR app...")
    try:
        # Use subprocess to run the command and capture output
        result = subprocess.run(
            ["python", "manage.py", "migrate", "Hr"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print("Migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying migrations: {e}")
        print(e.stdout)
        print(e.stderr)

if __name__ == "__main__":
    create_migrations()
    # Uncomment the following line to apply migrations
    # apply_migrations()