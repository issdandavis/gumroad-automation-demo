#!/usr/bin/env python3
"""
Self-Evolving AI Framework - Commercial Package Creator
======================================================

Creates distribution packages for different license tiers.
Generates ZIP files ready for Gumroad distribution.

Usage:
    python create_commercial_packages.py --all
    python create_commercial_packages.py --tier starter
    python create_commercial_packages.py --tier professional
    python create_commercial_packages.py --tier enterprise
"""

import argparse
import json
import os
import shutil
import zipfile
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommercialPackageCreator:
    """Creates commercial packages for different license tiers"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.packages_dir = self.project_root / "COMMERCIAL_PACKAGES"
        self.version = "3.0.0"
        self.build_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure packages directory exists
        self.packages_dir.mkdir(exist_ok=True)
        
        # Define tier configurations
        self.tier_configs = {
            'starter': {
                'price': 297,
                'name': 'Starter Edition',
                'description': 'Perfect for individual developers',
                'features': [
                    'Full source code with commercial license',
                    'Basic AI provider integrations',
                    'Community support',
                    'Documentation and tutorials'
                ],
                'include_enterprise_features': False,
                'include_aws_bedrock': False,
                'include_advanced_monitoring': False,
                'max_developers': 1
            },
            'professional': {
                'price': 997,
                'name': 'Professional Edition',
                'description': 'Ideal for teams and busines