"""
Ephemeris file validation utilities.

Provides functions to validate Swiss Ephemeris data file presence and integrity.
"""

import os
from pathlib import Path
from typing import List, Tuple

from .exceptions import EphemerisFileNotFoundError


def validate_ephemeris_path(path: str) -> Tuple[bool, List[str]]:
    """
    Validate that ephemeris path exists and contains expected files.

    Args:
        path: Path to check

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors: List[str] = []
    
    if not path:
        errors.append("Path is empty")
        return False, errors
    
    if not os.path.exists(path):
        errors.append(f"Path does not exist: {path}")
        return False, errors
    
    if not os.path.isdir(path):
        errors.append(f"Path is not a directory: {path}")
        return False, errors
    
    # Check for .se1 files (Swiss Ephemeris data files)
    se1_files = [f for f in os.listdir(path) if f.endswith('.se1')]
    if not se1_files:
        errors.append(f"No .se1 files found in: {path}")
        return False, errors
    
    return True, []


def validate_ephemeris_files(path: str, required_files: List[str] = None) -> Tuple[bool, List[str]]:
    """
    Validate that required ephemeris files are present.

    Args:
        path: Path to ephemeris directory
        required_files: Optional list of required file names.
                       If None, checks for at least one .se1 file.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors: List[str] = []
    
    # First validate path exists
    is_valid, path_errors = validate_ephemeris_path(path)
    if not is_valid:
        return False, path_errors
    
    if required_files is None:
        # Just check for at least one .se1 file
        se1_files = [f for f in os.listdir(path) if f.endswith('.se1')]
        if not se1_files:
            errors.append(f"No .se1 files found in: {path}")
        return len(errors) == 0, errors
    
    # Check for specific required files
    missing_files = []
    for filename in required_files:
        filepath = os.path.join(path, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
    
    if missing_files:
        errors.append(f"Missing required files: {', '.join(missing_files)}")
        errors.append(f"Expected in: {path}")
    
    return len(errors) == 0, errors


def check_file_integrity(filepath: str) -> Tuple[bool, List[str]]:
    """
    Perform basic integrity checks on an ephemeris file.

    Args:
        filepath: Path to file to check

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors: List[str] = []
    
    if not os.path.exists(filepath):
        errors.append(f"File does not exist: {filepath}")
        return False, errors
    
    if not os.path.isfile(filepath):
        errors.append(f"Path is not a file: {filepath}")
        return False, errors
    
    # Check file size (Swiss Ephemeris files are typically > 1MB)
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        errors.append(f"File is empty: {filepath}")
    elif file_size < 1024:  # Less than 1KB is suspicious
        errors.append(f"File is unusually small ({file_size} bytes): {filepath}")
    
    return len(errors) == 0, errors


def find_ephemeris_files(path: str) -> List[str]:
    """
    Find all Swiss Ephemeris data files in a directory.

    Args:
        path: Path to search

    Returns:
        List of file paths
    """
    if not os.path.exists(path) or not os.path.isdir(path):
        return []
    
    se1_files = []
    for filename in os.listdir(path):
        if filename.endswith('.se1'):
            filepath = os.path.join(path, filename)
            if os.path.isfile(filepath):
                se1_files.append(filepath)
    
    return sorted(se1_files)

