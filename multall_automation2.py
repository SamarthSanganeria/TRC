import subprocess

import os


def open_cygwin_and_run_commands():
    #cygwin_mintty = r"C:\cygwin64\bin\mintty.exe"
    #project_dir = "/cygdrive/c/Users/lenovo/PycharmProjects/Multall_Codes"

    cwd = os.getcwd()

    cygwin_mintty = os.path.join(cwd, "cygwin", "bin", "mintty.exe")
    project_dir = os.path.join(cwd, "multall")

    # Convert Windows paths to Cygwin style for commands inside mintty
    project_dir_cyg = "/cygdrive/" + project_dir[0].lower() + project_dir[2:].replace("\\", "/")
    project_dir=project_dir_cyg

    commands = f'''cd {project_dir} && \
echo "Compiling MEANGEN..." && \
gfortran -o5 meangen-17.4.f -o meangen-17.4.x && \
echo "Running MEANGEN with input file..." && \
echo F | ./meangen-17.4.x < meangen.in && \
echo "Compiling STAGEN..." && \
gfortran -o5 stagen-17.3.f -o stagen-17.3.x && \
echo "Running STAGEN..." && \
./stagen-17.3.x < stagen.dat && \
echo "Compiling MULTALL..." && \
gfortran -o5 multall-open-17.5.f -o multall-open-17.5.x && \
echo "Running MULTALL..." && \
./multall-open-17.5.x < stage_new.dat ; exec bash'''

    cmd = [
        cygwin_mintty,
        "-i", "/Cygwin-Terminal.ico",
        "-e", "/bin/bash", "-l", "-c", commands
    ]

    subprocess.Popen(cmd)

if __name__ == "__main__":
    open_cygwin_and_run_commands()
