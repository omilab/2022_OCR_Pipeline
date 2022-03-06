# Check status of all pending jobs

import argparse
import glob
import json
import os
from typing import Any

from tqdm import tqdm

from utilities import add_transkribus_auth_args, init_tkbs_connection


def get_args() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument('base', help='Base directory')
    add_transkribus_auth_args(parser)
    args = parser.parse_args()

    return args

def main():
    args = get_args()
    tkbs = init_tkbs_connection(args)

    job_files = glob.glob(os.path.join(args.base, '**', 'job-status.json'), recursive=True)
    running = finished = 0
    errors = []

    for job_file in tqdm(job_files):
        with open(job_file, 'r') as fp:
            job_info = json.load(fp)
        job_id = job_info['job']
        job = tkbs.getJobStatus(job_id)
        
        status = job['state']
        if status in ('RUNNING', 'CREATED'):
            running += 1
        elif status == 'FINISHED':
            if not job['success']:
                errors.append(job)
            else:
                finished += 1
                os.remove(job_file)
        elif status == 'FAILED':
            errors.append(job)
        else:
            print(job)

    print(f'Running jobs {running}, finished jobs {finished}, jobs with errors {len(errors)}')
    print('Errors are:')
    for error in errors:
        print(f"Job {error['jobId']}: {error['description']}")
        print()
        
if __name__ == '__main__':
    main()