#!/bin/bash

if [ $# -ne 2 ]; then
	echo "$0 <REPO_ROOT> <REGISTER>"
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

REPO_ROOT=${1}
REGISTER_FILE=${2}

# strip all comments and blank lines
REGISTER_DATA=($(sed '/^[[:blank:]]*#/d;s/#.*//;/^\s*$/d' ${REGISTER_FILE}))


STUDENT_IDS=($(printf "%s\n" ${REGISTER_DATA[@]} | cut -d, -f2))

STUDENT_REPOS=($(printf "%s\n" ${REGISTER_DATA[@]} | cut -d, -f1))

for i in "${!STUDENT_IDS[@]}";do
	echo ${STUDENT_IDS[${i}]} ${STUDENT_REPOS[${i}]}
	git submodule add --name ${STUDENT_IDS[${i}]} ${STUDENT_REPOS[${i}]} workspaces/${STUDENT_IDS[${i}]}
done

git add --all

git commit -m "Student import at $(date)"