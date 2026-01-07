#!/usr/bin/env python3
"""Run the desktop chess application with API integration."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desktop_client.main_api import main

if __name__ == '__main__':
    main()