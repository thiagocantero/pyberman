import os
from distutils.core import setup
import glob
import py2exe
from modulefinder import Module
import pygame

origIsSystemDLL = py2exe.build_exe.isSystemDLL # save the orginal before we edit it
def isSystemDLL(pathname):
    # checks if the freetype and ogg dll files are being included
    if os.path.basename(pathname).lower() in ("libfreetype-6.dll", "libogg-0.dll", "sdl_ttf.dll"):
            return 0
    return origIsSystemDLL(pathname) # return the orginal function
py2exe.build_exe.isSystemDLL = isSystemDLL # override the default function with this one

setup(
    windows=({'script': 'pyberman.py', 'icon_resources': [(0, 'icon.ico')], 'copyright': 'PyTeam'}, ),
    options = {'py2exe': {
        'packages': ['pygame._view', 'pygame.font'],
        'excludes': ("_ssl","bz2"),
        }
    },
    data_files = [
        #'Data', glob.glob(r'Data\*.*')), # Need to include recursivelly here
        ('Maps', glob.glob(r'Maps\*.bff')),
    ]
)