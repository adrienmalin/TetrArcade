# -*- coding: utf-8 -*-
import sys
from cx_Freeze import setup, Executable

if sys.platform == "win32":
    base = "Win32GUI"
    icon = "icon.ico"
else:
    base = None
    icon = None

excludes = [
    "tkinter",
    "PyQt4",
    "PyQt5",
    "PySide",
    "PySide2"
]

executable = Executable(
    script = "TetrArcade.py",
    icon = icon,
    base = base,
    shortcutName="TetrArcade",
    shortcutDir="DesktopFolder"
)

options = {
    "build_exe": {
        "packages": ["arcade", "pyglet"],
        "excludes": excludes,
        "include_files": "res",
        "silent": True
    }
}
setup(
    name = "TetrArcade",
    version = "0.2-dev",
    description = "Tetris clone",
    author = "AdrienMalin",
    executables = [executable],
    options = options,
)
