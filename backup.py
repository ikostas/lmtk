from app_context import AppContext
import subprocess # execute PowerShell script for user folder detection
import tkinter as tk # UI
from tkinter import ttk, filedialog 
import os
import threading

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
    self.add_folder_backend(folder, context)

  def add_folder_backend(self, folder, context: AppContext):
    if folder and folder not in context.backup_input:
      folder = os.path.normpath(folder)
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
      self.display_folder(folder_info, context)

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
