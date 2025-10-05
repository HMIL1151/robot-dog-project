import os
import tkinter as tk
from PIL import Image, ImageTk

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    return os.path.join(script_dir, relative_path)

root = tk.Tk()
root.title("Button Highlighter")

def load_and_scale(path, width, height):
    img = Image.open(path)
    img = img.resize((width, height))
    return ImageTk.PhotoImage(img)

button_width, button_height = 64, 64

button_off = load_and_scale(resource_path("sprites/button_off.png"), button_width, button_height)
button_on = load_and_scale(resource_path("sprites/button_on.png"), button_width, button_height)

canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack()

up_button = canvas.create_image(200, 100, image=button_off)
down_button = canvas.create_image(200, 300, image=button_off)

buttons = {
    "w": (up_button, button_off, button_on),
    "s": (down_button, button_off, button_on)    
    }

def on_key_press(event):
    if event.keysym in buttons:
        item, off_img, on_img = buttons[event.keysym]
        canvas.itemconfig(item, image=on_img)

def on_key_release(event):
    if event.keysym in buttons:
        item, off_img, on_img = buttons[event.keysym]
        canvas.itemconfig(item, image=off_img)

root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

root.mainloop()
