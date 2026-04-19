import subprocess
import sys
import ctypes
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# 1. ADMIN PRIVILEGES
# ==========================================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    except Exception as e:
        print(f"Failed to elevate: {e}")
    sys.exit()

# ==========================================
# 2. DETECTION LOGIC
# ==========================================
def get_usb_disks():
    ps_command = (
        'powershell "'
        '$disks = Get-PhysicalDisk | Where-Object { $_.BusType -eq \'USB\' }; '
        'foreach ($d in $disks) { '
            '$size = $d.Size; '
            'if (-not $size) { $size = (Get-Disk -Number $d.DeviceId).Size }; '
            'if (-not $size) { $size = (Get-WmiObject Win32_DiskDrive | Where-Object { $_.Index -eq $d.DeviceId }).Size }; '
            'Write-Output ($d.DeviceId.ToString() + \'|\' + $d.FriendlyName + \'|\' + $size.ToString())'
        '}"'
    )
    
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        output = subprocess.check_output(ps_command, startupinfo=startupinfo, text=True)
    except:
        return {}

    found_disks = {}
    lines = output.strip().splitlines()
    for line in lines:
        parts = line.split('|')
        if len(parts) >= 3:
            device_id = parts[0]
            name = parts[1]
            try:
                size_gb = round(int(parts[2]) / (1024**3), 1)
                size_str = f"{size_gb} GB"
            except:
                size_str = "Unknown Size"
            
            found_disks[device_id] = f"{name} ({size_str})"
            
    return found_disks

