#!/bin/bash
set -e

chroot /mnt/sd_rootfs python3 - << 'EOF'
import sys
import os
sys.path.insert(0, '/home/pi/rf-kit-gui_v200')
os.chdir('/home/pi/rf-kit-gui_v200')

print("[*] Testing all imports required by main.py...")
import tkinter
from tkinter import ttk, Tk, FALSE
from canBus.canConnectorFactory import CanConnectorFactory
from config import Config
from cursorSetting import CursorSetting
from customlogging import log, log_exc
from data import Data, ControllerVersionException
from dimensions import DIMENSIONS
from displaySetting import DisplaySetting
from interface import InterfaceWrapper
from localUpdateScreen import LocalUpdateScreen
from main_screen.operating_buttons import OperatingButtons
from main_screen.scale import NeedleScale, BarScale, Scale
from main_screen.status import StatusBar
from main_screen.tuners import NoTuner, Tuner, ManualTuner
from menu.menu import Menu
from operationalInterface import OperationalInterfaceControl
from rest_server.restServer import RestServerSupport
from restartScreen import RestartScreen, RestartMessage
from scaleTypeSetting import ScaleTypeSetting
from sleepTimer import SleepTimer
from themes import initThemes, useDarkTheme, useMenuTheme
from updateInProgress import UpdateInProgress
from migration.migrator import migrate
from migration.restartNecessity import RestartNecessity
from migration.desktopStartScript import DESKTOP_START_SCRIPT_PATH

print("[+] ALL IMPORTS AND SYMBOLS LOADED 100% CLEANLY!")
EOF
