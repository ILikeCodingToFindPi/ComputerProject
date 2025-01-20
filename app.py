import tkinter as tk
from tkinter import Canvas, colorchooser, filedialog, messagebox
from tkinter.simpledialog import askstring
from PIL import Image, ImageDraw, ImageTk
from collections import deque
import main_window_gui

class NotebookGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Buddhi.AI ~ Notepad")
        self.geometry("1000x800")
        self.iconbitmap(bitmap="Buddhi.ico")

        self.pen_color = "black"
        self.pen_width = 2
        self.current_tool = "pen"
        self.bg_color = "white"
        self.eraser_width = 20

        self.canvas = Canvas(self, bg=self.bg_color, cursor="pencil")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.bind('<Configure>', self.resize_canvas)

        self.image = Image.new("RGB", (self.winfo_width(), self.winfo_height()), self.bg_color)
        self.draw_image = ImageDraw.Draw(self.image)

        self.undo_stack = deque()
        self.redo_stack = deque()

        self.last_x, self.last_y = None, None
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        self.canvas.bind("<Button-3>", self.add_text)

        self.create_toolbox()
        self.create_menu()
        self.create_ruled_lines()

    def create_toolbox(self):
        toolbox = tk.Frame(self, bg="lightgray", padx=5, pady=5)
        toolbox.place(x=0, y=0, relwidth=1)

        color_btn = tk.Button(toolbox, text="Color", command=self.choose_color, bg="white", relief=tk.FLAT)
        color_btn.pack(side=tk.LEFT, padx=5)

        pen_size_scale = tk.Scale(toolbox, from_=1, to=10, orient=tk.HORIZONTAL, label="Pen Size", command=self.change_pen_size, bg="white")
        pen_size_scale.set(self.pen_width)
        pen_size_scale.pack(side=tk.LEFT, padx=5)

        pen_btn = tk.Button(toolbox, text="Pen", command=self.select_pen, bg="white", relief=tk.FLAT)
        pen_btn.pack(side=tk.LEFT, padx=5)

        eraser_btn = tk.Button(toolbox, text="Eraser", command=self.select_eraser, bg="white", relief=tk.FLAT)
        eraser_btn.pack(side=tk.LEFT, padx=5)

        undo_btn = tk.Button(toolbox, text="Undo", command=self.undo, bg="white", relief=tk.FLAT)
        undo_btn.pack(side=tk.LEFT, padx=5)

        redo_btn = tk.Button(toolbox, text="Redo", command=self.redo, bg="white", relief=tk.FLAT)
        redo_btn.pack(side=tk.LEFT, padx=5)

    def create_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

    def choose_color(self):
        self.pen_color = colorchooser.askcolor(color=self.pen_color)[1]

    def change_pen_size(self, size):
        self.pen_width = int(size)

    def select_pen(self):
        self.current_tool = "pen"
        self.canvas.config(cursor="pencil")

    def select_eraser(self):
        self.current_tool = "eraser"
        self.canvas.config(cursor="circle")

    def resize_canvas(self, event):
        if event.width > self.image.width or event.height > self.image.height:
            new_image = Image.new("RGB", (event.width, event.height), self.bg_color)
            new_image.paste(self.image, (0, 0))
            self.image = new_image
            self.draw_image = ImageDraw.Draw(self.image)
        self.update_canvas()

    def create_ruled_lines(self):
        line_distance = 30
        for y in range(line_distance, self.canvas.winfo_height(), line_distance):
            self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill="#A8C5F7", width=1)

    def draw(self, event):
        if self.current_tool == "pen":
            if self.last_x and self.last_y:
                self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=self.pen_color, width=self.pen_width)
                self.draw_image.line((self.last_x, self.last_y, event.x, event.y), fill=self.pen_color, width=self.pen_width)
        
        elif self.current_tool == "eraser":
            if self.last_x and self.last_y:
                self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=self.bg_color, width=self.eraser_width)
                self.draw_image.line((self.last_x, self.last_y, event.x, event.y), fill=self.bg_color, width=self.eraser_width)
            
        self.last_x, self.last_y = event.x, event.y

    def reset(self, event):
        self.last_x, self.last_y = None, None
        self.push_undo()

    def add_text(self, event):
        text = askstring("Input", "Enter text:")
        if text:
            self.canvas.create_text(event.x, event.y, text=text, fill=self.pen_color, font=("Arial", self.pen_width * 4))
            self.draw_image.text((event.x, event.y), text, fill=self.pen_color)
        self.push_undo()

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.image.save(file_path)
            messagebox.showinfo("Save", "File saved successfully!")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.image = Image.open(file_path)
            self.draw_image = ImageDraw.Draw(self.image)
            self.update_canvas()
        self.push_undo()

    def push_undo(self):
        self.undo_stack.append(self.image.copy())
        if len(self.undo_stack) > 10:
            self.undo_stack.popleft()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.draw_image = ImageDraw.Draw(self.image)
            self.update_canvas()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.draw_image = ImageDraw.Draw(self.image)
            self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        self.canvas_img = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_img)
        self.create_ruled_lines()

if __name__ == "__main__":
    notebook = NotebookGUI()
    notebook.mainloop()
