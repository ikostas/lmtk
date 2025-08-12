# LMTK creates report about hardware and software in windows, backs up data and displays info about creating installation media
# Copyright (C) 2025 Konstantin Ovchinnikov k@kovchinnikov.info
# This file is part of LMTK, licensed under the GNU GPLv3 or later.
# See the LICENSE file or <https://www.gnu.org/licenses/> for details.

'''
Module: report_defaults.py
Description: Stores default report filenames
'''

class ReportDefaults():
  """A class to store default report filenames"""
  def __init__(self):
    """Initialize default values"""
    self._report_files = {
      "standard_apps_txt": "installed_standard_apps.txt",
      "standard_apps_md": "cleaned_standard_apps.md",
      "store_apps_txt": "installed_store_apps.txt",
      "store_apps_md": "cleaned_store_apps.md",
      "hw_report_md": "hardware_info.md",
      "md_report": "swhw_report.md",
      "html_report": "swhw_report.html",
    }
    for key in self._report_files:
      setattr(self.__class__, key, property(lambda self, k=key: self._report_files[k]))
