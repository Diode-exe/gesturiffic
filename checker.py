import os
import argparse

class Checker:
    """A simple class to check if the necessary files and folders are present."""
    def __init__(self):
        self.required_venv = ".venv"
        self.activate_script = ""
        if os.name == 'nt':  # Windows
            self.activate_script = f"{self.required_venv}\\Scripts\\activate"
        else:  # Unix/Linux/Mac
            self.activate_script = f"source {self.required_venv}/bin/activate"

    def check_venv(self):
        """Check if the required virtual environment is present."""
        if not os.path.isdir(self.required_venv):
            print(f"Error: Required virtual environment '{self.required_venv}' not found.")
            print("Rerun script with --make-changes to create it automatically.")
            return False
        return True

    def make_changes(self):
        """Make changes to the system if necessary files/folders are missing."""
        if not self.check_venv():
            print(f"Creating virtual environment '{self.required_venv}'...")
            os.system(f"python -m venv {self.required_venv}")

            os.system(f"{self.activate_script} && pip install -r requirements.txt")
            print(f"Virtual environment '{self.required_venv}' created.")

    def parse_args(self):
        """Parse command line arguments. Don't run this outside of the bottom of this file."""
        parser = argparse.ArgumentParser(description="Check for necessary files and folders.")
        parser.add_argument('--make-changes', action='store_true', help="Make changes to the system if necessary files/folders are missing.")
        return parser.parse_args()

if __name__ == "__main__":
    checker = Checker()
    args = checker.parse_args()
    if args.make_changes:
        checker.make_changes()
    else:
        if not checker.check_venv():
            print("Please run the script with --make-changes to create the necessary virtual environment.")
