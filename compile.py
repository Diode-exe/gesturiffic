from pathlib import Path
import subprocess

class Compile:
    def __init__(self):
        self.prog_name = "Gesturiffic Compiler"
        self.main_script = Path("main.py")
        self.landmarker_model = Path("hand_landmarker.task")
        self.landmarker_model_in_path = Path("main.dist/hand_landmarker.task")
        self.venv_folder = Path(".venv/Lib/site-packages/mediapipe")
        self.error_text_in_red = "\033[91mError:\033[0m"
        self.warning_text_in_yellow = "\033[93mWarning:\033[0m"
        self.success_text_in_green = "\033[92mSuccess:\033[0m"
        self.info_text_in_cyan = "\033[96mInfo:\033[0m"
        self.command = [
            "python.exe",
            "-m",
            "nuitka",
            "--standalone",
            "main.py"
        ]

    def compile(self, test_mode=False, simulate_copy=True, simulate_hand_landmarker_check=True):
        """Compile the main.py script using Nuitka.
        If test_mode is True, skip actual compilation and just simulate it.
        Also checks for the presence of the hand_landmarker.task file and simulates copying it to the dist folder."""
        if not test_mode and simulate_copy or simulate_hand_landmarker_check:
            # this is kind of unnecessary but just in case something goes wrong
            simulate_copy = simulate_hand_landmarker_check = False

        if not test_mode:
            if not self.main_script.exists():
                print(f"{self.prog_name}: {self.error_text_in_red} {self.main_script} not found.\n"
                    "Please ensure it is in the same directory as this script.")
                return

            # nuitka compiler
            try:
                subprocess.run(self.command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"{self.prog_name}: {self.error_text_in_red} Compilation failed with error: {e}")

            if self.landmarker_model.exists():
                print(f"{self.prog_name}: {self.landmarker_model} found. Copying to dist folder...")
                dist_folder = Path("main.dist")
                if dist_folder.exists():
                    subprocess.run(["copy", str(self.landmarker_model),
                                    str(dist_folder)], shell=True, check=True)
            else:
                print(f"{self.prog_name}: {self.warning_text_in_yellow} {self.landmarker_model} not found.\n"
                    "Please download it from Google's documentation\n"
                    "and place it in the same directory as this script.\n")
        else:
            print(f"{self.prog_name}: {self.success_text_in_green} Test compile successful. (Compilation skipped in test mode)")

            if self.landmarker_model.exists():
                print(f"{self.prog_name}: {self.landmarker_model} found. Copying to dist folder...")
                dist_folder = Path("main.dist")
                if dist_folder.exists():
                    print(f"{self.prog_name}: {self.success_text_in_green} {self.landmarker_model} copied to {dist_folder}.\n"
                          "(Copy skipped in test mode)")
            else:
                print(f"{self.prog_name}: {self.warning_text_in_yellow} {self.landmarker_model} not found.\n"
                    "Please download it from Google's documentation\n"
                    "and place it in the same directory as this script.\n")

if __name__ == "__main__":
    compiler = Compile()
    compiler.compile(test_mode=True)
