# LMTK creates report about hardware and software in windows, backs up data and displays info about creating installation media
# Copyright (C) 2025 Konstantin Ovchinnikov k@kovchinnikov.info
# This file is part of LMTK, licensed under the GNU GPLv3 or later.
# See the LICENSE file or <https://www.gnu.org/licenses/> for details.

'''
Module: dialog.py
Description: Draws the screens of the UI and calls classes to do the job
'''

import tkinter as tk # UI
from tkinter import ttk, messagebox # UI
import subprocess # execute PowerShell scripts for hardware detection and to list standard folders in home catalog
import threading # to unfreese the UI
from report import Report # a class for step 1 -- get system info
from app_context import AppContext # filenames and other variables
from backup import Backup # a class for step 2 -- define input/output folders and perform backup
from i18n import _

class Dialog():
  """Drawing main program windows"""
  def __init__(self):
    self.context = AppContext()
    self.home()
    self.context.run()
    self.backup = None
    self.report = None

  def is_powershell_installed(self):
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

  def about(self):
    """About message box"""
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
    _("About"),
    _("""Linux Migration Toolkit
Copyright (C) 2025 Konstantin Ovchinnikov k@kovchinnikov.info

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.

Source code: https://github.com/ikostas/lmtk
""")
    )

  def media(self):
    """ Step 3. Prepare installation media """
    title_data = (
      f"LMTK: {_('Let\'s prepare your installation media')}",
      3,
      _("Let's prepare your installation media")
    )
    self.context.gen_title(title_data)

    if self.context.novice_mode:
      guide_content = _("""Here's what you should do next:
1. Download linux ISO and media writer
2. Launch media writer, write ISO to a USB-stick
3. Reboot, enter BIOS/UEFI, set USB-stick as a first boot device and turn off Secure Boot option

I'd recommend the following options for media writers:
- balenaEtcher
- Rufus
- UNetbootin

There's a thorough guide for using Rufus with Ubuntu:
- Ubuntu Wiki\
""")
      links = [
        ("link_etcher", "7.2", "7.14", "https://etcher.balena.io/"),
        ("link_rufus", "8.2", "8.8", "https://rufus.ie/"),
        ("link_unetbootin", "9.2", "9.12", "https://unetbootin.github.io/"),
        ("link_wiki", "12.2", "12.14", "https://ubuntu.com/tutorials/create-a-usb-stick-on-windows"),
        ]

      self.context.gen_guide(guide_content, links)
    else:
      guide_content = _("""You know the drill: write your ISO to a USB stick and boot into a Linux installation. Here are some media writer options:
- balenaEtcher, Rufus, UNetbootin as standard options
- Ventroy to experiment with several ISOs

Have fun!
""")
      links = [
        ("link_etcher", "2.2", "2.14", "https://etcher.balena.io/"),
        ("link_rufus", "2.16", "2.21", "https://rufus.ie/"),
        ("link_unetbootin", "2.23", "2.33", "https://unetbootin.github.io/"),
        ("link_ventroy", "3.2", "3.9", "https://www.ventoy.net/"),
        ]
      self.context.gen_guide(guide_content, links)

    buttons = [
      (_("Back"), self.backup_window),
      (_("Home"), self.home),
    ]
    self.context.gen_bbuttons(buttons)

  def backup_window(self):
    """ Step 2. Backup screen: create tar or tar.bz2 archive """
    title_data = (
      f"LMTK: {_('Let\'s back up your data')}",
      2,
      _("Let's back up your data")
    )
    self.context.gen_title(title_data)

    if self.context.novice_mode:
      self.context.gen_label(_("""Some tips:
1. Use an external drive with enough free space as the destination.
2. You must have read access (as a Windows user) to all folders you want to back up.
3. I've included some default folders, but it's your responsibility to add all folders that contain valuable data.
Bonus tip: All your data in Windows will be erased after installing Linux. :) So make sure you select all source folders with important data.\
"""))
    else:
      self.context.gen_label(_("Choose your folders to back up, and I'll create an archive in destination folder."))

    self.backup = Backup(self.context)

    # reserve frame for tar progress bar
    self.context.progress_frame = ttk.Frame(self.context.root)
    self.context.progress_frame.pack()

    # Create a frame for the destination and compression widgets
    dest_frame = ttk.Frame(self.context.root)
    dest_frame.pack(pady=(10, 0), padx=self.context.padx, anchor="w")

    # 1. destination label
    self.context.destination_label = ttk.Label(dest_frame, text=_("Your current destination folder: ") + self.backup.destination_folder, font=(self.context.font_family, 11))
    self.context.destination_label.pack(pady=0, anchor="w")
    check_var = tk.BooleanVar(value=self.context.compress)

    def update_context(*_):
      self.context.compress = check_var.get()

    check_var.trace_add("write", update_context)
    checkbox = ttk.Checkbutton(dest_frame, text=_("Enable compression"), variable=check_var)
    checkbox.pack(padx=30, anchor="w")

    # 2. button_frame: set destination, add source
    choice_buttons = [
      (_("Set destination"), lambda: self.backup.set_destination(self.context), _("Here you set the folder, where to put your archive")),
      (_("Add source folder"), lambda: self.backup.add_folder(self.context), _("Here you can add folders to the archive"))
    ]
    self.context.gen_choice(choice_buttons)

    # 3. folders from backup
    self.context.gen_label(_("Your source folders for backup - press 'Remove' to remove from the list."))
    self.context.set_source_folder_label()
    self.context.gen_canvas()

    if not self.context.backup_input:
      for i in self.backup.get_default_folders():
        self.backup.add_folder_backend(i, self.context)
    if self.context.backup_input:
      for folder in self.context.backup_input:
        self.backup.display_folder(folder, self.context)

    # 4. bottom buttons
    buttons = [
      (_("Back"), self.get_info),
      (_("Home"), self.home),
      (_("Perform backup"), self.start_backup),
      (_("Next"), self.media)
    ]
    self.context.gen_bbuttons(buttons)

  def start_backup(self):
    """A function to call backup method with context argument"""
    self.backup.start_backup(self.context)

  def get_info(self):
    """ Step 1. Create report re hardware and installed software """
    # Add some text here for novice: what we do, what to do next -- add argument to a function
    title_data = (
      _("Gathering software and hardware info"),
      1,
      _("Let's gather some info about your hardware and software")
    )
    self.context.gen_title(title_data)
    if self.context.novice_mode:
      self.context.gen_label(_("This is a very important step: we save information about your hardware configuration and installed software as HTML and Markdown for future use. Press 'View report' when it's ready — the report includes instructions and some useful links as well."))
    else:
      self.context.gen_label(_("Press 'View report' when it's ready — the report includes the collected information, instructions, and some useful links. A Markdown version is also included."))

    self.context.progress_frame = ttk.Frame(self.context.root)
    self.context.progress_frame.pack(pady=0)

    if not self.context.report_generated:
      self.context.set_report_label(_("Now we are gathering software and hardware info"))
      state = "disabled"
      self.context.start_progress()
      self.report = Report()
      threading.Thread(target=lambda: self.report.get_info_thread(self.context), daemon=True).start()
    else:
      self.context.set_report_label(_("Finished gathering software and hardware info"))
      state = "normal"

    buttons = [
      (_("Back"), self.launch_novice_mode),
      (_("Home"), self.home),
      (_("View report"), self.report.open_report),
      (_("Next"), self.backup_window)
    ]
    self.context.gen_bbuttons(buttons)
    self.context.view_btn.config(state=state)

  def launch_novice_mode(self):
    """ Step 0, for novice mode only -- display some info with links """
    title_data = (
      f"LMTK: {_('Are you familiar with Linux?')}",
      0,
      _("Are you familiar with Linux?")
    )
    self.context.gen_title(title_data)
    guide_content = _("""So, you're going to install Linux. But are you familiar with Linux?

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
""")

    links = [
      ("link_gitForWindows", "4.2", "4.17", "https://git-scm.com/downloads/win"),
      ("link_virtualbox", "5.2", "5.12", "https://www.virtualbox.org/wiki/Downloads"),
      ("link_fedora_gnome", "15.2", "15.8", "https://fedoraproject.org/workstation/download"),
      ("link_fedora_xfce", "16.2", "16.13", "https://fedoraproject.org/spins/xfce/download"),
      ("link_ubuntu_gnome", "17.2", "17.8", "https://ubuntu.com/download/desktop"),
      ("link_ubuntu_xfce", "18.2", "18.13", "https://xubuntu.org/download/"),
      ]

    self.context.gen_guide(guide_content, links)

    # buttons
    buttons = [
      (_("Home"), self.home),
      (_("Next"), self.get_info)
    ]
    self.context.gen_bbuttons(buttons)

  def launch_expert_mode(self):
    """ Set context variable and start with step 1. """
    self.context.novice_mode = False
    self.get_info()

  def home(self):
    """ Display the first screen -- choose the mode """
    self.context.clear_screen()
    self.context.root.title(_("LMTK: Welcome to Linux Migration Toolkit!"))
    self.context.gen_header(_("Welcome to Linux Migration Toolkit! Choose Your Mode"))

    # general info
    self.context.gen_label(_("Welcome to the Linux Migration Toolkit for the desktop! This app gathers information about your installed programs and hardware for future use, helps you back up your data, and assists in preparing installation media using external tools."))

    # buttons
    choice_buttons = [
      (_("Novice Mode"), self.launch_novice_mode, _("For each step you'll have useful guidance and links.\nAlso use it if you use this program for the first time.")),
      (_("Expert Mode"), self.launch_expert_mode, _("You know what the program does."))
    ]
    self.context.gen_choice(choice_buttons)

    # PowerShell check
    text_ps_installed = _("PowerShell is installed. We'll need it to do some stuff.")
    text_ps_not_installed = _("PowerShell is not installed. Please install it and restart the app.")

    if self.is_powershell_installed():
      self.context.gen_label(text_ps_installed)
    else:
      self.context.gen_label(text_ps_not_installed)
      self.context.btn_novice_mode.config(state="disabled")
      self.context.btn_expert_mode.config(state="disabled")
    self.context.gen_label(_("This project is licensed under the GNU General Public License v3.0 or later. Press 'About' for more details."))
    about_button = ttk.Button(self.context.root, text=_("About"), command=self.about)
    about_button.pack(pady=0)
    self.context.quit_button()

    self.context.gen_label(_("Thanks to all the guys and gals in reddit.com/r/linuxsucks/, you're my inspiration."))

dialog = Dialog()
