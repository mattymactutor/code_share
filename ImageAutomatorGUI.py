import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
#from adafruit_motorkit import MotorKit

class ImageAutomatorGUI:
    def __init__(self, root, window_title, video_source1=0, video_source2 = 2, video_source3 = 4, video_source4 = 6):
        self.root = root
        self.root.title(window_title)

        #Set maximized
        self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))

        # Open the video source
        self.cap1 = cv2.VideoCapture(video_source1)
        if not self.cap1.isOpened():
            print("Error: Could not open camera1.")
            exit()
        #TODO Open other cameras
        '''
        self.cap2 = cv2.VideoCapture(video_source2)
        if not self.cap2.isOpened():
            print("Error: Could not open camera2.")
            exit()
        self.cap3 = cv2.VideoCapture(video_source3)
        if not self.cap3.isOpened():
            print("Error: Could not open camera3.")
            exit()
        self.cap4 = cv2.VideoCapture(video_source4)
        if not self.cap4.isOpened():
            print("Error: Could not open camera4.")
            exit()
        '''


        #Setup frames
        self.frame1 = None
        self.frame2 = None
        self.frame3 = None
        self.frame4 = None
        # Create a window to display the captured frames
        self.canvas = tk.Canvas(root)
        #self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.root.grid_columnconfigure(0, weight=5)  # 80% width for the image
        self.root.grid_rowconfigure(0, weight=1)  # Full height for the canvas

        # Create a frame for the input fields on the right side
        self.input_frame = ttk.Frame(root, padding=(10, 10))
        #self.input_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.input_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.root.grid_columnconfigure(1, weight=1)  # 25% width for the input fields

        # Labels for input fields
        ttk.Label(self.input_frame, text="Item Number:").grid(row=0, column=0, sticky=tk.E, pady=5)
        ttk.Label(self.input_frame, text="Length:").grid(row=1, column=0, sticky=tk.E, pady=5)
        ttk.Label(self.input_frame, text="Width:").grid(row=2, column=0, sticky=tk.E, pady=5)
        ttk.Label(self.input_frame, text="Height:").grid(row=3, column=0, sticky=tk.E, pady=5)
        ttk.Label(self.input_frame, text="Weight:").grid(row=4, column=0, sticky=tk.E, pady=5)

        # Create entry fields with default values
        self.item_name_var = tk.StringVar()
        self.length_var = tk.StringVar()
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()

        # Set default values
        self.item_name_var.set("123")
        self.length_var.set("10")
        self.width_var.set("12")
        self.height_var.set("14")
        self.weight_var.set("16")

        #Add change listeners
        self.item_name_var.trace_add("write", self.item_changed)
        self.length_var.trace_add("write", self.item_changed)
        self.width_var.trace_add("write", self.item_changed)
        self.height_var.trace_add("write", self.item_changed)
        self.weight_var.trace_add("write", self.item_changed)

        # Input fields
        self.item_num_entry = ttk.Entry(self.input_frame, width=20,textvariable= self.item_name_var)
        self.item_num_entry.grid(row=0, column=1, pady=5)
        self.length_entry = ttk.Entry(self.input_frame, width=20,  textvariable= self.length_var)
        self.length_entry.grid(row=1, column=1, pady=5)
        self.width_entry = ttk.Entry(self.input_frame, width=20, textvariable= self.width_var)
        self.width_entry.grid(row=2, column=1, pady=5)
        self.height_entry = ttk.Entry(self.input_frame, width=20, textvariable= self.height_var)
        self.height_entry.grid(row=3, column=1, pady=5)
        self.weight_entry = ttk.Entry(self.input_frame, width=20,textvariable= self.weight_var)
        self.weight_entry.grid(row=4, column=1, pady=5)

        # Save button
        self.save_button = ttk.Button(self.input_frame, text="Save", command = self.saveDetails)
        self.save_button.grid(row=5, column=1, pady=5)

        # Take picture button
        self.take_picture_button = ttk.Button(self.input_frame, text="Take Picture",command = self.takePicture, state=tk.DISABLED)
        self.take_picture_button.grid(row=6, column=1, pady=5)

        # Rotate button
        self.rotate_button = ttk.Button(self.input_frame, text="Rotate",state=tk.DISABLED, command= self.rotate90)
        self.rotate_button.grid(row=7, column=1, pady=5)

        # Zero button
        self.zero_button = ttk.Button(self.input_frame, text="Zero Rig",state=tk.DISABLED, command = self.zeroRig)
        self.zero_button.grid(row=8, column=1, pady=5)

        #Create empty space for divider
        ttk.Label(self.input_frame,text="").grid(row=9,column=1)

        # New Item button
        self.newitem_button = ttk.Button(self.input_frame, text="New Item",state=tk.DISABLED, command = self.newItem)
        self.newitem_button.grid(row=10, column=1, pady=5)


        # Label for displaying rotation degrees
        self.degrees_label = ttk.Label(self.input_frame, text="Rotation: 0 degrees")
        self.degrees_label.grid(row=11, column=1, pady=5)

        # Label for displaying rotation degrees
        self.status_label = ttk.Label(self.input_frame, text="Status: Idle")
        self.status_label.grid(row=12, column=1, pady=5)

        # Set up initial value for rotation degrees
        self.rotation_degrees = 0
        self.pos = 0

        #set path
        self.path = "./"
        self.path_details = ""

        #setup motor
        #self.stepper = MotorKit()
        self.CLOCKWISE = 1
        self.CO_CLOCKWISE = -1

        # After initializing, call the function to capture and display frames
        self.update()

    def delete_folder_contents(self, folder_path):
        # Check if the folder path exists
        if os.path.exists(folder_path):
            # List items in the folder
            folder_items = os.listdir(folder_path)

            # Delete each item in the folder
            for item in folder_items:
                item_path = os.path.join(folder_path, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)  # Delete file
                    elif os.path.isdir(item_path):
                        os.rmdir(item_path)  # Delete directory (empty)
                except Exception as e:
                    print(f"Error deleting {item_path}: {e}")

            print(f"Deleted all items in {folder_path}")
            #delete the actual folder
            os.rmdir(folder_path)
            print(f"Delete folder {folder_path}")
        else:
            print(f"Path {folder_path} does not exist")

    def saveDetails(self):
         # Retrieve values from input fields
        item_num = self.item_name_var.get()
        length = self.length_var.get()
        width = self.width_var.get()
        height = self.height_var.get()
        weight = self.weight_var.get()

        #update the path to have the item name as the folder
        self.path = f"./{item_num}"
        #check if the directory exists and delete if so
        self.delete_folder_contents(self.path)
        #make the directory
        os.mkdir(self.path)
        #set the detail filename
        self.path_details = f"{self.path}/{item_num}_details.txt"

        #write to file
        try:
            with open(self.path_details, 'w') as file:
                file.write(f"ItemNum: {item_num}\n")
                file.write(f"Length: {length}\n")
                file.write(f"Width: {width}\n")
                file.write(f"Height: {height}\n")
                file.write(f"Weight: {weight}\n")
            print(f"Details for {item_num} written to {self.path_details}")
            self.take_picture_button.config(state=tk.NORMAL)
            self.rotate_button.config(state=tk.NORMAL)
            self.newitem_button.config(state=tk.NORMAL)
            self.zero_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
            self.status_label.config(text=f"Saved data to file for {item_num}")
        except Exception as e:
            print(f"Error writing to {self.path_details}: {e}")

    def item_changed(self,name,index,mode):
        print(f"Changed input field: {name} {index} {mode}")
        self.save_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Status: idle")

    def takePicture(self):
        #Save all images
        cv2.imwrite(f"{self.path}/frame1_{self.rotation_degrees}.jpg",self.frame1)
        cv2.imwrite(f"{self.path}/frame2_{self.rotation_degrees}.jpg",self.frame2)
        cv2.imwrite(f"{self.path}/frame3_{self.rotation_degrees}.jpg",self.frame3)
        cv2.imwrite(f"{self.path}/frame4_{self.rotation_degrees}.jpg",self.frame4)

    def update(self):
        # Get a frame from the video source
        ret, self.frame1 = self.cap1.read()
        #ret, self.frame2 = self.cap2.read()
        #ret, self.frame3 = self.cap3.read()
        #ret, self.frame4 = self.cap4.read()
        #fake other cameras
        self.frame2 = self.frame1
        self.frame3 = self.frame1
        self.frame4 = self.frame1

        if ret:
            # Rotate the frame based on the current rotation_degrees
            #rotated_frame = self.rotate_frame(frame, self.rotation_degrees)
            topRow = cv2.hconcat([self.frame1, self.frame2])
            bottomRow = cv2.hconcat([self.frame3, self.frame4])
            combined = cv2.vconcat([topRow,bottomRow])
            # Resize the frame to fit the canvas
            newWidth = int(self.root.winfo_reqwidth() * 0.8)
            newHeight = int(self.root.winfo_reqheight())
            resized_frame = self.resize_frame(combined, 1000 )
            # Display the frame on the Tkinter window
            self.photo = self.convert_frame_to_photo(resized_frame)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Call the update method after a delay (in milliseconds)
        self.root.after(10, self.update)

    def convert_frame_to_photo(self, frame):
        # Convert a frame to PhotoImage format for Tkinter
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        photo = ImageTk.PhotoImage(image=pil_image)
        return photo

    def resize_frame(self, frame, width=None, height=None):
        # Resize a frame using OpenCV
        if width is None and height is None:
            return frame
        elif width is None:
            aspect_ratio = height / float(frame.shape[0])
            new_width = int(frame.shape[1] * aspect_ratio)
            return cv2.resize(frame, (new_width, height))
        elif height is None:
            aspect_ratio = width / float(frame.shape[1])
            new_height = int(frame.shape[0] * aspect_ratio)
            return cv2.resize(frame, (width, new_height))
        else:
            return cv2.resize(frame, (width, height))
        
    def newItem(self):
        self.item_name_var.set("")
        self.length_var.set("")
        self.width_var.set("")
        self.height_var.set("")
        self.weight_var.set("")
        self.status_label.config(text="Status: Idle")

    def rotate90(self):
        degrees = 90
        direction = self.CLOCKWISE
        #TODO convert degrees to steps 
        steps = degrees 
        for i in range(steps):
            if direction == self.CLOCKWISE:
                self.stepper.stepper1.onestep(direction=self.stepper.stepper1.FORWARD, style=self.stepper.stepper1.MICROSTEP)
                self.pos += 1
            else:
                self.stepper.stepper1.onestep(direction=self.stepper.stepper1.BACKWARD, style=self.stepper.stepper1.MICROSTEP)
                self.pos -= 1

    def zeroRig(self):
        self.status_label.config(text=f"Moving Rig to Zero")
        #assume we're moving counter clockwise
        while(self.pos > 0):
            self.stepper.stepper1.onestep(direction=self.stepper.stepper1.BACKWARD, style=self.stepper.stepper1.MICROSTEP)
            self.pos -= 1
        self.status_label.config(text=f"Rig is reset to zero")

    def __del__(self):
        # Release the camera when the object is deleted
        if self.cap1.isOpened():
            self.cap1.release()
        #Release other cameras
        '''
        if self.cap2.isOpened():
            self.cap2.release()
        if self.cap3.isOpened():
            self.cap3.release()
        if self.cap4.isOpened():
            self.cap5.release()
        '''


