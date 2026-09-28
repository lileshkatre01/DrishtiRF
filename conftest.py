"""
Root-level pytest conftest.py — adds project root to sys.path so that
'backend' and 'ml_training' packages are importable without installation.
"""
import sys
import os

# Make project root the first entry on the path
sys.path.insert(0, os.path.dirname(__file__))
