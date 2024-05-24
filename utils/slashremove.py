import numpy as np
from PIL import Image, ImageDraw, ImageTk, ImageOps
import requests
import urllib
from io import BytesIO

response = requests.get("https://media.discordapp.net/attachments/1091162329720295557/1093941179172786196/3695752.png?width=947&height=533")
# Create the main window
root = tk.Tk()
root.geometry("800x600")
root.title("My App")
images = []
def create_rectangle(x,y,a,b,**options):
   if 'alpha' in options:
      # Calculate the alpha transparency for every color(RGB)
      alpha = int(options.pop('alpha') * 255)
      # Use the fill variable to fill the shape with transparent color
      fill = options.pop('fill')
      fill = root.winfo_rgb(fill) + (alpha,)
      image = Image.new('RGBA', (a-x, b-y), fill)
      images.append(ImageTk.PhotoImage(image))
      canvas.create_image(x, y, image=images[-1], anchor='nw')
      canvas.create_rectangle(x, y,a,b, **options)
# Load the background image and display it on a canvas
bg_image = Image.open(BytesIO(response.content))
bg_photo = ImageTk.PhotoImage(bg_image)
canvas = tk.Canvas(root, width=800, height=600)
canvas.create_image(0, 0, image=bg_photo, anchor=tk.NW)

# Add a circle on the top left and insert the logo inside it
#circle = canvas.create_oval(100, 100, 140, 140, outline="#f11",
#            fill="#1f1", width=3)
logo_res = requests.get("https://cdn.discordapp.com/avatars/978930369392951366/a_f604ee928488d76c1706bf4b751c2355.png")
img = Image.open(BytesIO(logo_res.content)).convert("RGB")
img = img.resize((100,100), Image.Resampling.LANCZOS)
arrImg = np.array(img) #convert to numpy array
alph = Image.new('L', img.size, 0) #create a new image with alpha channel
draw = ImageDraw.Draw(alph) #create a draw object
draw.pieslice([0, 0, img.size[0], img.size[1]], 0, 360, fill = 255) #create a circle
arAlpha = np.array(alph) #conver to numpy array
arrImg = np.dstack((arrImg, arAlpha))
logo_image = Image.fromarray(arrImg)
logo_photo = ImageTk.PhotoImage(logo_image)
canvas.create_image(140, 125, image=logo_photo, anchor=tk.CENTER)

# Add the "Anay.#0314" text
canvas.create_text(200, 100, text="Anay.#0314", font=("Arial", 16), anchor=tk.W)

# Add the Spotify, Soundcloud, and Deezer logos
spotify_res = requests.get("https://images-ext-1.discordapp.net/external/bA1me4gujZdwhhuxzyz4kP3W04Fp7R-9gEWMIeYm81E/https/cdn.discordapp.com/emojis/702156457218670698.png")
spotify_image = Image.open(BytesIO(spotify_res.content))
resized_image= spotify_image.resize((25,25), Image.Resampling.LANCZOS)
spotify_photo = ImageTk.PhotoImage(resized_image)
canvas.create_image(210, 150, image=spotify_photo, anchor=tk.CENTER)

# Add the left box with the "TOP SERVER" text and the format below it
left_box = create_rectangle(50, 200, 400, 300, fill="black", outline="", alpha=.5)
canvas.create_text(225, 210, text="TOP SERVER", font=("Arial", 16), fill="white", anchor=tk.CENTER)
canvas.create_text(225, 230, text="1. 1h 56m - Special Ones <3", font=("Arial", 12), fill="white", anchor=tk.CENTER)

# Add the right box with the "TOP FRIENDS" text and the format below it
right_box = create_rectangle(420, 200, 770, 300, fill="black", outline="", alpha=.5)
canvas.create_text(595, 210, text="TOP FRIENDS", font=("Arial", 16), fill="white", anchor=tk.CENTER)
canvas.create_text(595, 230, text="1. 1h 56m - Special Ones <3", font=("Arial", 12), fill="white", anchor=tk.CENTER)

# Add the bottom box with the "TOP TRACKS" text and the format below it
bottom_box = create_rectangle(50, 320, 770, 500, fill="black", outline="", alpha=.5)
canvas.create_text(410, 330, text="TOP TRACKS", font=("Arial", 16), fill="white", anchor=tk.CENTER)
canvas.create_text(410, 350, text="1. 1h 56m - Special Ones <3", font=("Arial", 12), fill="white", anchor=tk.CENTER)

canvas.pack()
root.mainloop()