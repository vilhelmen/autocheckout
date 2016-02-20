#!/usr/bin/env python3

import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_root', required=True,
                                 type=str, help='Path to the submission repository')

    subparse_master = parser.add_subparsers(help='How did this get here I am not so good with computers')

    register_parser = subparse_master.add_parser('register', help='Register students')
    register_parser.add_argument('import_file', reqtured=True,
                                 type=argparse.FileType('r'), help='Student list to register')
    register_parser.add_argument('subdir', type=str, help='Subdirectory to place repositories into')

    collect_parser = subparse_master.add_parser('collect', help='Collect assignment')
    collect_parser.add_argument('tag', required=True, type=str, help='Tag to collect')
    collect_parser.add_argument('--recollect', action='store_true', help='Recollect tag')







