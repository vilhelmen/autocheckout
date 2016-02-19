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

# For function export instead of giant command string
#function checkout_func {
#
#}

export TAG=${2}
export LOCATE_LOG='submission_status.log'
export MASTER_LOG='checkout.log'

echo "STUDENT,${TAG}_STATUS,COMMIT" > ${LOCATE_LOG}


{
  echo -e "=== AUTOCHECKOUT BEGIN AT $(date) ==="
  echo -e "=== AUTOCHECKOUT PULL ===\n\n\n"

  git pull --recurse-submodules

  #echo -e "=== AUTOCHECKOUT UPDATE ===\n\n\n"
  #git submodule update

  echo -e "\n\n\n=== AUTOCHECKOUT ${TAG} CHECKOUT ===\n\n\n"
  git submodule foreach '(git checkout -q ${TAG} && (commit = $(git rev-parse HEAD) ; echo "Tag ${TAG} FOUND for ${name} at ${commit}" ; echo "${name},FOUND,${commit}" > "${toplevel}/${LOCATE_LOG}")) || (git checkout -q master ; commit = $(git rev-parse HEAD) ; echo "Tag ${TAG} MISSING for ${name} before ${commit}" ; echo "${name},MISSING,${commit}" > "${toplevel}/${LOCATE_LOG}")'

  echo "=== AUTOCHECKOUT COMPLETE, BEGIN COMMIT ==="

} 2>&1 > ${MASTER_LOG}

git commit -a -m "Autocheckout for ${2} at $(date)"

git tag -a ${TAG} -m "Autocheckout for ${2} at $(date)"

git push origin master

git push --tags origin master
