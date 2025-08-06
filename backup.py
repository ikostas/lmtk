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
    if folder and not any(f["path"] == folder for f in context.backup_input):
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

  def set_destination(self, destination_label, context: AppContext):
    folder = filedialog.askdirectory()
    if folder: 
      folder = os.path.normpath(folder)
      context.backup_output = folder
      destination_label.config(text="Your current destination folder: " + folder)

  def display_folder(self, folder, context: AppContext):
    frame = ttk.Frame(self.folder_list_frame)
    frame.pack(pady=2,padx=30, anchor="w")
    label = ttk.Label(frame, text=f"{folder['path']} ({folder['size_human']})", anchor="w", justify="left")
    label.grid(row=0, column=0, sticky="w")

    remove_btn = ttk.Button(frame, text="Remove", width=10,
      command=lambda: self.remove_folder(folder, frame, context))
    remove_btn.grid(row=0, column=1, sticky="w")

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
    context.start_progress()
    threading.Thread(target=lambda: self.create_tar_archive(context), daemon=True).start()

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
    finished_label = ttk.Label(context.progress_frame, text="Backup complete", font=("Helvetica", 12))
    finished_label.pack()

