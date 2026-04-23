from pathlib import Path
import subprocess

class Compile:
    def __init__(self):
        self.prog_name = "Gesturiffic Compiler"
        self.main_script = Path("main.py")
        self.landmarker_model = Path("hand_landmarker.task")
        self.landmarker_model_in_path = Path("main.dist/hand_landmarker.task")
        self.venv_folder = Path(".venv/Lib/site-packages/mediapipe")
        self.command = [
            "python.exe",
            "-m",
            "nuitka",
            "--standalone",
            "main.py"
        ]

    def compile(self, test_mode=False):
        if not test_mode:
            if not self.main_script.exists():
                print(f"{self.prog_name}: Error: {self.main_script} not found.\n"
                    "Please ensure it is in the same directory as this script.")
                return

            # nuitka compiler
            try:
                subprocess.run(self.command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"{self.prog_name}: Error: Compilation failed with error: {e}")

            if self.landmarker_model.exists():
                print(f"{self.prog_name}: {self.landmarker_model} found. Copying to dist folder...")
                dist_folder = Path("main.dist")
                if dist_folder.exists():
                    subprocess.run(["copy", str(self.landmarker_model),
                                    str(dist_folder)], shell=True, check=True)
            else:
                print(f"{self.prog_name}: Warning: {self.landmarker_model} not found.\n"
                    "Please download it from Google's documentation\n"
                    "and place it in the same directory as this script.\n")
        else:
            print(f"{self.prog_name}: Test compile successful. (Compilation skipped in test mode)")

            if self.landmarker_model.exists():
                print(f"{self.prog_name}: {self.landmarker_model} found. Copying to dist folder...")
                dist_folder = Path("main.dist")
                if dist_folder.exists():
                    print(f"{self.prog_name}: {self.landmarker_model} copied to {dist_folder}.\n"
                          "(Copy skipped in test mode)")
            else:
                print(f"{self.prog_name}: Warning: {self.landmarker_model} not found.\n"
                    "Please download it from Google's documentation\n"
                    "and place it in the same directory as this script.\n")

    # def test_compile(self):
    #     if not self.main_script.exists():
    #         print(f"{self.prog_name}: Error: {self.main_script} not found.\n"
    #             "Please ensure it is in the same directory as this script.")
    #         return

    #     # nuitka compiler
    #     # try:
    #     #     subprocess.run(self.command, check=True)
    #     # except subprocess.CalledProcessError as e:
    #     #     print(f"{self.prog_name}: Error: Compilation failed with error: {e}")
    #     print(f"{self.prog_name}: Test compile successful. (Compilation skipped in test mode)")

    #     if self.landmarker_model.exists():
    #         print(f"{self.prog_name}: {self.landmarker_model} found. Copying to dist folder...")
    #         dist_folder = Path("main.dist")
    #         if dist_folder.exists():
    #             # subprocess.run(["copy", str(self.landmarker_model),
    #             #                 str(dist_folder)], shell=True, check=True)
    #             print(f"{self.prog_name}: {self.landmarker_model} copied to {dist_folder}.\n"
    #                   "(Copy skipped in test mode)")
    #     else:
    #         print(f"{self.prog_name}: Warning: {self.landmarker_model} not found.\n"
    #             "Please download it from Google's documentation\n"
    #             "and place it in the same directory as this script.\n")

if __name__ == "__main__":
    compiler = Compile()
    compiler.compile(test_mode=True)
