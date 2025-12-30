#!/usr/bin/env python
"""Simple test to check imports"""
import sys
import traceback

try:
    print("Testing imports...")
    from app.web import app
    print("✓ Import successful!")
except Exception as e:
    print(f"✗ Import failed!")
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)
