import tkinter as t
from tkinter import Canvas, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import requests
from collections import deque
import ollama
import json
import textwrap
def clickresize(event):
        s.canvas.config(width=event.width, height=event.height)

class App(t.Tk):
    def __init__(s):
        global model
        model = "phi"
        super().__init__()
        s.title("Notepad")
        s.geometry("1000x800")
        s.color = "black"
        s.width = 2
        s.tool = "pen"
        s.bg = "white"
        s.eraserSize = 20
        s.undoStack = deque()
        s.redoStack = deque()
        s.lastX, s.lastY = None, None
        s.canvas = Canvas(s, bg=s.bg, cursor="pencil")
        s.canvas.pack(fill=t.BOTH, expand=True)
        s.img = Image.new("RGB", (1000, 800), s.bg)
        s.draw = ImageDraw.Draw(s.img)
        s.canvas.bind('<B1-Motion>', s.drawLine)
        s.canvas.bind('<ButtonRelease-1>', s.resetPos)
        s.bind('<Configure>', s.resize)
        s.bind('<Configure>', clickresize)
        s.startX, s.startY = None, None
        s.rect = None
        s._drag_data = {"x": 0, "y": 0, "item": None}
        s.toolbar()
        s.menu()

    def toolbar(s):
        bar = t.Frame(s, bg="gray")
        bar.place(x=0, y=0, relwidth=1)
        t.Button(bar, text="Color", command=s.pickColor).pack(side=t.LEFT, padx=5)
        t.Scale(bar, from_=1, to=10, orient=t.HORIZONTAL, command=s.setWidth).pack(side=t.LEFT, padx=5)
        t.Button(bar, text="Pen", command=lambda: s.setTool("pen")).pack(side=t.LEFT, padx=5)
        t.Button(bar, text="Eraser", command=lambda: s.setTool("eraser")).pack(side=t.LEFT, padx=5)
        t.Button(bar, text="Undo", command=s.undo).pack(side=t.LEFT, padx=5)
        t.Button(bar, text="Redo", command=s.redo).pack(side=t.LEFT, padx=5)
        t.Button(bar, text="Snip", command=s.snip).pack(side=t.LEFT, padx=5)

    def menu(s):
        menu = t.Menu(s)
        fileMenu = t.Menu(menu, tearoff=0)
        fileMenu.add_command(label="Save", command=s.save)
        fileMenu.add_command(label="Open", command=s.load)
        fileMenu.add_command(label="Exit", command=s.quit)
        menu.add_cascade(label="File", menu=fileMenu)
        s.config(menu=menu)

    def snip(s):
        s.tool = "snip"
        s.canvas.bind("<ButtonPress-1>", s.startSnip)
        s.canvas.bind("<B1-Motion>", s.snipMotion)
        s.canvas.bind("<ButtonRelease-1>", s.endSnip)

    def startSnip(s, e):
        s.startX, s.startY = e.x, e.y
        s.rect = s.canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="red", width=2)

    def snipMotion(s, e):
        s.canvas.coords(s.rect, s.startX, s.startY, e.x, e.y)
       
    def endSnip(s, e):
        x1, y1, x2, y2 = s.startX, s.startY, e.x, e.y
        cropped = s.img.crop((x1, y1, x2, y2))
        cropped.save("snip.png")
        result = ocr("snip.png")
        text = extractText(result)
        if text.strip():
            response = ask(text)
            response_lines = textwrap.wrap(response, width=50)  
            formatted_text = "\n".join(response_lines)
            text_id = s.canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=formatted_text,
                fill="blue",
                font=("Arial", 12),
                anchor="nw",
                tags="draggable_text"
            )
            s._drag_data = {"x": 0, "y": 0, "item": text_id}
           # text_id.pack(padx=5, pady=15, side=tk.LEFT)

            
            s.canvas.tag_bind("draggable_text", "<ButtonPress-1>", s._on_drag_start)
            s.canvas.tag_bind("draggable_text", "<B1-Motion>", s._on_drag_motion)
        else:
            messagebox.showwarning("Error", "No text found.")

        
        s.canvas.delete(s.rect)
        s.rect = None
        s.startX, s.startY = None, None
        s.setTool("pen")
        s.canvas.bind('<B1-Motion>', s.drawLine)
        s.canvas.bind('<ButtonRelease-1>', s.resetPos)

    def _on_drag_start(s, event):
        s._drag_data["item"] = s.canvas.find_withtag("current")[0]
        s._drag_data["x"] = event.x
        s._drag_data["y"] = event.y

        
        s.tool = None

    def _on_drag_motion(s, event):
        delta_x = event.x - s._drag_data["x"]
        delta_y = event.y - s._drag_data["y"]
        s.canvas.move(s._drag_data["item"], delta_x, delta_y)
        s._drag_data["x"] = event.x
        s._drag_data["y"] = event.y

    def drawLine(s, e):
        if s.tool == "pen" and s.lastX and s.lastY:
            color = s.color
            width = s.width
            s.canvas.create_line(s.lastX, s.lastY, e.x, e.y, fill=color, width=width)
            s.draw.line((s.lastX, s.lastY, e.x, e.y), fill=color, width=width)
        elif s.tool == "eraser" and s.lastX and s.lastY:
            color = s.bg
            width = s.eraserSize
            s.canvas.create_line(s.lastX, s.lastY, e.x, e.y, fill=color, width=width)
            s.draw.line((s.lastX, s.lastY, e.x, e.y), fill=color, width=width)
        s.lastX, s.lastY = e.x, e.y

    def resetPos(s, e):
        s.lastX, s.lastY = None, None
        s.undoStack.append(s.img.copy())

    def pickColor(s):
        s.color = colorchooser.askcolor()[1]

    def setWidth(s, v):
        s.width = int(v)

    def setTool(s, t):
        s.tool = t

    def resize(s, e):
        if e.width > s.img.width or e.height > s.img.height:
            newImg = Image.new("RGB", (e.width, e.height), s.bg)
            newImg.paste(s.img, (0, 0))
            s.img = newImg
            s.draw = ImageDraw.Draw(s.img)
        s.update()

    def undo(s):
        if s.undoStack:
            s.redoStack.append(s.img.copy())
            s.img = s.undoStack.pop()
            s.draw = ImageDraw.Draw(s.img)
        s.update()

    def redo(s):
        if s.redoStack:
            s.undoStack.append(s.img.copy())
            s.img = s.redoStack.pop()
            s.draw = ImageDraw.Draw(s.img)
        s.update()

    def save(s):
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            s.img.save(path)

    def load(s):
        path = filedialog.askopenfilename()
        if path:
            s.img = Image.open(path)
            s.draw = ImageDraw.Draw(s.img)
        s.update()

    def update(s):
        s.canvas.delete("all")
        s.tkImg = ImageTk.PhotoImage(s.img)
        s.canvas.create_image(0, 0, anchor=t.NW, image=s.tkImg)


def ocr(file, overlay=True, key='K82693734788957', lang='eng'):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': key,
        'language': lang,
        'OCREngine': 2
    }
    with open(file, 'rb') as f:
        res = requests.post('https://api.ocr.space/parse/image', files={file: f}, data=payload)
    return res.content.decode()

def extractText(res):
    try:
        data = json.loads(res)
        results = data.get('ParsedResults', [])
        if not results:
            return "No text found."
        text = ""
        for r in results:
            text += r.get('ParsedText', '') + '\n'
        return text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def ask(q):
    global model
    try:
        res = ollama.chat(model=model, messages=[{'role': 'user', 'content': q}], stream=False)
        return res.get('message', {}).get('content', "No valid response.")
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app = App()
    app.mainloop()
