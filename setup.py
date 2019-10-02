# -*- coding: utf-8 -*-
import sys
from cx_Freeze import setup, Executable

if sys.platform == "win32":
    base = "Win32GUI"
    icon = "icon.ico"
else:
    base = None
    icon = None

setup(
    name="TetrArcade",
    version="0.1",
    description="Tetris clone",
    author="adrienmalin",
    executables=[Executable(
        script="TetrArcade.py",
        icon=icon,
        base=base
    )],
    options={
        "build_exe": {
            "packages": ["arcade", "pyglet"],
            "excludes": ["tkinter", "PyQt4", "PyQt5", "PySide", "PySide2"],
            "include_files": "res",
            "silent": True
        }
    },
)
