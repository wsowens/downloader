"""
Freeze downloader.py and its dependencies into cross-platform executables
"""
import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name = "ez downloader",
      version = "0.1",
      description = " Simple GUI wrapper around youtube-dl",
      executables = [Executable("downloader.py", base=base)])
