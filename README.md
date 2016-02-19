# Autocheckout

Automated tracking and collection of student work via submodules and tags; an extension to Classroom for GitHub.

## Why?

Managing 40+ repositories for every assignment is rather difficult. For our course, we're experimenting with student *workspaces*, a single private repository to hold a student's code throughout the semester.

## How?

Students create a tag for the commit they wish to have graded and push it to GitHub.
Students are able to update their workspace and change the tagged commit until the collection script (autocheckout) is run.

Autocheckout maintains a seperate repo of student submissions, with each workspace checked out as a submodule, making it light and efficient.
When collecting submissions, autocheckout updates all submodules, attempts to checkout the desired tag, logs wether the tag was found, and pushes all this back up to the submission repository and tags the commit with the tag that was collected.
When it's time to grade, simply clone the submissions repo and checkout the desired assignment tag; simple as that.

Autocheckout can be ran manually, or automatically at the submission deadline using your system's `at` queueing system.

Note: Students can reassign tags at any point in time, including after the collection date, but the checkout process selects the tag's commit at that time, not the tag itself.
This, coupled with branch protection, ensures that there is **no way** to modify or update the submitted version after it is collected.

## Setup

1. First, you'll need to create your master workspace.
This repository will be the one you update throughout the course with code updates, supplementary material, and future assignments.
You will most likely want to preload it with notes on how to update the repository and how to submit future work.
An example master readme has been provided in the example directory.

1. Student workspace creation is simple, just create an assignment through the [classroom frontend](https://classroom.github.com/classrooms) and point it towards your master workspace repository.

1. You will need to collect the account names for all your students and invite them to a team that has **read** access to your master repository.
This can likely be automated by the GitHub API, and is the target fo future development.
This allows students to fetch updates from your master workspace as the course proceeds.
***NOTE:*** This only needs to be done if the master workspace repository is private.

1. You will need to enable branch protection for the master branch for all student workspaces and, for safety, the master workspace.
If you're using other branches, you may want to add them as well, but the current version uses the master branch for all collections.
This can be found under Settings => Branches => Protected branches.
This will prevent students from monkeying with their repositories and being able to modify their submission after the collection date.
Students cannot disable branch protection, or even access the settings panel as they do not have admin access to their workspace.
This, also, can be automated in the future, but that portion of the GitHub API is currently under development.

1. Create a submission repository to collect student work in and populate it with student workspace submodules.
This requires a list of student workspaces and some sort of student ID string.
*(work in progress)*.

1. Update the master workspace as class proceeds and schedule assignment collection.
