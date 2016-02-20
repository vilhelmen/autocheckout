#!/usr/bin/env python3

import argparse


def register_students(vars):
    return


def collect_assignment(vars):
    return


def parse_args():
    parser = argparse.ArgumentParser()

    subparse_master = parser.add_subparsers(title='Commands')

    register_parser = subparse_master.add_parser('register', help='Register students')
    register_parser.add_argument('repo_root', type=str, help='Path to the submission repository')
    register_parser.add_argument('import_file', type=argparse.FileType('r'), help='Student list to register')
    register_parser.add_argument('--subdir', type=str, help='Subdirectory to place repositories into')
    register_parser.set_defaults(func=register_students)

    collect_parser = subparse_master.add_parser('collect', help='Collect assignment')
    collect_parser.add_argument('repo_root', type=str, help='Path to the submission repository')
    collect_parser.add_argument('tag', type=str, help='Tag to collect')
    collect_parser.add_argument('--recollect', action='store_true', help='Recollect tag')
    collect_parser.set_defaults(func=collect_assignment)

    args = parser.parse_args()

    if not vars(args):
        parser.print_help()
        parser.exit(1)

    print(args)

if __name__ == '__main__':
    parse_args()







