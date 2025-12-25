import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Load the image
class get_maze:
    def maze(self, image_path):
        image = Image.open(image_path).convert("L")  # Convert to grayscale

        # Resize the image
        image_resized = image.resize((256,256))

        # Convert to numpy array
        image_array = np.array(image_resized)

        # Apply threshold to create binary matrix (0 for white areas, 1 for dark areas)
        threshold = 200
        binary_matrix = (image_array > threshold).astype(int)

        return binary_matrix

