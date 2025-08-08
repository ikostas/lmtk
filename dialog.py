# LMTK creates report about hardware and software in windows, backs up data and displays info about creating installation media
# Copyright (C) 2025 Konstantin Ovchinnikov k@kovchinnikov.info
# This file is part of LMTK, licensed under the GNU GPLv3 or later.
# See the LICENSE file or <https://www.gnu.org/licenses/> for details.

import tkinter as tk # UI
from tkinter import ttk, font, filedialog # UI
import subprocess # execute PowerShell scripts for hardware detection and to list standard folders in home catalog
import threading # to unfreese the UI
import os
import webbrowser # open links in standard browser
from report import Report # a class for step 1 -- get system info
from app_context import AppContext # filenames and other variables
from backup import Backup # a class for step 2 -- define input/output folders and perform backup

def is_powershell_installed():
  """
  Check if PowerShell is installed
  All the commands are tested for PS v.5
  """
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

def media(context: AppContext):
  """
  Step 3. Prepare installation media
  """
  title_data = (
    "LMTK: Let's prepare your installation media",
    3,
    "Let's prepare your installation media"
  )
  context.gen_title(title_data)

  if context.novice_mode:
    guide_content = """\
Here's what you should do next:
1. Download linux ISO and media writer
2. Launch media writer, write ISO to a USB-stick
3. Reboot, enter BIOS/UEFI, set USB-stick as a first boot device and turn off Secure Boot option

I'd recommend the following options for media writers:
- balenaEtcher
- Rufus
- UNetbootin

There's a thorough guide for using Rufus with Ubuntu:
- Ubuntu Wiki\
"""
    links = [
      ("link_etcher", "7.2", "7.14", "https://etcher.balena.io/"),
      ("link_rufus", "8.2", "8.8", "https://rufus.ie/"),
      ("link_unetbootin", "9.2", "9.12", "https://unetbootin.github.io/"),
      ("link_wiki", "12.2", "12.14", "https://ubuntu.com/tutorials/create-a-usb-stick-on-windows"),
      ]

    context.gen_guide(guide_content, links)
  else:
    guide_content = """\
You know the drill: write your ISO to a USB stick and boot into a Linux installation. Here are some media writer options:
- balenaEtcher, Rufus, UNetbootin as standard options
- Ventroy to experiment with several ISOs

Have fun!
"""
    links = [
      ("link_etcher", "2.2", "2.14", "https://etcher.balena.io/"),
      ("link_rufus", "2.16", "2.21", "https://rufus.ie/"),
      ("link_unetbootin", "2.23", "2.33", "https://unetbootin.github.io/"),
      ("link_ventroy", "3.2", "3.9", "https://www.ventoy.net/"),
      ]
    context.gen_guide(guide_content, links)

  buttons = [
    ("Back", backup),
    ("Home", home),
  ]
  context.gen_bbuttons(buttons)

def backup(context: AppContext):
  """
  Step 2. Backup screen: create tar or tar.bz2 archive
  """
  title_data = (
    "LMTK: Let's back up your data",
    2,
    "Let's back up your data"
  )
  context.gen_title(title_data)

  if context.novice_mode:
    context.gen_label("""\
Some tips:
1. Use an external drive with enough free space as the destination.
2. You must have read access (as a Windows user) to all folders you want to back up.
3. I've included some default folders, but it's your responsibility to add all folders that contain valuable data.
Bonus tip: All your data in Windows will be erased after installing Linux. :) So make sure you select all source folders with important data.\
    """)
  else:
    context.gen_label("Choose your folders to back up, and I'll create an archive in destination folder.")

  backup = Backup(context)

  # reserve frame for tar progress bar
  context.progress_frame = ttk.Frame(context.root)
  context.progress_frame.pack()

  # Create a frame for the destination and compression widgets
  dest_frame = ttk.Frame(context.root)
  dest_frame.pack(pady=(10, 0), padx=context.padx, anchor="w")

  # 1. destination label
  context.destination_label = ttk.Label(dest_frame, text="Your current destination folder: " + backup.destination_folder, font=("Helvetica", 11))
  context.destination_label.pack(pady=0, anchor="w")
  check_var = tk.BooleanVar(value=context.compress)

  def update_context(*args):
      context.compress = check_var.get()

  check_var.trace_add("write", update_context)
  checkbox = ttk.Checkbutton(dest_frame, text="Enable compression", variable=check_var)
  checkbox.pack(padx=30, anchor="w")

  # 2. button_frame: set destination, add source
  choice_buttons = [
    ("Set destination", backup.set_destination, "Here you set the folder, where to put your archive"),
    ("Add source folder", backup.add_folder, "Here you can add folders to the archive")
  ]
  context.gen_choice(choice_buttons)

  # 3. folders from backup
  context.gen_label("Your source folders for backup - press 'Remove' to remove from the list.")
  context.set_source_folder_label()

  # Create a scrollable area for the folder list
  folder_list_container = ttk.Frame(context.root)
  folder_list_container.pack(fill='x', expand=True, padx=context.padx)
  bg_color = context.style.lookup('TFrame', 'background')
  folder_canvas = tk.Canvas(folder_list_container, width=600, height=200, borderwidth=0, highlightthickness=0, bg=bg_color)
  folder_scrollbar = ttk.Scrollbar(folder_list_container, orient="vertical", command=folder_canvas.yview)
  scrollable_frame = ttk.Frame(folder_canvas)

  scrollable_frame.bind(
      "<Configure>",
      lambda e: folder_canvas.configure(
          scrollregion=folder_canvas.bbox("all")
      )
  )

  folder_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
  folder_canvas.configure(yscrollcommand=folder_scrollbar.set)

  folder_canvas.pack(side="left", fill="both", expand=True)
  folder_scrollbar.pack(side="right", fill="y")

  backup.folder_list_frame = scrollable_frame # Assign the scrollable frame

  if context.backup_input == []:
    for i in backup.get_default_folders():
      backup.add_folder_backend(i, context)
  if context.backup_input:
   for folder in context.backup_input:
     backup.display_folder(folder, context)

  # 4. bottom buttons
  buttons = [
    ("Back", get_info),
    ("Home", home),
    ("Perform backup", backup.start_backup),
    ("Next", media)
  ]
  context.gen_bbuttons(buttons)

