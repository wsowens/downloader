"""
Freeze downloader.py and its dependencies into cross-platform executables
"""
import sys
import os
from cx_Freeze import setup, Executable
import cx_Freeze.util

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name = "ez downloader",
      version = "0.1.1",
      options = {
        'build_exe': {'include_files': ["downloader.ui", 'icon.ico', 'icon.png']},
        'bdist_msi': {'all_users': True, 'install_icon': 'icon.ico'}
      },
      description = " Simple GUI wrapper around youtube-dl",
      executables = [Executable("downloader.py", base=base)])

if os.path.exists(".\\build\\exe.win-amd64-3.8\\downloader.exe"):
    cx_Freeze.util.AddIcon(".\\build\\exe.win-amd64-3.8\\downloader.exe", "icon.ico")