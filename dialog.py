import tkinter as tk
from tkinter import ttk
import webbrowser
import subprocess
import re
import wmi

def open_git(event, link):
  webbrowser.open_new(link)

def get_hw_info():
  filename="hardware_summary.txt"
  c = wmi.WMI()
  lines = []

  # CPU info
  cpus = c.Win32_Processor()
  lines.append("CPU:")
  for cpu in cpus:
    lines.append(f"  Name: {cpu.Name}")
    lines.append(f"  Number of Cores: {cpu.NumberOfCores}")
  lines.append("")

  # RAM info (in GB)
  memories = c.Win32_PhysicalMemory()
  total_ram_bytes = sum(int(mem.Capacity) for mem in memories)
  total_ram_gb = total_ram_bytes / (1024 ** 3)
  lines.append(f"RAM: {total_ram_gb:.2f} GB")
  lines.append("")

  # Drives info
  drives = c.Win32_LogicalDisk(DriveType=3)  # local disks only
  lines.append("Drives:")
  for drive in drives:
    size_gb = int(drive.Size) / (1024 ** 3) if drive.Size else 0
    free_gb = int(drive.FreeSpace) / (1024 ** 3) if drive.FreeSpace else 0
    lines.append(f"  {drive.DeviceID} - Size: {size_gb:.2f} GB, Free: {free_gb:.2f} GB")
  lines.append("")

  # GPU info
  gpus = c.Win32_VideoController()
  lines.append("GPU:")
  for gpu in gpus:
    lines.append(f"  {gpu.Name}")
  lines.append("")

  # Network adapters (physical and enabled)
  net_adapters = [n for n in c.Win32_NetworkAdapter() if n.PhysicalAdapter and n.NetEnabled]
  lines.append("Network Adapters:")
  for net in net_adapters:
    lines.append(f"  Name: {net.Name}, Connection ID: {net.NetConnectionID}, Type: {net.AdapterType}")
  lines.append("")

  # Printers info
  printers = c.Win32_Printer()
  lines.append("Printers:")
  for printer in printers:
    lines.append(f"  Name: {printer.Name}, Port: {printer.PortName}")
  lines.append("")

  # Write all lines to file
  with open(filename, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

def clean_standardapps():
  input_file = "installed_standard_apps.txt"
  output_file = "cleaned_standard_apps.txt"
  cleaned_names = set() # to remove duplicates

  with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()[3:]  # Skip first 3 lines (headers)
    for line in lines:
      line = line.strip()
      if not line:
        continue  # Skip empty lines
      if "driver" in line.lower():
        continue  # Skip lines containing "driver" (case-insensitive)
      cleaned_names.add(line)

  # Sort and write to file
  with open(output_file, "w", encoding="utf-8") as f:
    for name in sorted(cleaned_names):
      f.write(name + "\n")

def clean_storeapps():
  # Input and output file paths
  input_file = "installed_store_apps.txt"
  output_file = "cleaned_store_apps.txt"

  # Regex to detect GUID-like lines
  guid_pattern = re.compile(r"^[0-9a-fA-F\-]{36}$")

  # Set to collect unique cleaned names
  cleaned_names = set() # to remove duplicates

  # Prefixes to strip
  prefixes = [
    "MicrosoftWindows.",
    "Microsoft.Windows.",
    "Microsoft.",
    ]

  with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()[3:]
    for line in lines:
      line = line.strip()
      if not line:
        continue  # skip empty lines
      if guid_pattern.match(line):
        continue  # skip GUIDs
      for prefix in prefixes:
        if line.startswith(prefix):
          line = line[len(prefix):]
          break  # strip only one prefix at most
      cleaned_names.add(line)

  # Sort alphabetically
  sorted_names = sorted(cleaned_names)

  # Write result
  with open(output_file, "w", encoding="utf-8") as f:
    for name in sorted_names:
      f.write(name + "\n")

def get_info():
# PowerShell command
  command_storeapps = 'Get-AppxPackage | Select-Object Name'

# Run the command
  result = subprocess.run(
    ["powershell", "-Command", command_storeapps],
    capture_output=True,
    text=True
  )
  with open("installed_store_apps.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)
  if result.stderr:
    print("PowerShell error:\n", result.stderr)
  clean_storeapps() # remove dups, empty lines, etc.

  command_standardapps = """
Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,
                  HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
    Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
    Where-Object { $_.DisplayName } |
    Sort-Object DisplayName
"""
  result = subprocess.run(
    ["powershell", "-Command", command_standardapps],
    capture_output=True,
    text=True
  )
  with open("installed_standard_apps.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)
  if result.stderr:
    print("PowerShell error:\n", result.stderr)

  clean_standardapps() # remove dups, empty lines, etc.
  get_hw_info()

def clear_screen():
  for widget in root.winfo_children():
    widget.destroy()

def launch_novice_mode():
  clear_screen()
  root.title("LMTK: Are you familiar with Linux?")

#    guide_text = tk.Text(root, height=25, width=100, wrap="word", font=("Helvetica", 11))
#    guitext.pack(padx=20, pady=20)

  guide_content = """\
So, you're going to install Linux. But are you familiar with Linux?

If not, there are some resources to help you master it without too much risk:
- Git for Windows -- includes bash and core command-line utilities, as well as vim text editor.
- VirtualBox -- you'll be able to install and play any Linux distribution you like in a sandbox.
- LiveCD -- you'll be able to boot into Linux and at least check if your hardware works.

The most common question you get , is 'What distribution should I use?'
Well, I recommend Ubuntu or Fedora to have a pleasant start.

The next question is 'What desktop environment should I use?'
I recommend Gnome if you have enough memory or XFCE, if you don't. :)

Here are some links (all of them are LiveCDs, by the way):
- Fedora (Gnome-based)
- Fedora XFCE
- Ubuntu (Gnome-based)
- Ubuntu XFCE
"""
  text = tk.Text(root, height=25, width=100, wrap="word", font=("Helvetica", 11), bd=0, bg=root.cget("bg"), relief="flat", highlightthickness=0)
  text.insert("1.0", guide_content)
  text.tag_config("line_spacing", spacing3=6)  # spacing in pixels
  text.tag_add("line_spacing", "1.0", "end")
  text.config(state="disabled")
  text.pack(padx=20, pady=20)

  links = [
    ("link_gitForWindows", "4.2", "4.17", "https://git-scm.com/downloads/win"),
    ("link_virtualbox", "5.2", "5.12", "https://www.virtualbox.org/wiki/Downloads"),
    ("link_fedora_gnome", "15.2", "15.22", "https://fedoraproject.org/workstation/download"),
    ("link_fedora_xfce", "16.2", "16.13", "https://fedoraproject.org/spins/xfce/download"),
    ("link_ubuntu_gnome", "17.2", "17.23", "https://ubuntu.com/download/desktop"),
    ("link_ubuntu_xfce", "18.2", "18.13", "https://xubuntu.org/download/"),
    ]

  for tag, start, end, url in links:
    text.tag_add(tag, start, end)
    text.tag_config(tag, foreground="blue")
    text.tag_bind(tag, "<Button-1>", lambda event, url=url: open_git(event, url))

  text.config(state=tk.DISABLED)

  # buttons
  frame = ttk.Frame(root)
  frame.pack(pady=10)
  home_btn = ttk.Button(frame, text="Home", width=20, command=home)
  home_btn.grid(row=0, column=0, padx=10, pady=5, sticky="w")
  next_btn = ttk.Button(frame, text="Next", width=20, command=get_info)
  next_btn.grid(row=0, column=1, padx=10, pady=5, sticky="e")
  quit_button = ttk.Button(root, text="Quit", command=root.destroy)
  quit_button.pack(pady=10)

def launch_expert_mode():
  print("Expert Mode selected")
    # Put your logic here

def is_powershell_installed():
  try:
    subprocess.run(
        ["powershell", "-Command", "Write-Output 'OK'"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
        )
    return True
  except (FileNotFoundError, subprocess.CalledProcessError):
    return False

def main():
  global root, novice_btn, expert_btn
  root = tk.Tk()
  root.geometry("800x600")
  root.resizable(False, False)
  home()
  root.mainloop()

def home():
  clear_screen()
  root.title("Welcome to Linux Migration Toolkit!")

  title_label = ttk.Label(root, text="Welcome to Linux Migration Toolkit! Choose Your Mode", font=("Helvetica", 16, "bold"))
  title_label.pack(pady=20)

  # general info
  text_intro = "Welcome to the Linux Migration Toolkit for the desktop! This app gathers information about your installed programs and hardware for future use, helps you back up your data, and assists in preparing installation media using external tools."
  intro_text = ttk.Label(root, text=text_intro, wraplength=600, justify="left")
  intro_text.pack(padx=20, pady=20)

  # buttons
  frame = ttk.Frame(root)
  frame.pack(pady=10)
  novice_btn = ttk.Button(frame, text="Novice Mode", width=20, command=launch_novice_mode)
  novice_btn.grid(row=0, column=0, padx=10, pady=5, sticky="n")
  novice_desc = ttk.Label(frame, text="For each step you'll have useful guidance and links.\nAlso use it if you use this program for the first time.", justify="left", wraplength=400)
  novice_desc.grid(row=0, column=1, padx=10, sticky="w")

  expert_btn = ttk.Button(frame, text="Expert Mode", width=20, command=launch_expert_mode)
  expert_btn.grid(row=1, column=0, padx=10, pady=5, sticky="n")
  expert_desc = ttk.Label(frame, text="You know what the program does.", justify="left", wraplength=400)
  expert_desc.grid(row=1, column=1, padx=10, sticky="w")

  # PowerShell check
  text_ps_installed = "PowerShell is installed. We'll need it to do some stuff."
  text_ps_not_installed = "PowerShell is not installed. Please install it and restart the app."

  if is_powershell_installed():
    ps_text = ttk.Label(root, text=text_ps_installed, wraplength=600, justify="left")
    ps_text.pack(padx=20, pady=20)
  else:
    ps_text = ttk.Label(root, text=text_ps_not_installed, wraplength=600, justify="left")
    ps_text.pack(padx=20, pady=20)
    novice_btn.config(state="disabled")
    expert_btn.config(state="disabled")

  quit_button = ttk.Button(root, text="Quit", command=root.destroy)
  quit_button.pack(pady=10)

  reddit_text = ttk.Label(root, text="Thanks to all the guys and gals in reddit.com/r/linuxsucks/, you're my inspiration.", wraplength=600, justify="left")
  reddit_text.pack(padx=20, pady=20)

main()

