import tkinter as tk
from tkinter import Label, Toplevel
from PIL import Image, ImageTk
from tkinter import Tk, Toplevel, Label, Button
from PIL import Image, ImageTk

class Select:
    def __init__(self):
        self.selected_image_name = None  # Store selected image name
        self.selected_image_path = None  # Store selected image path
        self.popup = None  # Store popup reference


    def display(self):
        image_files = {
            "house1": "images/house1.jpg",
            "house2": "images/house2.jpg",
            "house3": "images/house3.jpg",
            "house4": "images/house4.jpg",
            "house5": "images/image5.jpg",
            "house6": "images/image6.jpg",
            "house7": "images/image7.jpg",
            "house8": "images/image10.png",
            "house9": "images/image9.png",
        }

        tk_images = {}

        def open_popup():
            """Opens a popup window for image selection."""
            self.popup = Toplevel(root)
            self.popup.title("Select an Image")
            self.popup.geometry("566x600")
            self.popup.configure(bg="#001845")

            def on_select(image_name):
                """Updates the selected image in the main window and closes the popup."""
                self.selected_image_name = image_name  
                self.selected_image_path = image_files[image_name]  

                selected_image.config(text=f"Selected: {image_name}")
                img = Image.open(self.selected_image_path).resize((300, 300))
                tk_img = ImageTk.PhotoImage(img)

                image_label.config(image=tk_img)
                image_label.image = tk_img  

                if self.popup:
                    self.popup.destroy()  

            # Arrange images in a 3×3 grid
            row, col = 0, 0
            for idx, (name, path) in enumerate(image_files.items()):
                img = Image.open(path).resize((160, 160))
                tk_img = ImageTk.PhotoImage(img)
                tk_images[name] = tk_img  

                btn = Button(self.popup, text=name, image=tk_img, compound="top", command=lambda n=name: on_select(n))
                btn.grid(row=row, column=col, padx=10, pady=10)

                col += 1
                if col > 2:  # Reset column after 3 images
                    col = 0
                    row += 1

            self.popup.mainloop()

        def proceed():
            """Return the selected image path when Proceed is clicked."""
            if self.selected_image_path:
                print(f"Proceeding with image path: {self.selected_image_path}")  # Modify this action as needed
                root.quit()  # Close the main window after proceeding
                return self.selected_image_path
            else:
                print("No image selected. Please select an image first.")

        # Create main Tkinter window
        root = tk.Tk()
        root.title("Image Selector")
        root.geometry("600x600")
        root.configure(bg="#272640")

        # Button to open the pop-up
        open_popup_btn = tk.Button(
            root, 
            text="Select Image", 
            command=open_popup, 
            bg="#ffffb3",   # Background color
            fg="#023e7d",   # Text color
            font=("Arial", 12, "bold"),  # Font style
            padx=10,  # Padding for width
            pady=5,   # Padding for height
            relief="raised",  # Button border style
            bd=3,  # Border thickness
        )

        open_popup_btn.pack(pady=20)

        # Label to show the selected image
        selected_image = Label(root, text="No image selected", font=("Times New Roman", 14), bg="#272640", fg="#ffffb3")
        selected_image.pack(pady=10)

        # Label to display selected image
        image_label = Label(root)
        image_label.pack(pady=10)

        # Proceed button
        proceed_btn = tk.Button(
            root, 
            text="Proceed", 
            command=proceed, 
            bg="#ffffb3",   # Background color
            fg="#023e7d",   # Text color
            font=("Arial", 12, "bold"),  # Font style
            padx=10,  # Padding for width
            pady=5,   # Padding for height
            relief="raised",  # Button border style
            bd=3,  # Border thickness
        )
        proceed_btn.pack(pady=20)

        # Run Tkinter main loop
        root.mainloop()

        return (self.selected_image_path,self.selected_image_name)  # Return the selected path after closing the window