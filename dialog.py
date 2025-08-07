import tkinter as tk # UI
import os # open saved report 
from tkinter import ttk, font, filedialog # UI
import webbrowser # open links in standard browser
import subprocess # execute PowerShell scripts for hardware detection and to list standard folders in home catalog
import threading # to unfreese the UI
from report import Report # a class for step 1 -- get system info
from app_context import AppContext # filenames and other variables
from backup import Backup # define input/output folders and perform backup

# On the top we have service functions
# All the other function are steps
# some steps have novice mode, the mode is in context 

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

def open_report(context: AppContext):
  webbrowser.open_new(f"file://{os.path.abspath(context.html_report)}")

def get_status(step_index, context: AppContext):
  """
  Display current step 
  """
  normal_font = font.Font(family="Helvetica", size=11)
  bold_font = font.Font(family="Helvetica", size=11, weight="bold")
  if context.novice_mode:
    steps = ["0. Intro", "1. Gather Info", "2. Backup", "3. Prepare Media"]
  else:
    steps = ["1. Gather Info", "2. Backup", "3. Prepare Media"]

  status_frame = tk.Frame(context.root)
  status_frame.pack(pady=10, anchor="n")
  for i, step in enumerate(steps):
    lbl_font = bold_font if i == step_index else normal_font
    label = ttk.Label(status_frame, text=step, font=lbl_font)
    label.pack(side="left")

    if i < len(steps) - 1:
      sep = ttk.Label(status_frame, text=" > ", font=normal_font)
      sep.pack(side="left")

def media(context: AppContext):
  """
  Step 3. Prepare installation media
  """
  context.root.title("Let's prepare your installation media")
  context.clear_screen()
  get_status(3, context)
  context.gen_header("Let's prepare your installation media")
  buttons = [
    ("Back", backup),
    ("Home", home),
  ]
  context.gen_bbuttons(buttons)

def backup(context: AppContext):
  """
  Step 2. Backup screen: create tar or tar.bz2 archive
  """
  context.root.title("Let's back up your data")
  context.clear_screen()
  get_status(2, context)
  context.gen_header("Let's back up your data")
  backup = Backup(context)

  # reserve frame for tar progress bar
  context.progress_frame = ttk.Frame(context.root)
  context.progress_frame.pack(pady=5)

  # 1. destination label
  context.destination_label = ttk.Label(context.root, text="Your current destination folder: " + backup.destination_folder)
  context.destination_label.pack(pady=5, padx=30, anchor="center")
  check_var = tk.BooleanVar(value=context.compress)

  def update_context(*args):
      context.compress = check_var.get()

  check_var.trace_add("write", update_context)
  checkbox = ttk.Checkbutton(context.root, text="Enable compression", variable=check_var)
  checkbox.pack(pady=0, padx=10, anchor="center")

  # 2. button_frame: set destination, add source
  choice_buttons = [
    ("Set destination", backup.set_destination, "Here you set the folder, where to put your archive"),
    ("Add source folder", backup.add_folder, "Here you can add folders to the archive")
  ]
  context.gen_choice(choice_buttons)

  # 3. folders from backup
  context.gen_label("Your source folders for backup -- press 'Remove' to remove from the list.")
  context.set_source_folder_label()
  backup.folder_list_frame = ttk.Frame(context.root)
  backup.folder_list_frame.pack(fill="both", expand=False, padx=10, pady=5)

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
  context.root.title("Gathering software and hardware info")
  context.clear_screen()
  get_status(1, context)
  context.progress_frame = ttk.Frame(context.root)
  context.progress_frame.pack(pady=5)

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

def launch_novice_mode(context: AppContext):
  """
  Step 0, for novice mode only -- display some info with links
  """
  context.root.title("LMTK: Are you familiar with Linux?")
  context.clear_screen()
  context.gen_header("LMTK: Are you familiar with Linux?")
  get_status(0, context)
  text_frame = ttk.Frame(context.root)
  text_frame.pack(padx=20, pady=20, fill="x")
  text_frame.configure(height=200)  
  scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
  scrollbar.pack(side="right", fill="y")
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

When you click 'Next', we'll gather information about your software and hardware, save it as Markdown (.md) and HTML (.html) reports for future use.
"""
  text = tk.Text(text_frame, height=25, width=100, wrap="word", font=("Helvetica", 11), bd=0, bg=context.root.cget("bg"), relief="flat", highlightthickness=0, yscrollcommand=scrollbar.set)
  text.pack(side="left", fill="both", expand=True)
  text.insert("1.0", guide_content)
  scrollbar.config(command=text.yview)
  text.tag_config("line_spacing", spacing3=6)  # spacing in pixels
  # text.tag_add("line_spacing", "1.0", "end")
  text.config(state="disabled")

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
    text.tag_bind(tag, "<Button-1>", lambda event, url=url: webbrowser.open_new(url))

  # text.config(state=tk.DISABLED)

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
  context.root.title("Welcome to Linux Migration Toolkit!")
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
