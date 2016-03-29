#!/bin/bash

if [ $# -ne 2 ]; then
	echo "$0 <REPO_ROOT> <TAG>";
	exit 1;
fi

# go to repo root, pull EVERYTHING
# Update of all submodules not actually needed, probably
# foreach and checkout desired tag
# dump full log to file
# commit and push

cd ${1}

export TAG=${2}
export LOCATE_LOG='submission_status.log'
export MASTER_LOG='checkout.log'

# For function export instead of giant command string
# buuuut only works in bash. Which is a shame since I use zsh
#function checkout_func {
#  # "The command has access to the variables $name, $path, $sha1 and $toplevel"
#  if [ $# -ne 4 ]; then
#    echo "$0 <NAME> <PATH> <SHA1> <TOPLEVEL>"
#    return 1
#  fi
#
#  NAME=${1}
#  PATH=${2}
#  SHA1=${3}
#  TOPLEVEL=${4}
#
#  if git checkout -q ${TAG}; then
#    # Submission found! Log it
#    commit=$(git rev-parse HEAD)
#    echo "Tag ${TAG} FOUND for ${NAME} at ${commit}"
#    echo "${NAME},FOUND,${commit}" >> "${TOPLEVEL}/${LOCATE_LOG}"
#  else
#    # welp, submission not found, jump to master and log
#    git checkout -q master
#    commit=$(git rev-parse HEAD)
#    echo "Tag ${TAG} MISSING for ${NAME} by ${commit}"
#    echo "${NAME},MISSING,${commit}" >> "${TOPLEVEL}/${LOCATE_LOG}"
#  fi
#  return 0
#}
#export -f checkout_func

echo "STUDENT,${TAG}_STATUS,COMMIT" > ${LOCATE_LOG}

{
  echo -e "=== AUTOCHECKOUT BEGIN AT $(date) ==="
  echo -e "=== AUTOCHECKOUT PULL ===\n\n\n"

  # Miltiple calls to make sure it actually goes.
  # maybe my connection in the classroom is just spotty, but git seems to
  # get stuck at certain repos and they fail and have to be redone
  # Always the same ones, too, which is weird.
  git pull -t --recurse-submodules
  sleep 5
  git pull -t --recurse-submodules
  sleep 5
  git pull -t --recurse-submodules

  #echo -e "=== AUTOCHECKOUT UPDATE ===\n\n\n"
  #git submodule update

  echo -e "\n\n\n=== AUTOCHECKOUT ${TAG} CHECKOUT ===\n\n\n"
  # exporting a function doesn't work
  # At least, not with what I expected.
  # Exported functions can't refer to things like $name because they get resolved HERE it seems
  # So I guess it just needs to be changed to accept parameters like $name
  git submodule foreach '(git checkout -q ${TAG} && (commit=$(git rev-parse HEAD) ; echo "Tag ${TAG} FOUND for ${name} at ${commit}" ; echo "${name},FOUND,${commit}" >> "${toplevel}/${LOCATE_LOG}")) || (git checkout -q master ; commit=$(git rev-parse HEAD) ; echo "Tag ${TAG} MISSING for ${name} by ${commit}" ; echo "${name},MISSING,${commit}" >> "${toplevel}/${LOCATE_LOG}")'

  echo "=== AUTOCHECKOUT COMPLETE, BEGIN COMMIT ==="

} &> ${MASTER_LOG}

git commit -a -m "Autocheckout for ${2} at $(date)"

git tag -a ${TAG} -m "Autocheckout for ${2} at $(date)"

git push origin master

git push --tags origin master
