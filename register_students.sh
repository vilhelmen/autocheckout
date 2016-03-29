#!/bin/bash

if [ $# -ne 2 ]; then
	echo "$0 REPO_ROOT REGISTER_FILE"
	exit 1
fi

REPO_ROOT=${1}
REGISTER_FILE=${2}

if [[ ! -d ${REPO_ROOT} || ! -f ${REGISTER_FILE} ]]; then
	echo "Repo or register does not exist!"
	exit 1
fi

cd ${REPO_ROOT}

if [ ! git rev-parse >& /dev/null ]; then
	echo "Repo not a git repository!"
	exit 1
fi

# User input probably ok, anything bad past here is mildly catostrophic

# strip all comments and blank lines
REGISTER_DATA=($(sed '/^[[:blank:]]*#/d;s/#.*//;/^\s*$/d' ${REGISTER_FILE}))

STUDENT_IDS=($(printf "%s\n" ${REGISTER_DATA[@]} | cut -d, -f2))

STUDENT_REPOS=($(printf "%s\n" ${REGISTER_DATA[@]} | cut -d, -f1))

if [[ ! -d workspaces ]]; then
	echo "Workspace dir does not exist, creating..."
	if ! mkdir workspaces; then
		echo "Could not create directory!"
		exit 1
	fi
fi

if [[ ! -d logs ]]; then
	echo "Logging dir does not exist, creating..."
	if ! mkdir logs; then
		echo "Could not create logging directory!"
		exit 1
	fi
fi

{
for i in "${!STUDENT_IDS[@]}";do
	echo "IMPORT '${STUDENT_IDS[${i}]}' @ '${STUDENT_REPOS[${i}]}'"
	git submodule add --quiet --name ${STUDENT_IDS[${i}]} ${STUDENT_REPOS[${i}]} workspaces/${STUDENT_IDS[${i}]}
	# --name will set the module name to just the student's id
	# as opposed to workspaces/${ID}

	# I suppose you may want --recurse in some cases if they have submodules
	# But that's more testing than I have the time for and not in our main scope
done

# } |& tee logs/last_import.log
# of course it's not portable because it's still 2007 apparently
} 2>&1 | tee logs/last_import.log

git add --all

git commit -m "Student import at $(date)"