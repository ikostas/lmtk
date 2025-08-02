import os
import threading
import pythoncom
import markdown
import tkinter as tk
from tkinter import ttk
import webbrowser
import subprocess
import re
import wmi
from datetime import datetime

def open_git(event, link):
  webbrowser.open_new(link)

def markdown_to_html():
  md_file="swhw_report.md"
  html_file="swhw_report.html"
  # Read markdown content
  with open(md_file, "r", encoding="utf-8") as f:
    text = f.read()

  # Convert to HTML
  html = markdown.markdown(text, extensions=["fenced_code", "tables"])

  # Wrap in basic HTML boilerplate
  full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Linux Migration Toolkit Report</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>
<body>
<main class="container">
{html}
</main>
</body>
</html>
"""

  # Write HTML file
  with open(html_file, "w", encoding="utf-8") as f:
    f.write(full_html)

  # Open in default browser
  # webbrowser.open(f"file://{os.path.abspath(html_file)}")

def get_hwsw_report():
  file1 = "cleaned_standard_apps.md"
  file2 = "cleaned_store_apps.md"
  file3 = "hardware_info.md"
  output_file = "swhw_report.md"
  # Titles
  main_title = "# Linux Migration Toolkit Report"
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  sections = [
    ("## Standard Applications", file1),
    ("## Microsoft Store Applications", file2),
    ("## Hardware Information", file3),
]

  # Combine files into one markdown report
  with open(output_file, "w", encoding="utf-8") as out:
    out.write(f"{main_title}\n")
    out.write(f"\n*Generated on {timestamp}*\n\n")

    for header, filename in sections:
      out.write(f"{header}\n\n")
      with open(filename, "r", encoding="utf-8") as f:
        out.write(f.read().strip() + "\n\n")

  # Remove original files
  for _, filename in sections:
    try:
      os.remove(filename)
    except OSError as e:
      print(f"Error deleting {filename}: {e}")

def get_hw_info():
  filename="hardware_info.md"
  pythoncom.CoInitialize()
  try:
    c = wmi.WMI()
    lines = []

    # CPU info
    cpus = c.Win32_Processor()
    lines.append("### CPU:\n")
    for cpu in cpus:
      lines.append(f"- Name: {cpu.Name}")
      lines.append(f"- Number of Cores: {cpu.NumberOfCores}")

    # RAM info (in GB)
    system_info = c.Win32_ComputerSystem()[0]
    total_ram_bytes = int(system_info.TotalPhysicalMemory)
    total_ram_gb = total_ram_bytes / (1024 ** 3)
    lines.append(f"\n### RAM:\n\n- {total_ram_gb:.2f} GB")

    # Drives info
    drives = c.Win32_LogicalDisk(DriveType=3)  # local disks only
    lines.append("\n### Drives:\n")
    for drive in drives:
      size_gb = int(drive.Size) / (1024 ** 3) if drive.Size else 0
      free_gb = int(drive.FreeSpace) / (1024 ** 3) if drive.FreeSpace else 0
      lines.append(f"- {drive.DeviceID} - Size: {size_gb:.2f} GB, Free: {free_gb:.2f} GB")

    # GPU info
    gpus = c.Win32_VideoController()
    lines.append("\n### GPU:\n")
    for gpu in gpus:
      lines.append(f"- {gpu.Name}")
    lines.append("")

    # Network adapters (physical and enabled)
    net_adapters = [n for n in c.Win32_NetworkAdapter() if n.PhysicalAdapter and n.NetEnabled]
    lines.append("\n### Network Adapters:\n")
    for net in net_adapters:
      lines.append(f"- Name: {net.Name}, Connection ID: {net.NetConnectionID}, Type: {net.AdapterType}")

    # Printers info
    printers = c.Win32_Printer()
    lines.append("\n### Printers:\n")
    for printer in printers:
      lines.append(f"- Name: {printer.Name}, Port: {printer.PortName}")

    # Write all lines to file
    with open(filename, "w", encoding="utf-8") as f:
      f.write("\n".join(lines))
    
    # Generate combined report and remove partial reports
    get_hwsw_report()

  finally:
    pythoncom.CoUninitialize()

  # generate html report
  markdown_to_html()

def clean_standardapps():
  input_file = "installed_standard_apps.txt"
  output_file = "cleaned_standard_apps.md"
  cleaned_names = set() # to remove duplicates

  with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()[3:]  # Skip first 3 lines (headers)
    for line in lines:
      line = line.strip()
      if not line:
        continue  # Skip empty lines
      if "driver" in line.lower():
        continue  # Skip lines containing "driver" (case-insensitive)
      line = re.sub(r"\s+\S+$", "", line)
      line = "- " + line
      cleaned_names.add(line)

  # Sort and write to file
  with open(output_file, "w", encoding="utf-8") as f:
    for name in sorted(cleaned_names):
      f.write(name + "\n")

  # Remove input file - txt
  try:
    os.remove(input_file)
  except OSError as e:
    print(f"Error deleting {input_file}: {e}")

def clean_storeapps():
  # Input and output file paths
  input_file = "installed_store_apps.txt"
  output_file = "cleaned_store_apps.md"

  # Regex to detect GUID-like lines
  guid_pattern = re.compile(r"^[0-9a-fA-F\-]{36}$")

  # Set to collect unique cleaned names
  cleaned_names = set() # to remove duplicates

  # Prefixes to strip
  prefixes = [
    "MicrosoftWindows.",
    "Microsoft.Windows.",
    "Microsoft.",
    "MicrosoftCorporationII."
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
      line = "- " + line
      cleaned_names.add(line)

  # Sort alphabetically
  sorted_names = sorted(cleaned_names)

  # Write result
  with open(output_file, "w", encoding="utf-8") as f:
    for name in sorted_names:
      f.write(name + "\n")

  # Remove input file - txt
  try:
    os.remove(input_file)
  except OSError as e:
    print(f"Error deleting {input_file}: {e}")

def get_info_thread():
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
  get_hw_info() # get hardware info in markdown format
  root.after(0, finish_get_info)

def finish_get_info():
  # After work
  progress.stop()
  progress.pack_forget()
  title_label = ttk.Label(root, text="Finished gathering software and hardware info", font=("Helvetica", 16, "bold"))
  title_label.pack(pady=20)

def get_info():
  root.title("Gathering software and hardware info")
  clear_screen()
  title_label = ttk.Label(root, text="Now we are gathering software and hardware info", font=("Helvetica", 16, "bold"))
  title_label.pack(pady=20)

  global progress 
  progress = ttk.Progressbar(root, mode="indeterminate")
  progress.pack()
  progress.start()
  threading.Thread(target=get_info_thread, daemon=True).start()

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

