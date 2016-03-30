#!/usr/bin/env python3

import argparse
import sys
import csv
import os.path
import time
import subprocess
import logging


def comment_strip(iterator):
    for line in iterator:
        if line[:1] == '#' or not line.strip():
            continue
        yield line


def check_initialized():
    # Has it been initialized?
    if os.path.exists('.autocheckout'):
        return True
    else:
        print("Repo hasn't been initialized yet, exiting.")
        return False


def verify_and_cwd(params):
    try:
        # Does the dir exist?
        os.chdir(params['repo_root'])
        # Is it a repo?
        subprocess.run(['git', 'rev-parse'], check=True)
    except OSError as err:
        print("Repo does not exist, or permission denied: {0}".format(err))
        raise
    except subprocess.CalledProcessError as err:
        print("Git says this isn't a repository!")
        raise
    except:
        print("Mystery error occurred: ", sys.exc_info()[0])
        raise
    return


def create_multilog(log_stream, logfile_path, mode='a'):
    master_log = logging.getLogger(log_stream)
    master_log.setLevel(logging.INFO)

    stdout_log = logging.StreamHandler(sys.stdout)
    stdout_log.setLevel(logging.INFO)

    file_log = logging.FileHandler(logfile_path, mode=mode)
    file_log.setLevel(logging.INFO)

    master_log.addHandler(stdout_log)
    master_log.addHandler(file_log)

    return master_log


def run_command(command, activity_err_str, log_function):
    try:
        # Launch git
        result = subprocess.run(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                check=True)
        # output?
        result = result.stdout.strip()
        if result:
            log_function(result)
    except subprocess.CalledProcessError as err:
        # Git returned an error code
        log_function("Failed to {0}, git returned {1}, says:\n=~=\n{2}\n=~=".format(activity_err_str, err.returncode,
                                                                                  err.stdout.strip()))
    except OSError as err:
        # Git magically stopped existing. Or other OS errors, couldn't fork, etc.
        log_function("Mystery OS error. OS says:\n=~=\n{0}\n=~=".format(err))
    except Exception as err:
        # Idk, man. Computers are hard.
        log_function("Mystery error! Exception says:\n=~=\n{0}\n=~=".format(err))
    else:
        return True
    return False


def register_students(params):
    # already verified, cwd is repo_root
    # Start logging
    full_log = create_multilog("full_log", "logs/last_import.log", 'w')
    result_log = create_multilog("import_results", "logs/import_status.log", 'w')

    full_log.info("=== Preparing Registration ===")

    result_log.info("STUDENT,STATUS")
    # Alrighty, just open the csv and loop for all the entries

    try:
        student_list = csv.reader(comment_strip(params['import_file']))
    except Exception as err:
        full_log.info("Something terrible happened with the reader. Exception says:\n===\n{0}\n===".format(err))
        raise
    else:
        for registration_info in student_list:
            # Good input?
            if len(registration_info) != 2:
                full_log.info("Skipping bad entry '%s'", registration_info)
                continue
            # Pull out data
            repo = registration_info[0]
            student = registration_info[1]

            full_log.info("Registering '%s' @ '%s'...", student, repo)
            # if submodule_add(student, repo, params['subdir'], full_log):
            if run_command(
                    ['git', 'submodule', 'add', '--name', student, repo, params['subdir'] + '/' + student],
                    "register student '{0}'".format(student), full_log.info):
                result_log.info(student + ",REGISTERED")
            else:
                result_log.info(student + ",ERROR")

        # well, at the least, SOMETHING happened
        # Close the logs because we're about to commit them
        full_log.info("=== Committing Changes ===")
        logging.shutdown()

        # if I was smart, I'd figure out how to wrap that subprocess call and just make it return a bool
        # well, I tried
        print("=== Adding Files ===")
        if run_command(['git', 'add', '--all'], "add", print):
            print("=== Committing ===")
            if run_command(['git', 'commit', '-m', '"Student registration at ' + time.ctime()], "commit", print):
                print("=== Pushing ===")
                run_command(['git', 'push'], "push", print)

    return


def collect_assignment(params):
    print("Noooope")
    return
    # ['git', 'tag', '-a', tag_name, '-m', tag_msg]


#     try:
#         repository = Repo(params['repo_root'])
#     except(InvalidGitRepositoryError, NoSuchPathError):
#         print("Could not open repository!")
#         sys.exit(1)
#
#     # open repo (done)
#     # Recursive pull (all submodules)
#     # checkout of all submodules
#     #   if checkout of tag fails, checkout master
#     # Log checkout status for all modules
#     #   student,status,hash
#     # Commit, tag, optionally push both
#
#     # With recollect... overwrite previous tag?
#     # Need to test what happens if you don't delete the prev tag before pushing the new one
#
#     # AT SOME POINT, refine to support update of certain subdir (i.e. single class)
#     # instead of EVERYTHING
#
#     submodules = repository.submodules
#
#     with open(os.path.join(params['repo_root'], "last_collection.log"), 'w') as log_file, open(
#             os.path.join(params['repo_root'], "last_collection.log"), 'w') as submission_log:
#         print("STUDENT,TAG_STATUS,COMMIT", file=submission_log)
#         if submodules:
#             for submod in submodules:
#                 try:
#
#                 # Ok, actually, this is kinda annoying
#                 # we basically have to go call git commands
#                 # So what's the point of this library
#                 # going back to the bash impl.
#
#                 except Exception as e:
#                     print("An error occured working with ")
#
#         else:
#             print("Nothing to do!", file=log_file)
#
#     return


def init_repository(params):
    # does repo_root exist? Create it. (but don't go crazy with directories)
    # is it under version control? Git init
    # setup autocheckout stuff. Idk.
    print("Nooope")
    return


# def remove_students(params):
#     print("Nooope")
#     return

def parse_and_execute():
    parser = argparse.ArgumentParser()

    subparse_master = parser.add_subparsers(title="Commands")

    register_parser = subparse_master.add_parser('register', help="Register students")
    register_parser.add_argument('repo_root', type=str, help="Path to the submission repository")
    register_parser.add_argument('import_file', type=argparse.FileType('r'), help="Student list to register")
    register_parser.add_argument('--subdir', type=str, default='workspaces',
                                 help="Subdirectory to place repositories into")
    register_parser.set_defaults(action=register_students)

    collect_parser = subparse_master.add_parser('collect', help="Collect assignment")
    collect_parser.add_argument('repo_root', type=str, help="Path to the submission repository")
    collect_parser.add_argument('tag', type=str, help="Tag to collect")
    collect_parser.add_argument('--recollect', action='store_true', help="Recollect tag")
    collect_parser.set_defaults(action=collect_assignment)

    init_parser = subparse_master.add_parser('init', help="Create a new submission repo")
    init_parser.add_argument('repo_root', help="Repository to create")
    init_parser.set_defaults(action=init_repository)
    # init_parser.add_argument('remote_url', help="Repository to ")

    args = parser.parse_args()

    params = vars(args)

    # argparse won't throw if no submodule was triggered :/
    if not params:
        parser.print_help()
        parser.exit(1)

    # print(params)

    verify_and_cwd(params)

    if params['action'] == init_repository or check_initialized():
        params['action'](params)

    return


if __name__ == '__main__':
    parse_and_execute()
