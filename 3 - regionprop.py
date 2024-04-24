import os
import cv2
import numpy as np
import pandas as pd
from skimage import measure, color, io
from UNet_Model import unet_model
from keras.utils import normalize
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, simpledialog

class CoffeeBeanAnalyzer:
    def __init__(self, img_height, img_width, img_channels):
        self.IMG_HEIGHT = img_height
        self.IMG_WIDTH = img_width
        self.IMG_CHANNELS = img_channels
        self.model = self.get_model()
        self.model.load_weights('unet_model/coffee_bean_test-20.hdf5')

    def get_model(self):
        return unet_model(self.IMG_HEIGHT, self.IMG_WIDTH, self.IMG_CHANNELS)

    def load_and_process_image(self, filepath):
        img = cv2.imread(filepath, 0)
        img_norm = np.expand_dims(normalize(np.array(img), axis=1), 2)
        img_norm = img_norm[:, :, 0][:, :, None]
        img_input = np.expand_dims(img_norm, 0)
        return img_input

    def segment_image(self, img):
        return (self.model.predict(img)[0, :, :, 0] > 0.9).astype(np.uint8)

    def save_segmented_image(self, segmented, output_filename):
        plt.imsave(output_filename, segmented, cmap='gray')

    def apply_watershed_algorithm(self, img):
        img_grey = img[:, :, 0]
        ret1, thresh = cv2.threshold(img_grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=10)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        ret2, sure_fg = cv2.threshold(dist_transform, 0.01 * dist_transform.max(), 255, 0)
        sure_fg = np.array(sure_fg, dtype=np.uint8)
        unknown = cv2.subtract(sure_bg, sure_fg, dtype=cv2.CV_32S)
        ret3, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 10
        markers[unknown == 255] = 0
        cv2.watershed(img, markers)
        return markers

    def extract_properties(self, markers, img):
        props = measure.regionprops_table(markers, intensity_image=img[:, :, 0],
                                          properties=['area', 'perimeter', 'equivalent_diameter', 'extent', 'mean_intensity', 'solidity', 'convex_area', 'axis_major_length', 'axis_minor_length', 'eccentricity'])
        return props

    def create_dataframe(self, props, class_label, filepath):
        df = pd.DataFrame(props)
        df = df[df.mean_intensity > 100]
        df['class_label'] = class_label
        image_id = os.path.basename(filepath)
        df= df[['area', 'perimeter', 'equivalent_diameter', 'extent', 'mean_intensity', 'solidity', 'convex_area', 'axis_major_length', 'axis_minor_length', 'eccentricity', 'class_label']]
        df.insert(1, 'filepath', filepath)
        df.insert(2, 'image_id', image_id)
        return df

    def get_user_input(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        class_label = simpledialog.askstring(title="Class Label", prompt="Enter the class label (Farm) for the selected image (Katy, Mukring, Saludo, or Tunying):")
        return file_path, class_label

    def get_current_index(self, csv_file):
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            if not df.empty:
                return df.index[-1] + 1
        return 0

if __name__ == '__main__':
    analyzer = CoffeeBeanAnalyzer(img_height=256, img_width=256, img_channels=1)
    file_path, class_label = analyzer.get_user_input()
    img = analyzer.load_and_process_image(file_path)
    segmented = analyzer.segment_image(img)
    output_filename = os.path.join('for_watershed', f'{os.path.basename(file_path)}')
    analyzer.save_segmented_image(segmented, output_filename)
    img = cv2.imread(output_filename)
    markers = analyzer.apply_watershed_algorithm(img)
    props = analyzer.extract_properties(markers, img)
    df = analyzer.create_dataframe(props, class_label, file_path)
    csv_file = 'metadata/liberica_bean_metadata.csv'
    index = analyzer.get_current_index(csv_file)
    df.insert(0, 'index', index)
    df.set_index('index', inplace=True)
    df.to_csv(csv_file, mode='a', header=False)