# This module contains various utilities for the pipeline stages.

# Enumerates all daily folders, yielding each folder.
# All paths are relative to base_dir
import argparse
import logging
from typing import Any
import os

from TkbsApiClient import TranskribusClient

def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('base', help="Base Directory to Process")
    parser.add_argument('--log_file', default='pipeline.log', help='Log file for detailed output')
    parser.add_argument('--verbose', action='store_true', default=False, help='Write more information to the logfile')
    parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite existing data if data has already been processed before')

    return parser

def add_transkribus_auth_args(parser: argparse.ArgumentParser):
    parser.add_argument('--tkbs-user', default='omilab.openu@gmail.com', help='Transkribus User name')
    parser.add_argument('--tkbs-password', required=True, help='Transkribus Password')
    parser.add_argument('--tkbs-server', default='https://transkribus.eu/TrpServer')

def add_transkribus_args(parser: argparse.ArgumentParser):
    add_transkribus_auth_args(parser)
    parser.add_argument('--tkbs-collection-id', required=True, help='Transkribust Collection Id for Documents')
    parser.add_argument('--tkbs-htr-model-id', type=int, default=23005, help='Transkribus HTR model for OCR')

def setup_logging(args: Any):
    logging.basicConfig(filename=args.log_file, filemode="w", level=logging.DEBUG if args.verbose else logging.INFO)

def init_tkbs_connection(args: argparse.Namespace):
    tkbs = TranskribusClient(sServerUrl=args.tkbs_server)
    tkbs.auth_login(args.tkbs_user, args.tkbs_password, True)

    return tkbs
