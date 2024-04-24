import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog

class ImageResizer:
    def __init__(self):
        self.input_folder = None
        self.output_folder = None
        self.width = 256
        self.height = 256
        self.counter = 1

    def _create_output_folder(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def _resize_image(self, img_path):
        img = Image.open(img_path)
        img_resized = img.resize((self.width, self.height))
        return img_resized

    def select_files(self):
        root = tk.Tk()
        root.withdraw()
        files = filedialog.askopenfilenames(title="Select files to resize", filetypes=[("Image Files", ("*.png", "*.jpg", "*.jpeg"))])
        return files

    def resize_files(self, files=None):
        if files is None:
            files = self.select_files()
        self.output_folder = filedialog.askdirectory(title="Select output folder")
        self._create_output_folder()
        for filename in files:
            img_path = filename
            img_resized = self._resize_image(img_path)
            output_filename = filedialog.asksaveasfilename(defaultextension=".png", title="Select output file name and format", filetypes=[("PNG", "*.png")], initialfile=os.path.basename(filename))
            if not output_filename:
                print("No output file selected.")
                continue
            print(f'Processed {os.path.basename(filename)} and resized to {output_filename}')
            img_resized.save(output_filename)  # Save the resized image

# Create an instance of the ImageResizer class and call the resize_files method
resizer = ImageResizer()
resizer.resize_files()