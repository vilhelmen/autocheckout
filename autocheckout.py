#!/usr/bin/env python3

import argparse
import sys
import csv
import os.path
import time
import logging
import subprocess  # sh sounds cool, but I'm just going to stick to subprocess


def comment_strip(iterator):
    for line in iterator:
        line = line.strip()
        if not line or line[:1] == '#':
            continue
        yield line


class MultiLog:
    def __init__(self, log_stream, logfile_path, mode='a'):
        self.master_log = logging.getLogger(log_stream)
        self.master_log.setLevel(logging.INFO)
        stdout_log = logging.StreamHandler(sys.stdout)
        stdout_log.setLevel(logging.INFO)
        self.master_log.addHandler(stdout_log)
        try:
            self.file_log = logging.FileHandler(logfile_path, mode=mode)
        except:
            print("Log file '{0}' could not be created!".format(logfile_path))
            raise
        self.file_log.setLevel(logging.INFO)
        self.master_log.addHandler(self.file_log)

    def close_file(self):
        self.master_log.removeHandler(self.file_log)
        self.file_log.close()

    def log(self, msg, *args, **kwargs):
        self.master_log.info(msg, *args, **kwargs)

    def __call__(self, msg, *args, **kwargs):
        self.log(msg, *args, **kwargs)


def tentative_sync(log):
    # We're going to attempt tp pull/push
    # Return true if either there is no remote, or we pulled/pushed successfully
    log("=== Syncing ===")
    # silently query if git has a remote called origin
    # (a pull with no remote and a pull that conflicts both return 1)
    remote_status = run_manual_command(['git', 'remote', 'get-url', 'origin'], log, True)
    if remote_status == 0:
        # remote exists, cool.
        pull_status = run_manual_command(['git', 'pull', '--no-edit', 'origin', 'master'], log)
        if pull_status == 0:
            log("Pull from master successful, attempting to push any changes.")
            push_status = run_manual_command(['git', 'push', '--follow-tags', 'origin', 'master'], log)
            if push_status == 0:
                log("Push successful, sync complete!")
                return True
            if push_status == 1:
                log("Push failed for some reason. Halting :(")
                return False
            else:
                log("Git/the OS exploded on us. Halting :(")
                return False

        elif pull_status == 1:
            log("Pull failed. Either there's a conflict, or the network's down.\n"
                "Manual correction required to continue :(\n"
                "I am so sorry. You're probably about to have a bad day.")
            return False
        else:
            log("Git/the OS exploded on us. Halting :(")
            return False

    elif remote_status == 128:
        log("Remote 'origin' does not exist, nothing to do.")
        return True
    else:
        log("Git/the OS exploded on us. Halting :(")
        return False


def check_and_sync():
    # Has it been initialized?
    if os.path.exists('autocheckout') and os.path.exists('autocheckout/logs'):
        # should return True if either there's no remote, or we synced fine
        return tentative_sync(print)

    else:
        print("Repo hasn't been initialized yet, exiting.")
        return False


def add_files(log):
    log("=== Adding Files ===")
    return run_command(['git', 'add', '--all'], "add changes", log)


def commit_files(commit_message, log):
    if commit_message:
        log("=== Committing ===")
        return run_command(['git', 'commit', '-m', commit_message], "commit changes", log)
    return False


def tag_commit(tag_name, tag_message, log):
    if tag_name and tag_message:
        log("=== Tagging ===")
        return run_command(['git', 'tag', '-a', tag_name, '-m', tag_message], "tag commit", log)
    return False


def verify_git_and_cwd(params):
    try:
        # Does the dir exist?
        os.chdir(params['repo_root'])
        # Is it a repo?
        return run_command(['git', 'rev-parse'], "verify repository", print)
    except OSError as err:
        print("Repo does not exist / permission denied / something broke: {0}".format(err))
    except Exception as err:
        print("Mystery error! {0} {1}".format(err, sys.exc_info()[0]))
    return False


# Returns True/False if exec returned 0
# Spits out error message if it failed
def run_command(command, activity, log_func, silent=False):
    if run_manual_command(command, log_func, silent) != 0:
        log_func("=~= Failed to {0} =~=".format(activity))
        return False
    return True


# Returns error code for processing
def run_manual_command(command, log_func, silent=False):
    try:
        # Launch git
        with subprocess.Popen(command, universal_newlines=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, bufsize=1) as proc:
            if not silent:
                for line in proc.stdout:
                    # If it's print, I can just say end=''
                    # Which is lovely. Logger, however, refuses to play nice.
                    # It would be fine if we were waiting for the output in one hunk
                    # But this way we stay live, but we would explode the log with newlines
                    log_func(line[:-1] if line[-1] == '\n' else line)
            return proc.wait()

    except OSError as err:  # Git magically stopped existing. Or other OS errors, couldn't fork, etc.
        log_func("Mystery OS error. OS says:\n=~=\n{0}\n{1}\n=~=".format(sys.exc_info()[0], err))
    except Exception as err:
        # Idk, man. Computers are hard.
        log_func("Mystery error! Exception says:\n=~=\n{0}\n{1}\n=~=".format(sys.exc_info()[0], err))

    return -999


