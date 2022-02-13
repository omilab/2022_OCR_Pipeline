# This module contains various utilities for the pipeline stages.

# Enumerates all daily folders, yielding each folder.
# All paths are relative to base_dir
import argparse
from enum import Enum
import logging
from typing import Any, Generator
import os

def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('base', help="Base Directory to Process")
    parser.add_argument('--log_file', default='pipeline.log', help='Log file for detailed output')
    parser.add_argument('--verbose', action='store_true', default=False, help='Write more information to the logfile')
    parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite existing data if data has already been processed before')

    return parser

def setup_logging(args: Any):
    logging.basicConfig(filename=args.log_file, filemode="w", level=logging.DEBUG if args.verbose else logging.INFO)
