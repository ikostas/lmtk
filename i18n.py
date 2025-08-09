# LMTK creates report about hardware and software in windows, backs up data and displays info about creating installation media
# Copyright (C) 2025 Konstantin Ovchinnikov k@kovchinnikov.info
# This file is part of LMTK, licensed under the GNU GPLv3 or later.
# See the LICENSE file or <https://www.gnu.org/licenses/> for details.

'''
Module: i18n.py
Description: Define local and load localization, define localization object used by other modules
'''

import gettext
import locale
import os
import sys

def resource_path(relative_path):
  """Get path to resource, whether running as script or bundled with PyInstaller"""
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.abspath(relative_path)

locales_path = resource_path("locales")
lang = locale.getlocale()[0]

try:
  translation = gettext.translation('messages', localedir=locales_path, languages=[lang])
  _ = translation.gettext
except FileNotFoundError:
  _ = gettext.gettext
