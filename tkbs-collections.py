# This script provides helpful utilities for handling Transcribus Collections

import argparse
import json
from TkbsApiClient import TranskribusClient
from utilities import add_transkribus_auth_args, init_tkbs_connection

def get_args():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command')
    p_create = sub.add_parser('create', help='Create a new collection')
    p_create.add_argument('name', help='New collection name')
    p_delete = sub.add_parser('delete', help='Delete a collection')
    p_delete.add_argument('id', type=int, help='Collection ID')
    p_list = sub.add_parser('list', help='List documents in collection')
    p_list.add_argument('id', type=int, help='Collection ID')
    add_transkribus_auth_args(parser)
    return parser.parse_args()

def create_collection(tkbs: TranskribusClient, args: argparse.Namespace):
    result = tkbs.createCollection(args.name)
    print(f'Created collectin {args.name} with id {result}')

def list_collection(tkbs: TranskribusClient, args: argparse.Namespace):
    result = tkbs.listDocsByCollectionId(args.id)
    print(json.dumps(result, indent=4))

def delete_collection(tkbs: TranskribusClient, args: argparse.Namespace):
    result = tkbs.deleteCollection(args.id)
    print(f'Deleted collectin {args.id}')

def main():
    args = get_args()
    tkbs = init_tkbs_connection(args)

    if args.command=='create':
        create_collection(tkbs, args)
    elif args.command=='delete':
        delete_collection(tkbs, args)
    elif args.command=='list':
        list_collection(tkbs, args)
    else:
        raise ValueError(f'Invalid command {args.command}')
    

if __name__=='__main__':
    main()