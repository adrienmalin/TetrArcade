# -*- coding: utf-8 -*-
import sys
from cx_Freeze import setup, Executable

if sys.platform == "win32":
    base = "Win32GUI"
else:
    base = None

setup(
    name="TetrArcade",
    version="0.1",
    description="Tetris clone",
    executables=[Executable(script="TetrArcade.py", icon="icon.ico")],
    options={"build_exe": {"packages": ["arcade"], "excludes": ["tkinter"]}},
)