def register_students(params):
    # already verified, cwd is repo_root
    # Start logging
    full_log = MultiLog("full_log", "autocheckout/logs/last_import.log", 'w')
    result_log = MultiLog("import_results", "autocheckout/logs/import_status.log", 'w')

    full_log("=== Preparing Registration ===")

    result_log("STUDENT,STATUS")
    # Alrighty, just open the csv and loop for all the entries

    try:
        student_list = csv.reader(comment_strip(params['import_file']))
    except Exception as err:
        full_log("Something terrible happened with the reader. Exception says:\n===\n{0}\n===".format(err))
        raise
    else:
        for registration_info in student_list:
            # Good input?
            if len(registration_info) != 2:
                full_log("Skipping bad entry '%s'", registration_info)
                continue
            # Pull out data
            repo = registration_info[0]
            student = registration_info[1]

            full_log("Registering '%s' @ '%s'...", student, repo)
            # if submodule_add(student, repo, params['subdir'], full_log):
            if run_command(
                    ['git', 'submodule', 'add', '--name', student, repo, params['subdir'] + '/' + student],
                    "register student '{0}'".format(student), full_log):
                result_log(student + ",REGISTERED")
            else:
                result_log(student + ",ERROR")

        # well, at the least, SOMETHING happened
        # Close the logs because we're about to commit them
        full_log("=== Committing Changes ===")
        full_log.close_file()
        result_log.close_file()

        if add_files(full_log):
            if commit_files('"Student registration at ' + time.ctime(), full_log):
                tentative_sync(full_log)

    return


def collect_assignment(params):
    print("Noooope")
    return


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


def amend(params):
    # https://printf2linux.wordpress.com/2012/04/09/insert-a-commit-in-the-past-git/
    # checkout new branch (always same name, fail if it already exists?)
    # git add <whatever>
    # git commit
    # git rebase BRANCH master
    # Hope there aren't merge conflicts
    # switch to master
    # push
    # kill temp branch
    print("Noooope")
    return


def init_repository(params):
    # does repo_root exist? Create it. (but don't go crazy with directories)
    # is it under version control? Git init
    # setup autocheckout stuff. Idk.
    print("=== Initializing Repository ===")
    if run_command(['git', 'init', params['repo_root']], "initialize git repository", print):
        # Cool. Make directories
        if verify_git_and_cwd(params):
            if os.path.exists('autocheckout'):
                print("=~= ERROR: Autocheckout already initialized. Halting. =~=")
            else:
                try:
                    os.mkdir('autocheckout', 0o755)
                    os.mkdir('autocheckout/logs', 0o755)

                    # This log mostly exists so we can add the directory hierarchy
                    # Git doesn't like empty folders
                    full_log = MultiLog('log_init', 'autocheckout/logs/init.log', 'a')
                    if params['remote']:
                        full_log("=== Preparing Remote ===")
                        remote = params['remote']
                        full_log("=~= WARNING: Access to origin must be keyless =~=")
                        run_command(['git', 'remote', 'add', 'origin', remote],
                                    "add remote 'origin' @ '{0}".format(remote),
                                    full_log)

                    full_log("=== Initialization Complete ===")
                    full_log("=== Saving State ===")
                    full_log.close_file()

                    if add_files(full_log):
                        if commit_files("Repository Initialization", full_log):
                            # WHOOPS. Don't pull if it doesn't exist...
                            # tentative_sync(full_log)
                            full_log("=== Pushing ===")
                            run_command(['git', 'push', 'origin', 'master'], "push to origin", full_log)

                except OSError as err:
                    print("Couldn't make directory structure, OS says: {0}".format(err))
                except Exception as err:
                    print("Mystery error! {0} {1}".format(sys.exc_info()[0], err))

    return


def deregister_students(params):
    # I already forgot how to do this. Ugh.
    # Something about deinit and then an rm?
    # git submodule deinit NAME
    # git rm --cached NAME

    # Uhhh, really only supports one student at a time.
    # Figured it wasn't an issue unless like half the class drops/dies
    # I also can't (quickly) figure out how to toggle single/bulk
    # Also, please don't use this to cycle the semester. Just toss it all and start over.

    print("Nooope")
    return


def parse_and_execute():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    subparse_master = parser.add_subparsers(title="Commands")

    register_parser = subparse_master.add_parser('register', help="Register students")
    register_parser.add_argument('repo_root', type=str, help="Path to the submission repository")
    register_parser.add_argument('import_file', type=argparse.FileType('r'),
                                 help="Student list to register (CSV: repo_url,student_id)")
    register_parser.add_argument('--subdir', type=str, default='workspaces',
                                 help="Subdirectory to place repositories into")
    register_parser.set_defaults(action=register_students)

    collect_parser = subparse_master.add_parser('collect', help="Collect assignment")
    collect_parser.add_argument('repo_root', type=str, help="Path to the submission repository")
    collect_parser.add_argument('tag', type=str, help="Tag to collect")
    collect_parser.add_argument('--recollect', action='store_true', help="Recollect tag")
    collect_parser.set_defaults(action=collect_assignment)

    init_parser = subparse_master.add_parser('init', help="Create a new submission repo")
    init_parser.add_argument('repo_root', type=str, help="Repository to create")
    init_parser.add_argument('--remote', type=str, help="New remote to sync with")
    init_parser.set_defaults(action=init_repository)

    remove_parser = subparse_master.add_parser('deregister', help="Remove students")
    remove_parser.add_argument('repo_root', type=str, help="Path to the submission repository")
    remove_parser.add_argument('students', type=str, nargs='+',
                               help="List of students to remove")
    remove_parser.add_argument('--subdir', type=str, default='workspaces',
                                 help="Repository subdirectory")
    remove_parser.set_defaults(action=deregister_students)

    args = parser.parse_args()

    params = vars(args)

    # argparse won't throw if no submodule was triggered :/
    if not params:
        parser.print_help()
        parser.exit(1)

    # print(params)

    if params['action'] == init_repository or (verify_git_and_cwd(params) and check_and_sync()):
        params['action'](params)

    return


if __name__ == '__main__':
    parse_and_execute()
