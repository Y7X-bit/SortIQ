import os
import shutil
import json
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
from collections import defaultdict

SETTINGS_FILE = "config.json"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class SortIQ(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🧠 SortIQ")
        self.geometry("750x500")
        self.configure(bg="#000000")
        self.resizable(False, False)

        self.file_categories = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            'Videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            'Executables': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.app'],
            'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'Presentations': ['.ppt', '.pptx', '.odp'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go'],
            'Ebooks': ['.epub', '.mobi', '.azw', '.azw3']
        }

        self.load_settings()
        self.create_widgets()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {"last_folder": "", "auto_clean": True, "age_filter": 0}

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

    def create_widgets(self):
        red = "#ff0000"
        white = "#ffffff"
        radius = 50

        self.main_frame = ctk.CTkFrame(self, fg_color="#000000")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.main_frame, text="Select Folder to Organize", font=("Segoe UI", 22), text_color=white)
        self.label.pack(pady=(0, 15))

        self.folder_btn = ctk.CTkButton(self.main_frame, text="📂 Browse", text_color=white, fg_color="transparent", border_color=red, border_width=2, corner_radius=radius, command=self.select_folder, height=50, width=250)
        self.folder_btn.pack(pady=(10, 20))

        self.auto_clean_var = ctk.BooleanVar(value=self.settings.get("auto_clean", True))
        self.clean_checkbox = ctk.CTkCheckBox(self.main_frame, text="🧼 Auto-delete Empty Folders", variable=self.auto_clean_var, checkbox_height=20, checkbox_width=20, border_color=red, text_color=white)
        self.clean_checkbox.pack(pady=(0, 20))

        self.age_label = ctk.CTkLabel(self.main_frame, text=f"Filter Files Older Than {int(self.settings.get('age_filter', 0))} Days", font=("Segoe UI", 14), text_color=white)
        self.age_label.pack(pady=10)

        self.age_slider = ctk.CTkSlider(self.main_frame, from_=0, to=30, number_of_steps=30, command=self.update_age_label, progress_color=red)
        self.age_slider.set(self.settings.get("age_filter", 0))
        self.age_slider.pack(pady=5, fill="x", padx=50)

        self.button_row = ctk.CTkFrame(self.main_frame, fg_color="#000000")
        self.button_row.pack(pady=25)

        self.preview_btn = ctk.CTkButton(self.button_row, text="🔎 Preview", text_color=white, fg_color="transparent", border_color=red, border_width=2, corner_radius=radius, command=self.preview_files, height=50, width=180)
        self.preview_btn.grid(row=0, column=0, padx=20)

        self.organize_btn = ctk.CTkButton(self.button_row, text="🧹 Organize", text_color=white, fg_color="transparent", border_color=red, border_width=2, corner_radius=radius, command=self.organize_files, height=50, width=180)
        self.organize_btn.grid(row=0, column=1, padx=20)

        self.undo_btn = ctk.CTkButton(self.button_row, text="↩️ Undo", text_color=white, fg_color="transparent", border_color=red, border_width=2, corner_radius=radius, command=self.undo_organization, height=50, width=180)
        self.undo_btn.grid(row=0, column=2, padx=20)

        self.status = ctk.CTkLabel(self.main_frame, text="", font=("Segoe UI", 14), text_color=white)
        self.status.pack(pady=10)

        self.branding = ctk.CTkLabel(self.main_frame, text="🔎 Powered by Y7X 💗", font=("Segoe UI", 13), text_color=white)
        self.branding.pack(pady=5)

        self.selected_folder = self.settings.get("last_folder", "")

    def update_age_label(self, value):
        self.age_label.configure(text=f"Filter Files Older Than {int(float(value))} Days")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.settings["last_folder"] = folder
            self.save_settings()
            self.status.configure(text=f"Selected: {folder}")

    def get_category(self, ext):
        ext = ext.lower()
        for cat, exts in self.file_categories.items():
            if ext in exts:
                return cat
        return 'Others'

    def is_old_enough(self, path):
        age_days = int(self.age_slider.get())
        if age_days == 0:
            return True
        cutoff = datetime.now() - timedelta(days=age_days)
        return datetime.fromtimestamp(os.path.getmtime(path)) < cutoff

    def preview_files(self):
        if not self.selected_folder:
            messagebox.showwarning("No Folder", "Select a folder first!")
            return

        moved = defaultdict(int)
        for file in os.listdir(self.selected_folder):
            full_path = os.path.join(self.selected_folder, file)
            if os.path.isfile(full_path) and not file.startswith(('.', '~')) and self.is_old_enough(full_path):
                ext = Path(file).suffix
                cat = self.get_category(ext)
                moved[cat] += 1

        msg = "Preview:\n" + "\n".join([f"{cat}: {cnt} file(s)" for cat, cnt in moved.items()])
        messagebox.showinfo("Preview", msg if moved else "No files to organize with current filter.")

    def organize_files(self):
        if not self.selected_folder:
            messagebox.showwarning("No Folder", "Select a folder first!")
            return

        files = [f for f in os.listdir(self.selected_folder)
                 if os.path.isfile(os.path.join(self.selected_folder, f)) and not f.startswith(('.', '~'))]

        moved = 0
        for file in files:
            src = os.path.join(self.selected_folder, file)
            if not self.is_old_enough(src):
                continue
            ext = Path(file).suffix
            cat = self.get_category(ext)
            dest_dir = os.path.join(self.selected_folder, cat)
            os.makedirs(dest_dir, exist_ok=True)

            base, ext = os.path.splitext(file)
            new_name = f"{base}_{datetime.now().strftime('%H%M%S')}{ext}"
            dest_path = os.path.join(dest_dir, new_name if os.path.exists(os.path.join(dest_dir, file)) else file)

            shutil.move(src, dest_path)
            moved += 1

        if self.auto_clean_var.get():
            for cat in list(self.file_categories.keys()) + ['Others']:
                dir_path = os.path.join(self.selected_folder, cat)
                if os.path.exists(dir_path) and not os.listdir(dir_path):
                    os.rmdir(dir_path)

        self.status.configure(text=f"✅ Organized {moved} files")
        messagebox.showinfo("Done", f"Organized {moved} files successfully!")
        self.settings["auto_clean"] = self.auto_clean_var.get()
        self.settings["age_filter"] = int(self.age_slider.get())
        self.save_settings()

    def undo_organization(self):
        if not self.selected_folder:
            messagebox.showwarning("No Folder", "Select a folder first!")
            return

        restored = 0
        for cat in list(self.file_categories.keys()) + ['Others']:
            path = os.path.join(self.selected_folder, cat)
            if os.path.isdir(path):
                for file in os.listdir(path):
                    src = os.path.join(path, file)
                    dest = os.path.join(self.selected_folder, file)
                    base, ext = os.path.splitext(dest)
                    counter = 1
                    while os.path.exists(dest):
                        dest = f"{base}_restored_{counter}{ext}"
                        counter += 1
                    shutil.move(src, dest)
                    restored += 1
                try:
                    os.rmdir(path)
                except:
                    pass

        self.status.configure(text=f"↩️ Restored {restored} files")
        messagebox.showinfo("Undo", f"Restored {restored} files to main folder")

if __name__ == "__main__":
    app = SortIQ()
    app.mainloop()
