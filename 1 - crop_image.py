import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image

class ImageCropper:
    def __init__(self, crop_size):
        """
        Initialize ImageCropper instance.

        Args:
            crop_size (tuple): A tuple of two integers (width, height) defining the
                desired crop size.
        """
        self.crop_size = crop_size

    def _prepare_output_folder(self, output_folder):
        """Create output folder if needed."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    def _crop_image(self, image, filename):
        """Crop a single image."""
        # Get image dimensions
        image_width, image_height = image.size

        # Calculate center coordinates for crop box (half of width and height)
        center_x = int(image_width / 2)
        center_y = int(image_height / 2)

        # Calculate crop box coordinates based on desired size and center
        crop_box = (
            center_x - int(self.crop_size[0] / 2),  # x_min (center - half width)
            center_y - int(self.crop_size[1] / 2),  # y_min (center - half height)
            center_x + int(self.crop_size[0] / 2),  # x_max (center + half width)
            center_y + int(self.crop_size[1] / 2),  # y_max (center + half height)
        )

        # Crop image using the calculated box
        cropped_image = image.crop(crop_box)

        return cropped_image

    def crop_file(self):
        """Crop a single image file."""
        # Open file explorer to select an image
        root = tk.Tk()
        root.withdraw()
        self.file_path = filedialog.askopenfilename(filetypes=[("Image Files", ("*.jpg", "*.jpeg", "*.png"))])

        if not self.file_path:
            print("No file selected.")
            return

        output_folder = filedialog.askdirectory(title="Select output folder")
        if not output_folder:
            print("No output folder selected.")
            return

        output_filename = filedialog.asksaveasfilename(defaultextension=".jpg", title="Select output file name and format", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if not output_filename:
            print("No output file selected.")
            return

        try:
            # Open image
            image = Image.open(self.file_path)

            # Crop image
            cropped_image = self._crop_image(image, os.path.basename(self.file_path))

            # Save cropped image
            cropped_image.save(output_filename)
            print(f"Image cropped: {os.path.basename(self.file_path)} -> {os.path.basename(output_filename)}")
        except (IOError, OSError) as e:
            print(f"Error cropping image {os.path.basename(self.file_path)}: {e}")

# Example usage
crop_size = (1100, 1100)  # Example crop size (width, height)

cropper = ImageCropper(crop_size)
cropper.crop_file()  # Open file explorer and crop a single image