def get_info(context: AppContext):
  """
  Step 1. Create report re hardware and installed software
  """
  # Add some text here for novice: what we do, what to do next -- add argument to a function
  title_data = (
    "Gathering software and hardware info",
    1,
    "Let's gather some info about your hardware and software"
  )
  context.gen_title(title_data)
  if context.novice_mode:
    context.gen_label("This is a very important step: we save information about your hardware configuration and installed software as HTML and Markdown for future use. Press 'View report' when it's ready — the report includes instructions and some useful links as well.")
  else:
    context.gen_label("Press 'View report' when it's ready — the report includes the collected information, instructions, and some useful links. A Markdown version is also included.")

  context.progress_frame = ttk.Frame(context.root)
  context.progress_frame.pack(pady=0)

  if not context.report_generated:
    context.set_report_label("Now we are gathering software and hardware info")
    state = "disabled"
    context.start_progress()
    report = Report()
    threading.Thread(target=lambda: report.get_info_thread(context), daemon=True).start()
  else:
    context.set_report_label("Finished gathering software and hardware info")
    state = "normal"

  buttons = [
    ("Back", launch_novice_mode),
    ("Home", home),
    ("View report", open_report),
    ("Next", backup)
  ]
  context.gen_bbuttons(buttons)
  context.view_btn.config(state=state)

def open_report(context):
  webbrowser.open_new(f"file://{os.path.abspath(context.html_report)}")

def launch_novice_mode(context: AppContext):
  """
  Step 0, for novice mode only -- display some info with links
  """
  title_data = (
    "LMTK: Are you familiar with Linux?",
    0,
    "Are you familiar with Linux?"
  )
  context.gen_title(title_data)
  guide_content = """\
So, you're going to install Linux. But are you familiar with Linux?

If not, there are some resources to help you master it without too much risk:
- Git for Windows -- includes bash and core command-line utilities, as well as vim text editor.
- VirtualBox -- you'll be able to install and play with any Linux distribution you like in a sandbox.
- LiveCD -- you'll be able to boot into Linux and at least check if your hardware works.

The most common question is 'What distribution should I use?'
Well, I'd recommend Ubuntu or Fedora to have a pleasant start.

The next question is 'What desktop environment should I use?'
I'd recommend Gnome if you have enough memory or XFCE, if you don't. :)

Here are some links (all of them include LiveCDs, by the way):
- Fedora (Gnome-based)
- Fedora XFCE
- Ubuntu (Gnome-based)
- Ubuntu XFCE

When you click 'Next', we'll gather information about your software and hardware, save it as Markdown (.md) and HTML (.html) reports for future use.\
"""

  links = [
    ("link_gitForWindows", "4.2", "4.17", "https://git-scm.com/downloads/win"),
    ("link_virtualbox", "5.2", "5.12", "https://www.virtualbox.org/wiki/Downloads"),
    ("link_fedora_gnome", "15.2", "15.22", "https://fedoraproject.org/workstation/download"),
    ("link_fedora_xfce", "16.2", "16.13", "https://fedoraproject.org/spins/xfce/download"),
    ("link_ubuntu_gnome", "17.2", "17.23", "https://ubuntu.com/download/desktop"),
    ("link_ubuntu_xfce", "18.2", "18.13", "https://xubuntu.org/download/"),
    ]

  context.gen_guide(guide_content, links)

  # buttons
  buttons = [
    ("Home", home),
    ("Next", get_info)
  ]
  context.gen_bbuttons(buttons)

def launch_expert_mode(context: AppContext):
  """
  Set context variable and start with step 1.
  """
  context.novice_mode = False
  get_info(context)

def home(context: AppContext):
  """
  Display the first screen -- choose the mode
  """
  context.clear_screen()
  context.root.title("LMTK: Welcome to Linux Migration Toolkit!")
  context.gen_header("Welcome to Linux Migration Toolkit! Choose Your Mode")

  # general info
  context.gen_label("Welcome to the Linux Migration Toolkit for the desktop! This app gathers information about your installed programs and hardware for future use, helps you back up your data, and assists in preparing installation media using external tools.")

  # buttons
  choice_buttons = [
    ("Novice Mode", launch_novice_mode, "For each step you'll have useful guidance and links.\nAlso use it if you use this program for the first time."),
    ("Expert Mode", launch_expert_mode, "You know what the program does.")
  ]
  context.gen_choice(choice_buttons)

  # PowerShell check
  text_ps_installed = "PowerShell is installed. We'll need it to do some stuff."
  text_ps_not_installed = "PowerShell is not installed. Please install it and restart the app."

  if is_powershell_installed():
    context.gen_label(text_ps_installed)
  else:
    context.gen_label(text_ps_not_installed)
    context.btn_novice_mode.config(state="disabled")
    context.btn_expert_mode.config(state="disabled")

  context.quit_button()

  context.gen_label("Thanks to all the guys and gals in reddit.com/r/linuxsucks/, you're my inspiration.")

context = AppContext()
home(context)
context.run()
