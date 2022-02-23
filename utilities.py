# This module contains various utilities for the pipeline stages.

# Enumerates all daily folders, yielding each folder.
# All paths are relative to base_dir
import argparse
import glob
import json
import logging
from typing import Any
import os

from TkbsApiClient import TranskribusClient
from TkbsDocument import Document

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

def save_job_indication(folder: str, job_id: int):
    job_dict = {'job': job_id}
    with open(os.path.join(folder, 'job-status.json'), 'w') as fp:
        json.dump(job_dict, fp)


# class JobStatus:
#     # This is a more elaborate class for tracking job statuses. We'll make it work and use it only if the pipeline is
#     # going to work after we finish the current 9 newspapers. No point in investing time if we only run the 9 papers through the pipeline
#     filename: str
#     id: int
#     status: str
#     error: str | None

#     def __init__(self, folder: str, type: str):
#         folder = os.path.join(folder, 'jobs')
#         os.makedirs(folder, exist_ok=True)
#         self.filename = os.path.join(folder, f'job-{type}.json')

#     @staticmethod
#     def create_new(folder: str, type: str, id: int):
#         job = JobStatus(folder, type)
#         job.id = id
#         job.status = 'NEW'
#         job.save()

#     @staticmethod
#     def load(folder: str, type: str):
#         job = JobStatus(folder, type)
#         with open(job.filename, 'r') as fp:
#             d = json.load(fp)

#         job.id = d['id']
#         job.status = d.get('status', 'NEW')

#     def save(self):
#         d = dict(id=self.id, status=self.status, error=self.error)
#         with open(self.filename, 'w') as fp:
#             json.dump(d, fp, indent=4)

#     def fetch_status(self, tkbs: TranskribusClient):
#         response = tkbs.getJobStatus(self. id)
#         self.status = response['status']
#         if self.status == 'FINISHED' and not response['success']:
#             self.error = 'Error in job!'
#             print(response)
#         self.save()


# Gather all documents, returning a list of (base_dir, folder)
def gather_document_folders(base: str):
    folders = glob.glob(os.path.join(base, '**', 'legacy_output'), recursive=True)
    folders = [os.path.dirname(f) for f in folders]

    for folder in folders:
        yield folder

def load_document(folder: str):
    doc = Document()
    doc.load_legacy_data(folder)

    return doc