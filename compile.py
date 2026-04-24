"""Compiler script for Gesturiffic using Nuitka.
This script compiles the main.py file into a standalone executable.
It also checks for the presence of the hand_landmarker.task file and copies it to the dist
folder if it exists. If the model file is missing, it prints a warning message."""

from pathlib import Path
import subprocess
import argparse
import shutil
import sys

class Compile:
    """Class to handle compilation of the main.py script
    using Nuitka and manage the hand_landmarker.task file.
    Takes no args on initialization,
    but has a compile method that can be called with test mode and simulation options."""
    def __init__(self, main_script=None, dist_folder=None, landmarker_model=None):
        self.prog_name = "Gesturiffic Compiler"
        self.version = "2.1.1"
        self.main_script = Path(main_script) if main_script else Path("main.py")
        self.dist_folder = Path(dist_folder) if dist_folder else Path("main.dist")
        self.landmarker_model = Path(landmarker_model) if landmarker_model else Path("hand_landmarker.task")
        self.landmarker_model_in_path = Path(self.dist_folder / "hand_landmarker.task")
        self.venv_folder = Path(".venv/Lib/site-packages/mediapipe")
        self.mediapipe_in_path = Path(self.dist_folder / "mediapipe")
        self.compiled_folder = Path("compiled")
        self.archive_name = f"Gesturiffic_{self.version}.tar.xz"
        self.error_text_in_red = "\033[91mError:\033[0m"
        self.warning_text_in_yellow = "\033[93mWarning:\033[0m"
        self.success_text_in_green = "\033[92mSuccess:\033[0m"
        self.info_text_in_cyan = "\033[96mInfo:\033[0m"
        self.command = [
            sys.executable,
            "-m",
            "nuitka",
            "--standalone",
            str(self.main_script)
        ]
        self.archive_args = [
            "tar",
            "-cvJf",
            self.archive_name,
            str(self.compiled_folder)
        ]

    def compile(self, test_mode_ref=False, simulate_copy_ref=True,
                simulate_hand_landmarker_check_ref=True, run_after_compile_ref=False, archive_ref=False):
        """Compile the main.py script using Nuitka.
        If test_mode is True, skip actual compilation and just simulate it.
        Also checks for the presence of the hand_landmarker.task file
        and simulates copying it to the dist folder."""
        # If not running in test mode, don't simulate copy/check behavior.
        if not test_mode_ref:
            simulate_copy_ref = simulate_hand_landmarker_check_ref = False

        if not test_mode_ref:
            if not self.main_script.exists():
                print(f"{self.prog_name}: {self.error_text_in_red} {self.main_script} not found.\n"
                    "Please ensure it is in the same directory as this script.")
                return

            # nuitka compiler
            try:
                subprocess.run(self.command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"{self.prog_name}: {self.error_text_in_red} "
                      f"Compilation failed with error: {e}")
                return

            if self.landmarker_model.exists():
                print(f"{self.prog_name}: {self.landmarker_model} found. Copying to dist folder...")
                try:
                    # Use shutil.copy for reliable cross-platform copying
                    if not self.dist_folder.exists():
                        self.dist_folder.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(self.landmarker_model), str(self.landmarker_model_in_path))
                    print(f"{self.prog_name}: {self.success_text_in_green} {self.landmarker_model} successfully copied to {self.dist_folder}.")

                    # Copy the mediapipe package directory from the virtualenv into the dist folder.
                    # Use copytree for directories and handle existing destination / permission issues.
                    if self.venv_folder.exists() and self.venv_folder.is_dir():
                        try:
                            if self.mediapipe_in_path.exists():
                                shutil.rmtree(self.mediapipe_in_path)
                            shutil.copytree(self.venv_folder, self.mediapipe_in_path)
                            print(f"{self.prog_name}: {self.success_text_in_green} mediapipe package successfully copied to {self.dist_folder}.")
                        except PermissionError as e:
                            print(f"{self.prog_name}: {self.error_text_in_red} Permission denied while copying mediapipe: {e}\n"
                                  "Try running this script with administrator privileges or ensure the .venv folder is readable.")
                        except Exception as e:
                            print(f"{self.prog_name}: {self.error_text_in_red} Failed to copy mediapipe package: {e}")
                            return
                    else:
                        print(f"{self.prog_name}: {self.warning_text_in_yellow} mediapipe package not found at {self.venv_folder}; skipping mediapipe copy.")

                    if archive_ref:
                        print(f"{self.prog_name}: {self.info_text_in_cyan} Creating archive {self.archive_name} from {self.compiled_folder}...")
                        try:
                            shutil.copytree(self.dist_folder, self.compiled_folder, dirs_exist_ok=True)
                            subprocess.run(self.archive_args, check=True)
                            shutil.rmtree(self.compiled_folder)
                            print(f"{self.prog_name}: {self.success_text_in_green} Archive {self.archive_name} created successfully.")
                        except subprocess.CalledProcessError as e:
                            print(f"{self.prog_name}: {self.error_text_in_red} Failed to create archive: {e}")

                    if run_after_compile_ref:
                        print(f"{self.prog_name}: {self.info_text_in_cyan} Running the compiled executable...")
                        try:
                            subprocess.run([str(self.dist_folder / "main.exe")], check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"{self.prog_name}: {self.error_text_in_red} Failed to run the compiled executable: {e}")

                except Exception as e:
                    print(f"{self.prog_name}: {self.error_text_in_red} Failed to copy model: {e}")

            else:
                print(f"{self.prog_name}: {self.warning_text_in_yellow} {self.landmarker_model} not found.\n"
                    "Please download it from Google's documentation\n"
                    "and place it in the same directory as this script.\n")

        else:
            print(f"{self.prog_name}: {self.success_text_in_green} Test compile successful. (Compilation skipped in test mode)")

            if simulate_hand_landmarker_check_ref:

                if self.landmarker_model.exists():

                    if simulate_copy_ref:
                        print(f"{self.prog_name}: {self.landmarker_model} found. (Simulated) copying to dist folder...")

                        if self.dist_folder.exists():
                            print(f"{self.prog_name}: {self.success_text_in_green} {self.landmarker_model} would be copied to {self.dist_folder}.\n"
                                "(Copy skipped in test mode)")
                        else:
                            print(f"{self.prog_name}: {self.info_text_in_cyan} Dist folder does not exist; copy would create it.")

                    else:
                        print(f"{self.prog_name}: {self.success_text_in_green} Not simulating copy of {self.landmarker_model} to dist folder.\n")

                else:
                    print(f"{self.prog_name}: {self.warning_text_in_yellow} {self.landmarker_model} not found.\n"
                        "Please download it from Google's documentation\n"
                        "and place it in the same directory as this script.\n")