def run_diskpart(commands):
    script = "\n".join(commands)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    p = subprocess.Popen(["diskpart"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, startupinfo=startupinfo)
    p.communicate(script)

# ==========================================
# 3. MODERN DARK GUI WITH HOVER & PROGRESS
# ==========================================
class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Recovery Tool")
        self.root.geometry("480x620")
        self.root.configure(bg="#121212")
        self.root.resizable(False, False)

        self.bg_color = "#121212"
        self.accent_color = "#3d5afe"      # Azul normal
        self.hover_color = "#536dfe"       # Azul más brillante
        self.text_color = "#FFFFFF"
        self.card_color = "#1E1E1E"

        self.disk_map = {}
        self.setup_styles()
        self.create_widgets()
        self.refresh_list()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo de la Barra de Progreso
        style.configure("Custom.Horizontal.TProgressbar", 
                        troughcolor="#1e1e1e", 
                        background=self.accent_color, 
                        thickness=6, 
                        borderwidth=0)
        
        style.configure("TCombobox", 
                        fieldbackground=self.card_color, 
                        background=self.card_color, 
                        foreground=self.text_color, 
                        bordercolor="#333333",
                        arrowcolor=self.text_color)
        
        style.map("TCombobox",
                  fieldbackground=[("readonly", self.card_color)],
                  foreground=[("readonly", self.text_color)])

        self.root.option_add("*TCombobox*Listbox.background", self.card_color)
        self.root.option_add("*TCombobox*Listbox.foreground", self.text_color)
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.accent_color)
        self.root.option_add("*TCombobox*Listbox.selectForeground", self.text_color)

    def create_widgets(self):
        # Header
        tk.Label(self.root, text="USB Recovery", font=("Segoe UI", 26, "bold"), bg=self.bg_color, fg=self.text_color).pack(pady=(40, 5))
        tk.Label(self.root, text="Flash drive restoration utility", font=("Segoe UI", 10), bg=self.bg_color, fg="#888888").pack(pady=(0, 30))

        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(padx=40, fill="x")

        # Refresh Row
        label_frame = tk.Frame(container, bg=self.bg_color)
        label_frame.pack(fill="x", pady=(10, 5))
        tk.Label(label_frame, text="SELECT TARGET DEVICE", font=("Segoe UI", 8, "bold"), bg=self.bg_color, fg=self.accent_color).pack(side="left")
        self.btn_refresh = tk.Button(label_frame, text="↻", font=("Segoe UI", 12), bg=self.bg_color, fg="#888888", 
                                     borderwidth=0, activebackground=self.bg_color, activeforeground="white", 
                                     cursor="hand2", command=self.refresh_list)
        self.btn_refresh.pack(side="right")

        self.disk_var = tk.StringVar()
        self.disk_combo = ttk.Combobox(container, textvariable=self.disk_var, state="readonly")
        self.disk_combo.pack(fill="x", ipady=8)

        # File System
        tk.Label(container, text="FILE SYSTEM", font=("Segoe UI", 8, "bold"), bg=self.bg_color, fg=self.accent_color).pack(anchor="w", pady=(20, 5))
        self.fs_var = tk.StringVar(value="exFAT (Recommended)")
        self.fs_combo = ttk.Combobox(container, textvariable=self.fs_var, 
                                     values=["exFAT (Recommended)", "FAT32", "NTFS"], 
                                     state="readonly")
        self.fs_combo.pack(fill="x", ipady=8)

        # Simulation Mode
        self.sim_var = tk.BooleanVar(value=True)
        self.sim_check = tk.Checkbutton(self.root, text="Run in Simulation Mode", variable=self.sim_var, 
                                        bg=self.bg_color, fg="#888888", selectcolor="#121212", 
                                        activebackground=self.bg_color, activeforeground="white", 
                                        font=("Segoe UI", 9), bd=0, highlightthickness=0)
        self.sim_check.pack(pady=20)

        # Main Action Button with Hover Effect
        self.btn_action = tk.Button(self.root, text="RECOVER DEVICE", font=("Segoe UI", 10, "bold"), 
                                    bg=self.accent_color, fg="white", cursor="hand2", borderwidth=0,
                                    activebackground=self.hover_color, activeforeground="white", 
                                    relief="flat", command=self.start_process)
        self.btn_action.pack(ipadx=40, ipady=12, pady=10)
        
        # Bind Hover Events
        self.btn_action.bind("<Enter>", lambda e: self.btn_action.config(bg=self.hover_color))
        self.btn_action.bind("<Leave>", lambda e: self.btn_action.config(bg=self.accent_color))

        # Real Progress Bar (Hidden by default)
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="indeterminate", style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10)
        self.progress.pack_forget() # Hide initially

        self.status_label = tk.Label(self.root, text="Ready", font=("Segoe UI", 8), bg=self.bg_color, fg="#555555")
        self.status_label.pack(side="bottom", pady=20)

    def refresh_list(self):
        self.status_label.config(text="Scanning...")
        self.root.update_idletasks()
        self.disk_map = get_usb_disks()
        if not self.disk_map:
            self.disk_combo['values'] = ["No USB drives detected"]
            self.disk_combo.current(0)
            self.btn_action.config(state="disabled", bg="#333333")
        else:
            self.disk_combo['values'] = list(self.disk_map.values())
            self.disk_combo.current(0)
            self.btn_action.config(state="normal", bg=self.accent_color)
        self.status_label.config(text="Ready")

    def start_process(self):
        display_name = self.disk_var.get()
        if "No USB" in display_name: return

        disk_id = None
        for device_id, name_label in self.disk_map.items():
            if name_label == display_name:
                disk_id = device_id
                break
        
        if disk_id is None: return

        if not self.sim_var.get():
            confirm = messagebox.askyesno("Confirm Action", f"WARNING: All data on '{display_name}' will be destroyed.\nProceed?")
            if not confirm: return

        # UI Updates for processing
        self.btn_action.config(state="disabled", text="PROCESSING...")
        self.btn_refresh.config(state="disabled")
        self.status_label.config(text="Running Diskpart operations...")
        
        # Show and start progress bar
        self.progress.pack(pady=10)
        self.progress.start(15)
        
        threading.Thread(target=self.worker, args=(disk_id,)).start()

    def worker(self, disk_id):
        raw_fs = self.fs_var.get().split(" ")[0].lower()
        if self.sim_var.get():
            import time
            time.sleep(2.5) # Simulating work
            messagebox.showinfo("Simulation", "Commands processed (Virtual)")
        else:
            cmds = [f"select disk {disk_id}", "clean", "create partition primary", f"format fs={raw_fs} quick", "assign", "exit"]
            run_diskpart(cmds)
            messagebox.showinfo("Success", "Device recovered successfully.")

        self.root.after(0, self.finish_worker)

    def finish_worker(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_action.config(state="normal", text="RECOVER DEVICE")
        self.btn_refresh.config(state="normal")
        self.status_label.config(text="Ready")
        self.refresh_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()
