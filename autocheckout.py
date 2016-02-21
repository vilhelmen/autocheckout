#!/usr/bin/env python3

import argparse
from git import *
import sys
import csv
import os.path
import time


def comment_strip(iterator):
    for line in iterator:
        if line[:1] == '#' or not line.strip():
            continue
        yield line


class ProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")


def register_students(params):
    try:
        repository = Repo(params['repo_root'])
    except(InvalidGitRepositoryError, NoSuchPathError):
        print("Could not open repository!")
        sys.exit(1)

    # open repo (done)
    # get config parser to rip out submodule urls (explicitly use .gitmodules?)
    # start an import log file
    # toss out existing repos and log them as duplicates - duplicates ignored
    # init all submodules and log
    # commit
    # create tag
    # if remote, push commit and tag

    reg_reader = csv.reader(comment_strip(params['import_file']))

    files_added = []

    with open(os.path.join(params['repo_root'], "last_import.log")) as log_file:

        for reg_line in reg_reader:
            # print(reg_line)
            if len(reg_line) != 2:
                print("Skipping bad entry: ", reg_line)
                print("Skipping bad entry: ", reg_line, file=log_file)
                continue

            try:
                repository.create_submodule(name=reg_line[0], path=reg_line[0], url=reg_line[1], branch='master')
            except:
                # In my tests, if the repo url is bad, it throws an exception with a weird name
                # (something about reading a file that is closed)
                # so it's a generic catch because who knows what happens
                # if it fails, the folders probably exist, but nothing is registered with git
                print("Could not register ", reg_line[0])
                print("Could not register ", reg_line[0], file=log_file)
                continue

            files_added.append(reg_line[0])

            print("Registered ", reg_line[0])
            print("Registered ", reg_line[0], file=log_file)

    # existing submodules are silently ignored by GitPython (OR SO IT SAYS), but I guess that's ok?

    if len(files_added):
        # We added stuff, add our log and modules file
        files_added.append([".gitmodules", "last_import.log"])
        print("Adding files to index...")
        # Probably safe
        repository.index.add(files_added)
        print("Committing...")
        # this needs ot be error checked
        repository.index.commit("Autocheckout student registration at "+time.strftime("%I:%M %p %Z %d/%m/%Y"),
                                committer="Autocheckout")

        if repository.remotes.origin.exists():
            # origin exists, let's push
            print("Pushing to origin...")
            try:
                repository.remotes.origin.push(progress=ProgressPrinter())
            except Exception as e:
                print("Error pushing to origin! " + str(e))

    return


def collect_assignment(params):
    print("Noooope")
    return


# def init_repository(params):
#     print("Nooope")
#     return

# def remove_students(params):
#     print("Nooope")
#     return

def parse_and_execute():
    parser = argparse.ArgumentParser()

    subparse_master = parser.add_subparsers(title="Commands")

    register_parser = subparse_master.add_parser('register', help="Register students")
    register_parser.add_argument('repo_root', type=str, help="Path to the submission repository")
    register_parser.add_argument('import_file', type=argparse.FileType('r'), help="Student list to register")
    register_parser.add_argument('--subdir', type=str, help="Subdirectory to place repositories into")
    register_parser.set_defaults(action=register_students)

    collect_parser = subparse_master.add_parser('collect', help="Collect assignment")
    collect_parser.add_argument('repo_root', type=str, help="Path to the submission repository")
    collect_parser.add_argument('tag', type=str, help="Tag to collect")
    collect_parser.add_argument('--recollect', action='store_true', help="Recollect tag")
    collect_parser.set_defaults(action=collect_assignment)

    # init_parser = subparse_master.add_parser('initialize', help="Create a new submission repo")
    # init_parser.add_argument('repo_root', help="Repository to create")
    # init_parser.add_argument('remote_url', help="Repository to ")

    args = parser.parse_args()

    params = vars(args)

    # argparse won't throw if no submodule was triggered :/
    if not params:
        parser.print_help()
        parser.exit(1)

    # print(params)

    params['action'](params)

    return


if __name__ == '__main__':
    parse_and_execute()
