# Before you start
1. Make sure you have python installed. FairyMander uses python 3.11 or above

2. Create a virtual environment

In VSCode:
- Press `Ctrl-Shift-P`
- Select `Python: Create Environment`
- Create virtual environment in 3.11 with the Fairymander requirements.txt

Using python command line:
`python3 -m venv .venv`

Now activate the script, see below
`pip install -r requirements.txt`

You can now enter the virtual environment using jupyter notebook and selecting it

You can also activate it via command line...
- Linux + Mac: `source .venv/Scripts/activate`
- Windows Command Prompt: `call .venv/Scripts/activate`

3. Install fairymander package
First, activate the .venv (see "You can also activate it via command line...")

`cd` into the `FaryMander/fairymander` folder, if you have not already

build the fairymander package using `pip install -e .`

# Adding a package
If you want to add a package, put it in requirement.txt with the name and version using the same format as the packages listed there.