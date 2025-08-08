# LMTK: Linux Migration Toolkit
# Copyright (C) 2025 Konstantin Ovchinnikov <k@kovchinnikov.info>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from app_context import AppContext
import subprocess # execute PowerShell script for user folder detection
import tkinter as tk # UI
from tkinter import ttk, filedialog 
import os
import threading
import tarfile
import datetime
import logging

class Backup():
  def __init__(self, context: AppContext):
    self.folder_list_frame = ttk.Frame(context.root)
    self.folder_list_frame.pack(padx=10, pady=10)
    if context.backup_output == None:
      self.destination_folder = "No folder selected" 
    else:
      self.destination_folder = context.backup_output

  def get_default_folders(self):
    ps_script = r'''
    $folders = @(
      [Environment]::GetFolderPath("MyDocuments")
      [Environment]::GetFolderPath("MyPictures")
      [Environment]::GetFolderPath("MyMusic")
      [Environment]::GetFolderPath("MyVideos")
      [Environment]::GetFolderPath("Desktop")
      (Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders').'{374DE290-123F-4565-9164-39C4925E467B}'
    )
    $folders -join "`n"
    '''

    result = subprocess.run(
      ["powershell", "-NoProfile", "-Command", ps_script],
      capture_output=True,
      text=True,
      check=True
    )
    return result.stdout.strip().splitlines()

  def add_folder(self, context: AppContext):
    folder = filedialog.askdirectory()
    folder = os.path.normpath(folder)
    if folder and folder != "." and not any(f["path"] == folder for f in context.backup_input):
      self.add_folder_backend(folder, context)
      self.display_folder(context.backup_input[-1], context)

  def add_folder_backend(self, folder, context: AppContext):
    folder_size = self.get_folder_size(folder)
    folder_info = {
      "path": folder,
      "size_bytes": folder_size,
      "size_human": self.get_size_hr(folder_size)
      }
    context.backup_input.append(folder_info)
    context.source_size += folder_size
    context.source_size_human = self.get_size_hr(context.source_size)
    context.set_source_folder_label()

  def set_destination(self, context: AppContext):
    folder = filedialog.askdirectory()
    folder = os.path.normpath(folder)
    if folder and folder != "." and not any(f["path"] == folder for f in context.backup_input):
      context.backup_output = folder
      context.destination_label.config(text="Your current destination folder: " + folder)

  def display_folder(self, folder, context: AppContext):
    frame = ttk.Frame(self.folder_list_frame)
    frame.pack(pady=2,padx=context.padx, anchor="w", fill="x")
    frame.columnconfigure(0, weight=1)
    label = ttk.Label(frame, text=f"{folder['path']} ({folder['size_human']})", anchor="w", justify="left")
    label.grid(row=0, column=0, sticky="w")

    remove_btn = ttk.Button(frame, text="Remove", width=10,
      command=lambda: self.remove_folder(folder, frame, context))
    remove_btn.grid(row=0, column=1, sticky="e")

  def remove_folder(self, folder, frame, context: AppContext):
    if folder in context.backup_input:
      context.source_size -= folder['size_bytes'] 
      context.source_size_human = self.get_size_hr(context.source_size)
      context.backup_input.remove(folder)
      context.set_source_folder_label()
      frame.destroy()

  def get_folder_size(self, path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
      for f in filenames:
        try:
          fp = os.path.join(dirpath, f)
          total += os.path.getsize(fp)
        except OSError:
          pass
    return total

  def get_size_hr(self, total):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
      if total < 1024:
        return f"{total:.1f} {unit}"
      total /= 1024
    return f"{total:.1f} PB"

  def start_backup(self, context: AppContext):
    if getattr(context, "error_label", None):
      context.error_label.destroy()
      context.error_label = None
    error_code = self.validate_backup_paths(context)
    if error_code == 0:
      context.start_progress()
      threading.Thread(target=lambda: self.create_tar_archive(context), daemon=True).start()
    else:
      error_arr = [
        "OK",
        "No source folders selected",
        "No destination folder selected",
        "Destination is one of the input folders",
        "One input folder is a subfolder of another input folder",
        "Output is inside one of the input folders (cyclic backup)",
      ]
      text = "Error: " + error_arr[error_code]
      if getattr(context, "error_label", None):
        context.error_label.config(text=text)
      else:
        context.error_label = ttk.Label(context.progress_frame, text=text, font=(context.font_family, 12)) 
        context.error_label.pack()

  def create_tar_archive(self, context: AppContext):
    if context.compress:
      mode = "w:bz2"
      extension = "tar.bz2"
    else:
      mode = "w"
      extension = "tar"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(context.backup_output, f"backup_{timestamp}.{extension}")
    log_filename = f"log_{timestamp}.txt"
    log_path = os.path.join(context.backup_output, log_filename)

    logging.basicConfig(
      filename=log_path,
      level=logging.INFO,
      format='%(asctime)s - %(levelname)s - %(message)s',
      filemode='w'  # overwrite if re-run
    )

    with tarfile.open(output_path, mode) as tar:
      for folder_info in context.backup_input:
        base_path = os.path.normpath(folder_info["path"])
        arcname = os.path.basename(base_path.rstrip("\\/"))

        try:
          tar.add(base_path, arcname=arcname)
        except (PermissionError, FileNotFoundError) as e:
          logging.error(f"Skipping {base_path}: {e}")

    context.root.after(0, lambda: self.after_backup(context))

  def after_backup(self, context: AppContext):
    context.stop_progress()
    finished_label = ttk.Label(context.progress_frame, text="Backup complete, see log file for details", font=("Helvetica", 12))
    finished_label.pack()

  def validate_backup_paths(self, context):
    input_paths = [(folder["path"]) for folder in context.backup_input]
    output_path = context.backup_output if context.backup_output else None
    # 1. No source folders selected
    if not input_paths:
      return 1

    # 2. No destination folder selected
    if not output_path:
      return 2

    # 3. Output is one of the input folders
    if output_path in input_paths:
      return 3

    # 4. One input folder is a subfolder of another input folder
    for i, path1 in enumerate(input_paths):
      for j, path2 in enumerate(input_paths):
        if i != j and path1.startswith(path2 + os.sep):
          return 4

    # 5. Output is inside one of the input folders (cyclic backup)
    for source in input_paths:
      if output_path.startswith(source + os.sep):
        return 5 

    return 0
