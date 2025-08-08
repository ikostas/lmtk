# LMTK creates report about hardware and software in windows, backs up data and displays info about creating installation media
# Copyright (C) 2025 Konstantin Ovchinnikov k@kovchinnikov.info
# This file is part of LMTK, licensed under the GNU GPLv3 or later.
# See the LICENSE file or <https://www.gnu.org/licenses/> for details.

import tkinter as tk # UI
from tkinter import ttk, font # UI
import os
import webbrowser # open links in standard browser
from i18n import _

class AppContext():
  def __init__(self):
    self._standard_apps_txt = "installed_standard_apps.txt"
    self._standard_apps_md = "cleaned_standard_apps.md"
    self._store_apps_txt = "installed_store_apps.txt"
    self._store_apps_md = "cleaned_store_apps.md"
    self._hw_report_md = "hardware_info.md"
    self._md_report = "swhw_report.md"
    self._html_report = "swhw_report.html"
    self.backup_input = [] # folders to backup
    self.backup_output = None # where to put a backup
    self.source_size = 0
    self.source_size_human = "0 B"
    self.compress = False
    self.source_size_label = None
    self.report_label = None
    self.error_label = None
    self.novice_mode = True
    self.font_family = "Segoe UI" # A standard, modern Windows font.
    self.padx = 30
    self.root = tk.Tk()
    self.style = ttk.Style(self.root)
    self.style.theme_use('vista')
    self.style.configure('TCheckbutton', font=(self.font_family, 11))
    self.root.configure(bg=self.style.lookup('TFrame', 'background'))
    self.root.geometry("900x800")
    self.root.resizable(True, True)
    self.report_generated = False

  def set_source_folder_label(self):
    # Convert to human-readable format
    text = _("Total source folder size is: ") + self.source_size_human
    if getattr(self, "source_size_label", None):
      self.source_size_label.config(text=text)
    else:
      self.source_size_label = ttk.Label(self.root, text=text, font=(self.font_family, 11))
      self.source_size_label.pack(pady=(10, 0), padx=self.padx, anchor="w")

  def set_report_label(self, text):
    if getattr(self, "report_label", None):
      self.report_label.config(text=text)
    else:
      self.report_label = ttk.Label(self.root, text=text, font=(self.font_family, 12))
      self.report_label.pack(pady=10)

  def run(self):
    self.root.mainloop()

  def start_progress(self):
    self.progress = ttk.Progressbar(self.progress_frame, mode="indeterminate")
    self.progress.pack(pady=10)
    self.progress.start()

  def stop_progress(self):
    self.progress.stop()
    self.progress.pack_forget()
    del self.progress

  def quit_button(self):
    quit_button = ttk.Button(self.root, text=_("Quit"), command=self.root.destroy)
    quit_button.pack(pady=10)

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

  def clear_screen(self):
    """
    Clear root window and empty some labels used
    """
    for widget in self.root.winfo_children():
      widget.destroy()
    self.report_label = None
    self.source_size_label = None

  def gen_header(self, text):
    header_label = ttk.Label(self.root, text=text, font=(self.font_family, 14, "bold"))
    header_label.pack(pady=10) 

  def gen_bbuttons(self, buttons):
    bb_frame = ttk.Frame(self.root)
    bb_frame.pack(pady=10)
    for idx, (label, func) in enumerate(buttons):
      btn = ttk.Button(bb_frame, text=label, width=30, command=lambda f=func: f(self))
      btn.grid(row=0, column=idx, padx=10)
      if label == _("View report"):
        self.view_btn = btn
    self.quit_button()

  def gen_choice(self, buttons):
    choice_frame = ttk.Frame(self.root)
    choice_frame.pack(pady=0, padx=self.padx)
    for idx, (label, func, description) in enumerate(buttons):
      btn = ttk.Button(choice_frame, text=label, width=20, command=lambda f=func: f(self))
      btn.grid(row=idx, column=0, padx=10, pady=5)
      desc = ttk.Label(choice_frame, text=description, justify="left", wraplength=400)
      desc.grid(row=idx, column=1, padx=10, sticky="w")
      if label == _("Novice Mode"):
        self.btn_novice_mode = btn
      elif label == _("Expert Mode"):
        self.btn_expert_mode = btn

  def gen_label(self, label):
    label = ttk.Label(self.root, text=label, font=(self.font_family, 11))
    label.pack(pady=5, padx=self.padx, fill='x')
    def update_wrap(event):
        label.config(wraplength=event.width)
    label.bind('<Configure>', update_wrap)

  def get_status(self, step_index):
    """
    Display current step 
    """
    normal_font = font.Font(family=self.font_family, size=12)
    bold_font = font.Font(family=self.font_family, size=12, weight="bold")
    if self.novice_mode:
      steps = [_("0. Intro"), _("1. Gather Info"), _("2. Backup"), _("3. Prepare Media")]
    else:
      steps = [_("1. Gather Info"), _("2. Backup"), _("3. Prepare Media")]

    status_frame = tk.Frame(self.root)
    status_frame.pack(pady=10, anchor="n")
    for i, step in enumerate(steps):
      lbl_font = bold_font if i == step_index else normal_font
      label = ttk.Label(status_frame, text=step, font=lbl_font)
      label.pack(side="left")

      if i < len(steps) - 1:
        sep = ttk.Label(status_frame, text=" > ", font=normal_font)
        sep.pack(side="left")

  def gen_title(self, data):
    title, status, header = data
    self.root.title(title)
    self.clear_screen()
    self.get_status(status)
    self.gen_header(header)

  def gen_guide(self, guide_content, links):
    text_frame = ttk.Frame(self.root, height=400)
    text_frame.pack(padx=self.padx, pady=10, fill="x")
    text_frame.pack_propagate(False)
    scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")
    text = tk.Text(text_frame, height=25, width=100, wrap="word", font=(self.font_family, 12), bd=0, bg=self.root.cget("bg"), relief="flat", highlightthickness=0, yscrollcommand=scrollbar.set)
    text.pack(side="left", fill="both", expand=True)
    text.insert("1.0", guide_content)
    scrollbar.config(command=text.yview)
    text.tag_config("line_spacing", spacing3=8)  # spacing in pixels
    text.config(state="disabled")

    for tag, start, end, url in links:
      text.tag_add(tag, start, end)
      text.tag_config(tag, foreground="blue")
      text.tag_bind(tag, "<Button-1>", lambda event, url=url: webbrowser.open_new(url))

