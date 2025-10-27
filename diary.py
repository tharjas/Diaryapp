import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import Image, ImageTk, ImageDraw
import calendar
from datetime import datetime
import json
import os
import sys
import math
from themes import THEMES
from datetime import timedelta

class DiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("♡ My Diary ♡")
        self.root.geometry("900x600")
        
        self.themes = THEMES
        self.config_file = "config.json"
        self.font_main = ("MS PGothic", 12)
        self.load_config()

        self.root.configure(bg=self.theme['main_bg'])

        self.selected_date = datetime.now()
        self.data = {}

        # Drawing defaults
        self.brush_color = "black"
        self.brush_width = 5
        self.eraser_width = 20
        self.current_tool = "brush"

        self.drawings_dir = os.path.join(os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)), "drawings")
        os.makedirs(self.drawings_dir, exist_ok=True)
        self.images_dir = os.path.join(os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)), "images")
        os.makedirs(self.images_dir, exist_ok=True)

        # Data file setup
        if getattr(sys, 'frozen', False):
            self.data_file = os.path.join(os.path.dirname(sys.executable), "entries", "diary_data.json")
        else:
            self.data_file = os.path.join(os.path.dirname(__file__), "entries", "diary_data.json")

        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f:
                json.dump({}, f)

        self.load_data()
        self.create_widgets()
        self.update_calendar()
        self.load_entry()
        self.update_time()
        # Apply backgrounds based on theme
        if self.current_theme == "kawaii_pink":
            self.calendar_frame.configure(bg=self.bg_left_start)
            self.entry_frame.configure(bg=self.bg_right_start)
        else:
            self.apply_gradient(self.calendar_frame, self.bg_left_start, self.bg_left_end)
            self.apply_gradient(self.entry_frame, self.bg_right_start, self.bg_right_end)

    def load_theme(self):
        self.theme = self.themes[self.current_theme]
        self.bg_left_start = self.theme["bg_left_start"]
        self.bg_left_end = self.theme["bg_left_end"]
        self.bg_right_start = self.theme["bg_right_start"]
        self.bg_right_end = self.theme["bg_right_end"]
        self.button_color = self.theme["button_color"]
        self.active_button = self.theme["active_button"]
        self.text_bg = self.theme["text_bg"]
        self.text_fg = self.theme["text_fg"]
        self.calendar_day_bg = self.theme["calendar_day_bg"]
        self.settings_text_fg = self.theme["settings_text_fg"]
        self.calendar_day_fg = self.theme["calendar_day_fg"]
        self.border_color = self.theme["border_color"]

    def update_time(self):
        now = datetime.now()
        time_str = f"🕰️{now.strftime('%H:%M:%S')}"
        date_str = f"🗓️{now.strftime('%m/%d/%Y')}"
        self.time_label.config(text=time_str)
        self.date_label.config(text=date_str)
        self.root.after(1000, self.update_time)

    def apply_gradient(self, frame, start_color, end_color):
        # Only apply gradient if not kawaii_pink theme
        if self.current_theme == "kawaii_pink":
            frame.configure(bg=start_color)
            if hasattr(frame, 'bg_label'):
                frame.bg_label.destroy()
                del frame.bg_label
            return

        frame.start_color = start_color
        frame.end_color = end_color

        def draw_gradient(event=None):
            width = frame.winfo_width()
            height = frame.winfo_height()
            if width < 2 or height < 2:
                return

            image = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(image)

            # Convert colors to RGB (winfo_rgb returns 0-65535)
            r1, g1, b1 = self.root.winfo_rgb(frame.start_color)
            r2, g2, b2 = self.root.winfo_rgb(frame.end_color)

            dr = (r2 - r1) / (height - 1) if height > 1 else 0
            dg = (g2 - g1) / (height - 1) if height > 1 else 0
            db = (b2 - b1) / (height - 1) if height > 1 else 0

            r, g, b = r1, g1, b1
            for i in range(height):
                draw.line((0, i, width, i), fill=(int(r / 256), int(g / 256), int(b / 256)))
                r += dr
                g += dg
                b += db

            tk_image = ImageTk.PhotoImage(image)

            if not hasattr(frame, 'bg_label'):
                frame.bg_label = tk.Label(frame, image=tk_image)
                frame.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                frame.bg_label.lower()  # Send to back so other widgets show on top
            else:
                frame.bg_label.configure(image=tk_image)

            frame.bg_label.image = tk_image  # Keep reference to prevent garbage collection

        frame.draw_gradient = draw_gradient
        frame.bind("<Configure>", lambda e: draw_gradient())
        # Initial draw (delay slightly to ensure frame has size)
        self.root.after(100, draw_gradient)

    # ---------------- UI SETUP ----------------
    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg="#C7D3E3")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Calendar
        self.calendar_frame = tk.Frame(self.main_frame, bg=self.bg_left_start, bd=6, relief="ridge")
        self.calendar_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Diary
        self.entry_frame = tk.Frame(self.main_frame, bg=self.bg_right_start, bd=6, relief="ridge")
        self.entry_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Settings Menu
        self.settings_button = tk.Button(self.entry_frame, text="⚙️", font=self.font_main, bg=self.button_color, relief="raised", bd=2, command=self.open_settings_window, width=2)
        self.settings_button.place(relx=1.0, rely=0, anchor="ne", x=-5, y=5)

        # Navigation
        self.navigation_frame = tk.Frame(self.calendar_frame, bg=self.bg_left_start)
        self.navigation_frame.pack(pady=5)
        tk.Button(self.navigation_frame, text="<", command=self.prev_month,
                  font=self.font_main, bg=self.button_color,
                  activebackground=self.active_button).pack(side="left", padx=10)
        self.month_year_label = tk.Label(self.navigation_frame, text="", font=self.font_main, bg=self.bg_left_start)
        self.month_year_label.pack(side="left")
        tk.Button(self.navigation_frame, text=">", command=self.next_month,
                  font=self.font_main, bg=self.button_color,
                  activebackground=self.active_button).pack(side="left", padx=10)

        self.calendar_grid = tk.Frame(self.calendar_frame, bg=self.bg_left_start)
        self.calendar_grid.pack(pady=10)

        # Date and Time Widget
        self.datetime_frame = tk.Frame(self.calendar_frame, bg=self.bg_left_start)
        self.datetime_frame.pack(side="bottom", anchor="sw", padx=10, pady=10)

        self.time_label = tk.Label(self.datetime_frame, text="", font=self.font_main, bg=self.bg_left_start)
        self.time_label.pack(anchor="w")
        self.date_label = tk.Label(self.datetime_frame, text="", font=self.font_main, bg=self.bg_left_start)
        self.date_label.pack(anchor="w")

        # Mood Tracker
        self.day_status_frame = tk.Frame(self.entry_frame, bg=self.bg_right_start)
        self.day_status_frame.pack(pady=10)
        tk.Label(self.day_status_frame, text="♡ Mood Tracker ♡",
                 bg=self.bg_right_start, font=self.font_main).pack(pady=(0, 5))
        self.status_var = tk.StringVar()
        self.create_mood_radiobuttons()

        # Diary Text
        self.text_frame = tk.Frame(self.entry_frame, bg=self.border_color, relief="sunken", bd=4)
        self.text_frame.pack(pady=5, fill="both", expand=True, padx=10)
        self.diary_text = tk.Text(self.text_frame, height=15, width=40, font=self.font_main,
                                  bg=self.text_bg, fg="black", relief="flat", wrap="word", undo=True)
        self.diary_text.pack(fill="both", expand=True)

        # Editor buttons + Save button (same line)
        self.editor_frame = tk.Frame(self.entry_frame, bg=self.bg_right_start)
        self.editor_frame.pack(pady=(0, 5), padx=10, fill="x")
        self.create_editor_buttons()

        save_btn = tk.Button(self.editor_frame, text="💾 Save Entry", command=self.save_entry,
                             font=self.font_main, bg=self.button_color,
                             activebackground=self.active_button)
        save_btn.pack(side="right", padx=5)

        # Image & Drawing buttons
        self.image_drawing_frame = tk.Frame(self.entry_frame, bg=self.bg_right_start)
        self.image_drawing_frame.pack(pady=5)
        tk.Button(self.image_drawing_frame, text="🖼️ Image of the Day", font=self.font_main,
                  bg=self.button_color, activebackground=self.active_button,
                  command=self.open_image_window).pack(side="left", padx=5)
        tk.Button(self.image_drawing_frame, text="🎨 Drawing of the Day", font=self.font_main,
                  bg=self.button_color, activebackground=self.active_button,
                  command=self.open_drawing_window).pack(side="left", padx=5)
        self.update_ui_colors()

    def open_settings_window(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("300x200")
        settings_win.configure(bg=self.theme['main_bg'])

        tk.Label(settings_win, text="Skins", font=self.font_main, bg=self.theme['main_bg'], fg=self.settings_text_fg).pack(pady=5)

        theme_var = tk.StringVar(value=self.current_theme)
        theme_menu = tk.OptionMenu(settings_win, theme_var, *self.themes.keys(), command=self.change_theme)
        theme_menu.pack(pady=5)

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.load_theme()
        self.update_ui_colors()
        self.save_config()
        # Apply backgrounds based on theme
        if self.current_theme == "kawaii_pink":
            self.calendar_frame.configure(bg=self.bg_left_start)
            self.entry_frame.configure(bg=self.bg_right_start)
            if hasattr(self.calendar_frame, 'bg_label'):
                self.calendar_frame.bg_label.destroy()
                del self.calendar_frame.bg_label
            if hasattr(self.entry_frame, 'bg_label'):
                self.entry_frame.bg_label.destroy()
                del self.entry_frame.bg_label
        else:
            self.calendar_frame.start_color = self.bg_left_start
            self.calendar_frame.end_color = self.bg_left_end
            self.apply_gradient(self.calendar_frame, self.bg_left_start, self.bg_left_end)
            self.entry_frame.start_color = self.bg_right_start
            self.entry_frame.end_color = self.bg_right_end
            self.apply_gradient(self.entry_frame, self.bg_right_start, self.bg_right_end)

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.current_theme = config.get("theme", "kawaii_pink")
        except (FileNotFoundError, json.JSONDecodeError):
            self.current_theme = "kawaii_pink"
        self.load_theme()

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump({"theme": self.current_theme}, f)

    def update_ui_colors(self):
        self.root.configure(bg=self.theme['main_bg'])
        self.main_frame.configure(bg=self.theme['main_bg'])
        self.calendar_frame.configure(bg=self.bg_left_start)
        self.entry_frame.configure(bg=self.bg_right_start)
        self.navigation_frame.configure(bg=self.bg_left_start)
        self.month_year_label.configure(bg=self.bg_left_start, fg=self.text_fg)
        self.calendar_grid.configure(bg=self.bg_left_start)
        self.datetime_frame.configure(bg=self.bg_left_start)
        self.time_label.configure(bg=self.bg_left_start, fg=self.text_fg)
        self.date_label.configure(bg=self.bg_left_start, fg=self.text_fg)
        self.day_status_frame.configure(bg=self.bg_right_start)
        self.text_frame.configure(bg=self.border_color)
        self.diary_text.configure(bg=self.text_bg, fg=self.text_fg)
        self.editor_frame.configure(bg=self.bg_right_start)
        self.image_drawing_frame.configure(bg=self.bg_right_start)
        self.settings_button.configure(bg=self.button_color)

        for widget in self.navigation_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=self.button_color, activebackground=self.active_button)
        
        for widget in self.day_status_frame.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                widget.configure(bg=self.bg_right_start, activebackground=self.bg_right_start, selectcolor=self.bg_right_start, fg=self.text_fg)
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.bg_right_start, fg=self.text_fg)

        for widget in self.editor_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=self.button_color, activebackground=self.active_button)

        for widget in self.image_drawing_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=self.button_color, activebackground=self.active_button)

        self.update_calendar()

    # ---------------- Mood Tracker ----------------
    def create_mood_radiobuttons(self):
        moods = [
            ("Healthy eating", "yellow"),
            ("Healthy eating + exercise", "green"),
            ("Bad Day", "red")
        ]
        for text, color in moods:
            tk.Radiobutton(self.day_status_frame, text=text, variable=self.status_var, value=color,
                           bg=self.bg_right_start, font=self.font_main, activebackground=self.bg_right_start).pack(anchor="w")

    # ---------------- Editor ----------------
    def create_editor_buttons(self):
        color_btn = tk.Button(self.editor_frame, text="Text Color", font=self.font_main,
                              bg=self.button_color, activebackground=self.active_button,
                              command=self.change_text_color)
        bold_btn = tk.Button(self.editor_frame, text="B", font=self.font_main + ("bold",),
                             bg=self.button_color, activebackground=self.active_button,
                             command=lambda: self.toggle_tag("bold"))
        italic_btn = tk.Button(self.editor_frame, text="I", font=self.font_main + ("italic",),
                               bg=self.button_color, activebackground=self.active_button,
                               command=lambda: self.toggle_tag("italic"))
        underline_btn = tk.Button(self.editor_frame, text="U", font=self.font_main,
                                  bg=self.button_color, activebackground=self.active_button,
                                  command=lambda: self.toggle_tag("underline"))
        emoji_btn = tk.Button(self.editor_frame, text="😊", font=self.font_main,
                              bg=self.button_color, activebackground=self.active_button,
                              command=self.insert_emoji)
        for b in [color_btn, bold_btn, italic_btn, underline_btn, emoji_btn]:
            b.pack(side="left", padx=2)

        self.diary_text.tag_configure("bold", font=self.font_main + ("bold",))
        self.diary_text.tag_configure("italic", font=self.font_main + ("italic",))
        self.diary_text.tag_configure("underline", font=self.font_main + ("underline",))

    def change_text_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            try:
                self.diary_text.tag_add(color, "sel.first", "sel.last")
                self.diary_text.tag_config(color, foreground=color)
            except tk.TclError:
                pass

    def toggle_tag(self, tag):
        try:
            current_tags = self.diary_text.tag_names("sel.first")
            if tag in current_tags:
                self.diary_text.tag_remove(tag, "sel.first", "sel.last")
            else:
                self.diary_text.tag_add(tag, "sel.first", "sel.last")
        except tk.TclError:
            pass
        return "break"

    def insert_emoji(self):
        emoji_list = ["😊", "😂", "😍", "😢", "😎", "❤️", "👍"]
        menu = tk.Menu(self.root, tearoff=0)
        for e in emoji_list:
            menu.add_command(label=e, command=lambda em=e: self.diary_text.insert("insert", em))
        try:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    # ---------------- Helper: darken hex color ----------------
    def _darken_hex(self, hexcolor, amount=0.85):
        """
        Darken a hex color by amount (0..1). If invalid hex, return original.
        """
        try:
            if not hexcolor or not hexcolor.startswith("#") or len(hexcolor) != 7:
                return hexcolor
            r = int(hexcolor[1:3], 16)
            g = int(hexcolor[3:5], 16)
            b = int(hexcolor[5:7], 16)
            r = max(0, min(255, int(r * amount)))
            g = max(0, min(255, int(g * amount)))
            b = max(0, min(255, int(b * amount)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hexcolor

    # ---------------- Calendar ----------------
    def update_calendar(self):
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
        self.month_year_label.config(text=self.selected_date.strftime("%B %Y"))
        cal = calendar.monthcalendar(self.selected_date.year, self.selected_date.month)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(self.calendar_grid, text=day, font=self.font_main, bg=self.bg_left_start, fg=self.text_fg).grid(row=0, column=i)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day != 0:
                    date_str = f"{self.selected_date.year}-{self.selected_date.month:02d}-{day:02d}"
                    color = self.data.get(date_str, {}).get("color") or self.calendar_day_bg

                    # Determine if this day is the currently selected day
                    is_selected = (day == self.selected_date.day)

                    # If color is a hex color and selected, slightly darken it so the pressed effect is obvious
                    display_color = color
                    if is_selected and isinstance(color, str) and color.startswith("#") and len(color) == 7:
                        display_color = self._darken_hex(color, amount=0.82)

                    # Visual pressed-in style for selected day
                    relief_style = "sunken" if is_selected else "raised"
                    bd_val = 4 if is_selected else 2

                    day_fg_color = self.calendar_day_fg
                    if self.current_theme in ["dark_mode", "xbox", "galaxy"] and color in ["yellow", "green", "red"]:
                        day_fg_color = "black"

                    btn = tk.Button(self.calendar_grid, text=str(day), width=4, height=2,
                                    bg=display_color, command=lambda d=day: self.select_date(d),
                                    relief=relief_style, bd=bd_val, activebackground=self.active_button, fg=day_fg_color)
                    btn.grid(row=r + 1, column=c, padx=2, pady=2)

    def next_month(self):
        if self.selected_date.month == 12:
            self.selected_date = self.selected_date.replace(year=self.selected_date.year + 1, month=1)
        else:
            self.selected_date = self.selected_date.replace(month=self.selected_date.month + 1)
        self.update_calendar()

    def prev_month(self):
        if self.selected_date.month == 1:
            self.selected_date = self.selected_date.replace(year=self.selected_date.year - 1, month=12)
        else:
            self.selected_date = self.selected_date.replace(month=self.selected_date.month - 1)
        self.update_calendar()

    def select_date(self, day):
        self.selected_date = self.selected_date.replace(day=day)
        self.update_calendar()
        self.load_entry()

    # ---------------- Save / Load ----------------
    def save_entry(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        entry_text = self.diary_text.get("1.0", "end-1c")
        status = self.status_var.get()
        if date_str not in self.data:
            self.data[date_str] = {}
        self.data[date_str]["text"] = entry_text
        self.data[date_str]["color"] = status
        self.save_data_to_file()
        self.update_calendar()

    def load_entry(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        entry = self.data.get(date_str, {})
        self.diary_text.delete("1.0", "end")
        self.diary_text.insert("1.0", entry.get("text", ""))
        self.status_var.set(entry.get("color", ""))

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

    def save_data_to_file(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    # ---------------- Image of the Day ----------------
    def open_image_window(self):
        win = tk.Toplevel(self.root)
        win.title("🖼️ Image of the Day")
        win.geometry("400x400")
        win.configure(bg=self.theme['bg_right_start'])

        date_str = self.selected_date.strftime("%Y-%m-%d")
        current = self.data.get(date_str, {}).get("image_path")

        img_label = tk.Label(win, bg=self.theme['bg_right_start'])
        img_label.pack(pady=10)

        def load_image():
            path = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
            )
            if path:
                filename = os.path.basename(path)
                new_path = os.path.join(self.images_dir, filename)
                img = Image.open(path)
                img.save(new_path)

                img.thumbnail((300, 300))
                tk_img = ImageTk.PhotoImage(img)
                img_label.configure(image=tk_img)
                img_label.image = tk_img
                if date_str not in self.data:
                    self.data[date_str] = {}
                self.data[date_str]["image_path"] = new_path
                self.save_data_to_file()

        tk.Button(win, text="Upload Image", command=load_image,
                  bg=self.theme['button_color'], activebackground=self.theme['active_button'],
                  font=self.font_main).pack(pady=5)

        if current and os.path.exists(current):
            img = Image.open(current)
            img.thumbnail((300, 300))
            tk_img = ImageTk.PhotoImage(img)
            img_label.configure(image=tk_img)
            img_label.image = tk_img

    # ---------------- Drawing of the Day ----------------
    def open_drawing_window(self):
        DrawingWindow(self, self.theme)

class DrawingWindow(tk.Toplevel):
    def __init__(self, app, theme):
        super().__init__(app.root)
        self.app = app
        self.theme = theme
        self.title("🎨 Drawing of the Day")
        self.geometry("850x650")  # Adjusted height to accommodate controls
        self.resizable(False, False)
        self.configure(bg=self.theme['bg_right_start'])

        self.date_str = self.app.selected_date.strftime("%Y-%m-%d")
        self.draw_path = os.path.join(self.app.drawings_dir, f"drawing_{self.date_str}.png")

        # Main frame for canvas and layers
        main_drawing_frame = tk.Frame(self, bg=self.theme['bg_right_start'])
        main_drawing_frame.pack(fill="both", expand=True)

        self.canvas_width, self.canvas_height = 600, 400
        self.canvas = tk.Canvas(main_drawing_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Layer management UI
        layer_frame = tk.Frame(main_drawing_frame, bg=self.theme['bg_right_start'], bd=2, relief="sunken")
        layer_frame.pack(side="right", fill="y", padx=(10, 0))
        tk.Label(layer_frame, text="Layers", font=self.app.font_main, bg=self.theme['bg_right_start'], fg=self.theme['text_fg']).pack(pady=5)
        self.layer_listbox = tk.Listbox(layer_frame, selectmode="browse", font=self.app.font_main, bg=self.theme['text_bg'], fg=self.theme['text_fg'])
        self.layer_listbox.pack(pady=5, padx=5, fill="y", expand=True)
        self.layer_listbox.bind("<<ListboxSelect>>", self.on_layer_select)

        layer_button_frame = tk.Frame(layer_frame, bg=self.theme['bg_right_start'])
        layer_button_frame.pack(pady=5)
        tk.Button(layer_button_frame, text="+", command=self.add_layer, bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=2)
        tk.Button(layer_button_frame, text="-", command=self.remove_layer, bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=2)
        tk.Button(layer_button_frame, text="↑", command=self.move_layer_up, bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=2)
        tk.Button(layer_button_frame, text="↓", command=self.move_layer_down, bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=2)

        self.layers = []
        self.active_layer_index = 0
        self.undo_stack = []
        self.redo_stack = []

        if os.path.exists(self.draw_path):
            self.load_drawing()
        else:
            self.add_layer("Background")

        self.update_layer_listbox()
        self.composite_layers()

        self.start_x, self.start_y = None, None
        self.preview_shape = None
        self.preview_circle = self.canvas.create_oval(0, 0, 0, 0, outline="black", width=1)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.update_preview)

        # Tools frame
        tools_frame = tk.Frame(self, bg=self.theme['bg_right_start'])
        tools_frame.pack(pady=5)

        self.tool_buttons = {}
        for tool_name in ["Brush", "Eraser", "Fill"]:
            btn = tk.Button(tools_frame, text=tool_name,
                            command=lambda t=tool_name.lower(): self.select_tool(t),
                            bg=self.theme['button_color'], activebackground=self.theme['active_button'])
            btn.pack(side="left", padx=5)
            self.tool_buttons[tool_name.lower()] = btn

        self.shape_var = tk.StringVar(value="Line")
        self.shape_options = ["Line", "Rectangle", "Oval", "Star", "Heart"]
        shape_menu = tk.OptionMenu(tools_frame, self.shape_var, *self.shape_options, command=self.select_shape_tool)
        shape_menu.pack(side="left", padx=5)
        self.tool_buttons["shape"] = shape_menu

        self.color_btn = tk.Button(tools_frame, text="Color", bg=self.app.brush_color, command=self.choose_color)
        self.color_btn.pack(side="left", padx=5)

        # Size and opacity frame
        self.size_frame = tk.Frame(self, bg=self.theme['bg_right_start'])
        self.size_frame.pack(pady=5)
        self.opacity_var = tk.IntVar(value=255)
        tk.Label(self.size_frame, text="Opacity", bg=self.theme['bg_right_start'], fg=self.theme['text_fg']).pack(side="left")
        tk.Scale(self.size_frame, from_=0, to=255, orient="horizontal", variable=self.opacity_var,
                 bg=self.theme['bg_right_start'], fg=self.theme['text_fg'], troughcolor=self.theme['button_color']).pack(side="left", padx=5)
        self.scale_var = tk.IntVar()
        self.update_size_frame()
        self.select_tool("brush")  # Select brush by default

        # Bottom actions
        action_frame = tk.Frame(self, bg=self.theme['bg_right_start'])
        action_frame.pack(pady=5)
        tk.Button(action_frame, text="Undo", command=self.undo_action, bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=5)
        tk.Button(action_frame, text="Redo", command=self.redo_action, bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=5)
        tk.Button(action_frame, text="Clear", command=self.clear_action, bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=5)
        tk.Button(action_frame, text="💾 Save", command=self.save_drawing, bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=5)

    def on_canvas_configure(self, event):
        new_width = event.width
        new_height = event.height
        if new_width != self.canvas_width or new_height != self.canvas_height:
            self.canvas_width = new_width
            self.canvas_height = new_height
            self.resize_layers()

    def resize_layers(self):
        for layer in self.layers:
            layer['image'] = layer['image'].resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)
        self.composite_layers()

    def on_press(self, event):
        self._save_state_for_undo()
        self.start_x, self.start_y = event.x, event.y
        if self.app.current_tool == "fill":
            self.fill(self.start_x, self.start_y)
        elif self.app.current_tool in ["line", "rectangle", "oval", "star", "heart"]:
            color = self.app.brush_color
            self.preview_shape = self.canvas.create_line(
                self.start_x, self.start_y, self.start_x, self.start_y, fill=color, width=int(self.app.brush_width)
            ) if self.app.current_tool == "line" else \
                self.canvas.create_rectangle(
                    self.start_x, self.start_y, self.start_x, self.start_y, outline=color, width=int(self.app.brush_width)
                ) if self.app.current_tool == "rectangle" else \
                self.canvas.create_oval(
                    self.start_x, self.start_y, self.start_x, self.start_y, outline=color, width=int(self.app.brush_width)
                ) if self.app.current_tool == "oval" else \
                self.draw_preview_shape(self.start_x, self.start_y, self.start_x, self.start_y)

    def on_drag(self, event):
        if self.app.current_tool == "brush" or self.app.current_tool == "eraser":
            self.paint(event)
        elif self.app.current_tool in ["line", "rectangle", "oval"] and self.preview_shape:
            self.canvas.coords(self.preview_shape, self.start_x, self.start_y, event.x, event.y)
        elif self.app.current_tool in ["star", "heart"] and self.preview_shape:
            self.canvas.delete(self.preview_shape)
            self.preview_shape = self.draw_preview_shape(self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.app.current_tool in ["line", "rectangle", "oval", "star", "heart"]:
            self.draw_shape(self.start_x, self.start_y, event.x, event.y)
            if self.preview_shape:
                self.canvas.delete(self.preview_shape)
                self.preview_shape = None
        self.start_x, self.start_y = None, None
        self.composite_layers()

    def get_brush_color(self):
        color = self.app.brush_color
        if isinstance(color, str) and color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return (r, g, b, int(self.opacity_var.get()))
        return (0, 0, 0, int(self.opacity_var.get()))

    def paint(self, event):
        x, y = event.x, event.y
        active_layer_image = self.layers[self.active_layer_index]['image']
        draw = ImageDraw.Draw(active_layer_image)
        color = self.get_brush_color() if self.app.current_tool == "brush" else (0, 0, 0, 0)
        width = self.app.brush_width if self.app.current_tool == "brush" else self.app.eraser_width
        if self.start_x is not None and self.start_y is not None:
            draw.line((self.start_x, self.start_y, x, y), fill=color, width=int(width))
        self.start_x, self.start_y = x, y
        self.update_preview(event)
        self.composite_layers()

    def fill(self, x, y):
        if self.layers:
            active_layer_image = self.layers[self.active_layer_index]['image']
            color_to_fill = self.get_brush_color()
            ImageDraw.floodfill(active_layer_image, (x, y), color_to_fill)
            self.composite_layers()

    def draw_shape(self, x1, y1, x2, y2):
        if self.layers:
            active_layer_image = self.layers[self.active_layer_index]['image']
            draw = ImageDraw.Draw(active_layer_image)
            color = self.get_brush_color()
            width = self.app.brush_width
            if self.app.current_tool == "line":
                draw.line((x1, y1, x2, y2), fill=color, width=int(width))
            elif self.app.current_tool == "rectangle":
                draw.rectangle((x1, y1, x2, y2), outline=color, width=int(width))
            elif self.app.current_tool == "oval":
                draw.ellipse((x1, y1, x2, y2), outline=color, width=int(width))
            elif self.app.current_tool == "star":
                self.draw_star(draw, x1, y1, x2, y2, color, int(width))
            elif self.app.current_tool == "heart":
                self.draw_heart(draw, x1, y1, x2, y2, color, int(width))

    def draw_preview_shape(self, x1, y1, x2, y2):
        color = self.app.brush_color
        width = int(self.app.brush_width)
        if self.app.current_tool == "star":
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            outer_radius = min(abs(x2 - x1), abs(y2 - y1)) / 2
            inner_radius = outer_radius / 2.5
            points = []
            for i in range(10):
                angle_deg = -90 + i * 36
                angle_rad = math.radians(angle_deg)
                radius = outer_radius if i % 2 == 0 else inner_radius
                points.append((cx + radius * math.cos(angle_rad), cy + radius * math.sin(angle_rad)))
            return self.canvas.create_polygon(points, fill="", outline=color, width=width)
        elif self.app.current_tool == "heart":
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            width_h = abs(x2 - x1)
            height_h = abs(y2 - y1)
            points = []
            for i in range(0, 100):
                t = 2 * math.pi * i / 100
                x = cx + width_h/20 * (16 * math.sin(t)**3)
                y = cy - height_h/20 * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
                points.append((x, y))
            return self.canvas.create_line(points, fill=color, width=width, joinstyle="round")

    def draw_star(self, draw, x1, y1, x2, y2, color, width):
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        outer_radius = min(abs(x2 - x1), abs(y2 - y1)) / 2
        inner_radius = outer_radius / 2.5
        points = []
        for i in range(10):
            angle_deg = -90 + i * 36
            angle_rad = math.radians(angle_deg)
            radius = outer_radius if i % 2 == 0 else inner_radius
            points.append((cx + radius * math.cos(angle_rad), cy + radius * math.sin(angle_rad)))
        draw.polygon(points, outline=color, width=width)

    def draw_heart(self, draw, x1, y1, x2, y2, color, width):
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        width_h = abs(x2 - x1)
        height_h = abs(y2 - y1)
        points = []
        for i in range(0, 100):
            t = 2 * math.pi * i / 100
            x = cx + width_h/20 * (16 * math.sin(t)**3)
            y = cy - height_h/20 * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            points.append((x, y))
        draw.line(points, fill=color, width=width, joint="curve")

    def update_preview(self, event=None):
        if event:
            x, y = event.x, event.y
        else:
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        if self.app.current_tool == "brush" or self.app.current_tool == "eraser":
            width = self.app.brush_width if self.app.current_tool == "brush" else self.app.eraser_width
            radius = width / 2
            color = self.app.brush_color if self.app.current_tool == "brush" else "gray"
            self.canvas.coords(self.preview_circle, x - radius, y - radius, x + radius, y + radius)
            self.canvas.itemconfig(self.preview_circle, outline=color)
            self.canvas.tag_raise(self.preview_circle)
        else:
            self.canvas.coords(self.preview_circle, -10, -10, -10, -10)

    def select_tool(self, tool):
        self.app.current_tool = tool
        for t, btn in self.tool_buttons.items():
            if t != "shape":
                btn.config(bg=self.theme['active_button'] if t == tool else self.theme['button_color'])
        self.update_size_frame()

    def select_shape_tool(self, shape):
        self.select_tool(shape.lower())

    def update_size_frame(self):
        for widget in self.size_frame.winfo_children():
            widget.destroy()
        tk.Label(self.size_frame, text="Opacity", bg=self.theme['bg_right_start'], fg=self.theme['text_fg']).pack(side="left")
        tk.Scale(self.size_frame, from_=0, to=255, orient="horizontal", variable=self.opacity_var,
                 bg=self.theme['bg_right_start'], fg=self.theme['text_fg'], troughcolor=self.theme['button_color']).pack(side="left", padx=5)
        if self.app.current_tool in ["brush", "eraser", "line", "rectangle", "oval", "star", "heart"]:
            preset_sizes = [1, 5, 10, 20]
            for s in preset_sizes:
                tk.Button(self.size_frame, text=str(s),
                          command=lambda val=s: self.set_size(val, update_slider=True),
                          bg=self.theme['button_color'], activebackground=self.theme['active_button']).pack(side="left", padx=2)
            current_width = self.app.brush_width if self.app.current_tool in ["brush", "line", "rectangle", "oval", "star", "heart"] else self.app.eraser_width
            self.scale_var.set(int(current_width))
            scale = tk.Scale(self.size_frame, from_=1, to=50, orient="horizontal", resolution=1,
                             variable=self.scale_var,
                             command=lambda val: self.set_size(int(val), update_slider=False),
                             bg=self.theme['bg_right_start'], fg=self.theme['text_fg'], troughcolor=self.theme['button_color'])
            scale.pack(side="left", padx=5)

    def set_size(self, val, update_slider=True):
        if self.app.current_tool in ["brush", "line", "rectangle", "oval", "star", "heart"]:
            self.app.brush_width = int(val)
        elif self.app.current_tool == "eraser":
            self.app.eraser_width = int(val)
        if update_slider:
            self.scale_var.set(int(val))

    def choose_color(self):
        color = colorchooser.askcolor(color=self.app.brush_color, parent=self)[1]
        if color:
            self.app.brush_color = color
            self.color_btn.config(bg=color)

    def _save_state_for_undo(self):
        if self.layers:
            active_layer_image = self.layers[self.active_layer_index]['image']
            self.undo_stack.append(active_layer_image.copy())
            self.redo_stack.clear()

    def undo_action(self):
        if self.undo_stack:
            current_image = self.layers[self.active_layer_index]['image']
            self.redo_stack.append(current_image)
            self.layers[self.active_layer_index]['image'] = self.undo_stack.pop()
            self.composite_layers()

    def redo_action(self):
        if self.redo_stack:
            current_image = self.layers[self.active_layer_index]['image']
            self.undo_stack.append(current_image)
            self.layers[self.active_layer_index]['image'] = self.redo_stack.pop()
            self.composite_layers()

    def clear_action(self):
        if self.layers:
            active_layer_image = self.layers[self.active_layer_index]['image']
            draw = ImageDraw.Draw(active_layer_image)
            draw.rectangle([0, 0, self.canvas_width, self.canvas_height], fill=(0, 0, 0, 0))
            self.composite_layers()

    def save_drawing(self):
        final_image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (255, 255, 255, 255))
        for layer in reversed(self.layers):
            final_image.alpha_composite(layer['image'])
        final_image.convert("RGB").save(self.draw_path)

    def load_drawing(self):
        try:
            loaded_image = Image.open(self.draw_path).convert("RGBA")
            self.add_layer("Loaded Drawing", image=loaded_image)
        except FileNotFoundError:
            self.add_layer("Background")

    def add_layer(self, name=None, image=None):
        if name is None:
            name = f"Layer {len(self.layers) + 1}"
        if image is None:
            image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        insert_index = self.active_layer_index
        self.layers.insert(insert_index, {'name': name, 'image': image})
        self.active_layer_index = insert_index
        self.update_layer_listbox()
        self.composite_layers()

    def remove_layer(self):
        if len(self.layers) > 0 and self.active_layer_index is not None:
            self.layers.pop(self.active_layer_index)
            if self.active_layer_index >= len(self.layers):
                self.active_layer_index = len(self.layers) - 1
            if not self.layers:
                self.add_layer("Background")
            self.update_layer_listbox()
            self.composite_layers()

    def move_layer_up(self):
        if self.active_layer_index > 0:
            self.layers.insert(self.active_layer_index - 1, self.layers.pop(self.active_layer_index))
            self.active_layer_index -= 1
            self.update_layer_listbox()
            self.composite_layers()

    def move_layer_down(self):
        if self.active_layer_index < len(self.layers) - 1:
            self.layers.insert(self.active_layer_index + 1, self.layers.pop(self.active_layer_index))
            self.active_layer_index += 1
            self.update_layer_listbox()
            self.composite_layers()

    def on_layer_select(self, event):
        if self.layer_listbox.curselection():
            self.active_layer_index = self.layer_listbox.curselection()[0]

    def update_layer_listbox(self):
        self.layer_listbox.delete(0, "end")
        for i, layer in enumerate(self.layers):
            self.layer_listbox.insert("end", layer['name'])
            if i == self.active_layer_index:
                self.layer_listbox.selection_set(i)
                self.layer_listbox.activate(i)

    def composite_layers(self):
        composite_image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (255, 255, 255, 255))
        for layer in reversed(self.layers):
            composite_image.alpha_composite(layer['image'])
        self.tk_img = ImageTk.PhotoImage(composite_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_img, anchor="nw")
        self.preview_circle = self.canvas.create_oval(0, 0, 0, 0, outline="black", width=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiaryApp(root)
    root.mainloop()