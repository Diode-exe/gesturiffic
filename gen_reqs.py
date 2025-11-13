import os
import sys
import pkg_resources
import importlib

project_path = os.path.dirname(os.path.abspath(__file__))

# Find all .py files
py_files = [f for f in os.listdir(project_path) if f.endswith(".py")]

packages = set()

for f in py_files:
    with open(os.path.join(project_path, f), "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("import "):
                pkg = line.split()[1].split('.')[0]
                packages.add(pkg)
            elif line.startswith("from "):
                pkg = line.split()[1].split('.')[0]
                packages.add(pkg)

# Filter only installed packages
installed = {pkg.key for pkg in pkg_resources.working_set}
used = [pkg for pkg in packages if pkg.lower() in installed]

# Write requirements.txt
with open("requirements.txt", "w", encoding="utf-8") as req:
    for pkg in sorted(used):
        req.write(f"{pkg}\n")

print("requirements.txt generated with:", used)
