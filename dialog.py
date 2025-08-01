import tkinter as tk
from tkinter import ttk
import webbrowser
import subprocess

def open_git(event, link):
  webbrowser.open_new(link)

def launch_novice_mode():
  for widget in root.winfo_children():
    widget.destroy()
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
    text.tag_config(tag, foreground="blue", underline=1)
    text.tag_bind(tag, "<Button-1>", lambda event, url=url: open_git(event, url))

  text.config(state=tk.DISABLED)

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
  root.title("Welcome to Linux Migration Toolkit!")
  root.geometry("800x600")
  root.resizable(False, False)

  title_label = ttk.Label(root, text="Welcome to Linux Migration Toolkit! Choose Your Mode", font=("Helvetica", 16, "bold"))
  title_label.pack(pady=20)

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

  reddit_text = ttk.Label(root, text="Thanks to all the guys and gals in reddit.com/r/linuxsucks/, you're my inspiration.", wraplength=600, justify="left")
  reddit_text.pack(padx=20, pady=20)

  root.mainloop()

main()

