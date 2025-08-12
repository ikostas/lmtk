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
import ctypes

def resource_path(relative_path):
  """Get path to resource, whether running as script or bundled with PyInstaller"""
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.abspath(relative_path)

def get_display_language():
  """Get the Windows display/UI language (first in preferred list)"""
  GetUserPreferredUILanguages = ctypes.windll.kernel32.GetUserPreferredUILanguages
  MUI_LANGUAGE_NAME = 0x8
  num_languages = ctypes.c_ulong()
  buffer_size = ctypes.c_ulong()
  GetUserPreferredUILanguages(MUI_LANGUAGE_NAME, ctypes.byref(num_languages), None, ctypes.byref(buffer_size))
  buffer = ctypes.create_unicode_buffer(buffer_size.value)
  GetUserPreferredUILanguages(MUI_LANGUAGE_NAME, ctypes.byref(num_languages), buffer, ctypes.byref(buffer_size))
  return buffer.value.split("-")[0]

locales_path = resource_path("locales")
lang_code = get_display_language()

try:
  translation = gettext.translation('messages', localedir=locales_path, languages=[lang_code])
  _ = translation.gettext
except FileNotFoundError:
  _ = gettext.gettext
