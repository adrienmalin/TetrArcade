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
    version="v0.1",
    description="Tetris clone",
    author="AdrienMalin",
    executables=[Executable(
        script="TetrArcade.py",
        icon=icon,
        base=base,
        shortcutDir="AdrienMalin",
        shortcutName="TetrArcade"
    )],
    options={
        "build_exe": {
            "packages": ["arcade", "pyglet"],
            "excludes": ["tkinter", "PyQt4", "PyQt5", "PySide", "PySide2", "arcade.examples"],
            "include_files": "res",
            "silent": True
        },
        "bdist_msi": {
            "data": {
                "Shortcut": [
                    (
                        "TetrArcade",        # Shortcut
                        "TetrArcade",          # Directory_
                        "TetrArcade",           # Name
                        "TetrArcade",              # Component_
                        "[TetrArcade]TetrArcade.exe",# Target
                        None,                     # Arguments
                        None,                     # Description
                        None,                     # Hotkey
                        None,                     # Icon
                        None,                     # IconIndex
                        None,                     # ShowCmd
                        'TetrArcade'               # WkDir
                    )
                ]
            }
        }
    },
)
