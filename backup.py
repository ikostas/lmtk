from app_context import AppContext

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
    if folder and folder not in context.backup_input:
      context.backup_input.append(folder)
      self.display_folder(folder)

  def set_destination(self, destination_label, context: AppContext):
    folder = filedialog.askdirectory()
    if folder: 
      context.backup_output = folder
      destination_label.config(text=folder)

  def display_folder(self, folder, context: AppContext):
    frame = ttk.Frame(self.folder_list_frame)
    frame.pack(fill="x", pady=2)
    label = ttk.Label(frame, text=folder)
    label.pack(side="left", fill="x", expand=True)
    remove_btn = ttk.Button(frame, text="Remove", width=7, command=lambda f=folder, fr=frame: self.remove_folder(f, fr, context))
    remove_btn.pack(side="right")

  def remove_folder(self, folder, frame, context: AppContext):
    if folder in self.folders:
      context.backup_input.remove(folder)
      frame.destroy()

