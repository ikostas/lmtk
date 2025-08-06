import tkinter as tk # UI
from tkinter import ttk, font # UI
import os

class AppContext():
  def __init__(self):
    self._root = tk.Tk()
    self._root.geometry("900x800")
    self._root.resizable(True, True)
    self._standard_apps_txt = "installed_standard_apps.txt"
    self._standard_apps_md = "cleaned_standard_apps.md"
    self._store_apps_txt = "installed_store_apps.txt"
    self._store_apps_md = "cleaned_store_apps.md"
    self._hw_report_md = "hardware_info.md"
    self._md_report = "swhw_report.md"
    self._html_report = "swhw_report.html"
    self._backup_input = [] # folders to backup
    self._backup_output = None # where to put a backup
    self.source_size = 0
    self.source_size_human = "0 B"
    self.view_button = None
    self.compress = True

  def set_source_folder_label(self):
    # change this to human-readable
    text = "Total source folder size is: " + self.source_size_human
    if hasattr(self, "_source_size_label"):
      self._source_size_label.config(text=text)
    else:
      self._source_size_label = ttk.Label(self.root, text=text)
      self._source_size_label.pack(pady=10)

  def set_report_label(self, text):
    if hasattr(self, "_report_label"):
      self._report_label.config(text=text)
    else:
      self._report_label = ttk.Label(self.root, text=text, font=("Helvetica", 12))
      self._report_label.pack(pady=10)

  def run(self):
    self._root.mainloop()

  def start_progress(self):
    self.progress = ttk.Progressbar(self._root, mode="indeterminate")
    self.progress.pack()
    self.progress.start()

  def stop_progress(self):
    self.progress.stop()
    self.progress.pack_forget()

  def set_root_title(self, title):
    self._root.title(title)

  def quit_button(self):
    quit_button = ttk.Button(self.root, text="Quit", command=self.root.destroy)
    quit_button.pack(pady=10)

  @property
  def backup_input(self):
    return self._backup_input

  @property
  def backup_output(self):
    return self._backup_output

  @backup_output.setter
  def backup_output(self, value):
    self._backup_output = value

  @property
  def root(self):
    return self._root

  @property
  def standard_apps_txt(self):
    return self._standard_apps_txt 

  @property
  def standard_apps_md(self):
    return self._standard_apps_md
  
  @property
  def store_apps_txt(self):
    return self._store_apps_txt

  @property
  def store_apps_md(self):
    return self._store_apps_md

  @property
  def hw_report_md(self):
    return self._hw_report_md
  
  @property
  def md_report(self):
    return self._md_report

  @property
  def html_report(self):
    return self._html_report

