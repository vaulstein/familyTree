# FAMILY TREE
==========================================

<div align="center">
  <a href="http://htmlpreview.github.io/?https://raw.githubusercontent.com/vaulstein/familyTree/master/htmlcov/index.html">
    <img src="https://raw.githubusercontent.com/vaulstein/familyTree/master/coverage.svg" alt="Codecov" />
  </a>
</div>

## INSTALLATION/DEPENDENCIES

Python version for which code has been run is **Python 3.6**

Virtualenv is advised to test the code.
Create virtualenv outside the mavericks folder.

Steps:

     pip install virtualenv
     virtualenv -p /path/to/python3.6 venv
     source venv/bin/activate

Requirements are listed in : *requirements.txt* file

    pip install -r requirements.txt

## Assumptions

1. Once a ROOT node is added, another won't be added.
2. No parent to the ROOT node will be added.
3. List of supported relations in the PDF does not mention some relations like *Husband*, *Wife*
4. Names are unique. Any new member added will also have a unique name.
5. Relations other than those mentioned in the PDF won't be supported
6. Input would be of the format:
    Two parts, separated by spaces, and each part separated by '=' sign with no spaces in between
    for querying - **Person=Name Relation=relation**
    for adding - **Relation=Name Matching_Relation=Name**
7. Partners not related by blood will not be part of the output other than for *Uncle/Aunt*
8. Non-blood related partners need to be added after adding partner.

## Running

After installing dependencies, script can be run as follows:

    cd mavericks
    python3 family_tree.py

On running this, a prepopulated tree will be shown.
You can query/add to this tree. Refer to assumptions for query construction.

To continue querying/adding, you can select *'y'* on command prompt:

    Do you want to Continue? Type "y" to continue

## Test Cases

Test cases can be run using below command:

    python3 -m pytest --cov=.

To generate coverage report html files, run:

    python3 -m pytest --cov=. --cov-report html


You can check the last run coverage report file in *htmlcov*.
Open the index.html to view detailed report of hits and misses.

Warnings in test cases are for this - [pytest fixtures](https://docs.pytest.org/en/latest/proposals/parametrize_with_fixtures.html)