def _parse_args():
    p = argparse.ArgumentParser(description="Compile Gesturiffic with optional test mode")
    p.add_argument('--real', action='store_true',
                   help='Run actual compilation (default: test mode)')
    p.add_argument('--no-simulate-copy', action='store_true',
                   help='In test mode, do not simulate copying the model')
    p.add_argument('--no-simulate-model-check', action='store_true',
                   help='In test mode, do not simulate checking for the model file')
    p.add_argument('--run-after-compile', action='store_true',
                   help='Run the compiled executable after compilation (only works in real mode)')
    p.add_argument('--archive', action='store_true',
                   help='Create a compressed archive of the dist folder after compilation')
    return p.parse_args()

if __name__ == "__main__":
    args = _parse_args()
    compiler = Compile()
    # "not" args.real means test_mode is True when --real is not provided
    # and False when --real is provided
    test_mode = not args.real
    # same with these
    simulate_copy = not args.no_simulate_copy
    simulate_hand = not args.no_simulate_model_check
    run_after_compile = args.run_after_compile
    archive = args.archive
    compiler.compile(test_mode_ref=test_mode,
                     simulate_copy_ref=simulate_copy, simulate_hand_landmarker_check_ref=simulate_hand,
                     run_after_compile_ref=run_after_compile, archive_ref=archive)
    # print(f"{compiler.prog_name}: {compiler.success_text_in_green} "
    #       "Compilation with applied settings completed.")
    # compiler.compile(test_mode=True, simulate_copy=True, simulate_hand_landmarker_check=True)
    # print(f"{compiler.prog_name}: {compiler.success_text_in_green} "
    #       "Test compilation with all simulations completed.")
