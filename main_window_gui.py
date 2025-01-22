import customtkinter as tk
from customtkinter import *
from PIL import Image
import app2

tk.set_appearance_mode("light")

app = tk.CTk()
app.title("Welcome to Buddhi AI! ~ Onboarding Screen")
app.grid_rowconfigure(0, weight=1)


#display logo
start_img=CTkImage(light_image=Image.open("BuddhiAi.png"), size=(500,500))
disp = CTkLabel(app, image=start_img, text="")
disp.grid(row=0, column=0)

#display button to move to main window
def starter():
    app.destroy()
    app3 = app2.App()
    app3.mainloop()

def ender():
    app.destroy()
    self.destroy()


go_but = tk.CTkButton(master=app, text="Let's Go!", command=starter, hover_color="#f49a31",fg_color="#f49a31", font=("Comic Sans",20))
go_but.grid(row=1, column=0)
app.mainloop()