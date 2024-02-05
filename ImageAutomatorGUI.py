#pip install opencv-python
import cv2
#pip install tk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
#pip install pillow
from PIL import Image, ImageTk
import os
#pip install adafruit-circuitpython-motorkit
#from adafruit_motorkit import MotorKit
import time

class ImageAutomatorGUI:
    def __init__(self, root, window_title, video_source1=0, video_source2 = 2, video_source3 = 4, video_source4 = 6):
        self.root = root
        self.root.title(window_title)

        #Set maximized
        self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        # root.bind("<Button-1>", lambda event: self.on_root_click(event))

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
        #Setup the number tracker for close up images, this gets put on the saved image filename for close ups
        self.numCloseUp = 1
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
        ttk.Label(self.input_frame, text="Description:").grid(row=5, column=0, sticky=tk.E, pady=5)
        ttk.Label(self.input_frame, text="Long Description:").grid(row=6, column=0, sticky=tk.E, pady=5)


        # Create entry fields with default values
        self.item_name_var = tk.StringVar()
        self.length_var = tk.StringVar()
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.description_long_var = tk.StringVar()
        self.rotation_degrees_var = tk.StringVar()

        # Set default values
        self.item_name_var.set("123")
        self.length_var.set("10")
        self.width_var.set("12")
        self.height_var.set("14")
        self.weight_var.set("16")
        self.description_var.set("Short description")
        #THIS GETS PUT INTO THE TEXT WIDGET DOWN BELOW
        self.description_long_var.set("Sample Long description")
        self.rotation_degrees_var.set("0")

        #Add change listeners
        self.item_name_var.trace_add("write", self.item_changed)
        self.length_var.trace_add("write", self.item_changed)
        self.width_var.trace_add("write", self.item_changed)
        self.height_var.trace_add("write", self.item_changed)
        self.weight_var.trace_add("write", self.item_changed)
        self.description_var.trace_add("write", self.item_changed)
        #This is multiline text element and it behaves differently, the text widget gets a KeyRelease listener
        #to change the backend variable
        #self.description_long_var.trace_add("write", self.item_changed)

        rowIdx = 0
        numberWidth = 10
        # Input fields
        #ItemNumber
        self.item_num_entry = self.setupEntry(numberWidth,self.item_name_var,rowIdx)
        rowIdx += 1
        #Length
        self.length_entry = self.setupEntry(numberWidth,self.length_var,rowIdx)
        rowIdx +=1
        #Width
        self.width_entry = self.setupEntry(numberWidth,self.width_var,rowIdx)
        rowIdx +=1
        #Height
        self.height_entry = self.setupEntry(numberWidth,self.height_var,rowIdx)
        rowIdx +=1
        #Weight
        self.weight_entry = self.setupEntry(numberWidth,self.weight_var,rowIdx)
        rowIdx +=1
        #Short Description
        self.description_entry = self.setupEntry(40,self.description_var,rowIdx)
        rowIdx +=2
        #Long Description
        #self.description_long_entry = ttk.Entry(self.input_frame, width=20,textvariable= self.description_long_var)
        self.description_long_entry = tk.Text(self.input_frame, width=50, height=3)
        self.description_long_entry.grid(row=rowIdx, column=1, pady=5)
        self.description_long_entry.bind("<FocusIn>", lambda event: self.on_entry_focus_in(event))
        self.description_long_entry.bind("<FocusOut>", lambda event: self.on_entry_focus_out(event))
        self.description_long_entry.bind("<Return>", lambda event: self.on_return_key(event))
        rowIdx +=1
        #bind the text widget on change
        self.description_long_entry.bind("<KeyRelease>", self.on_long_description_changed)

        ##------PUT TESTING DATA IN---
        #TAKE THIS OUT
        self.description_long_entry.insert("1.0", self.description_long_var.get())  # Insert new content

        # Save button
        self.save_button = ttk.Button(self.input_frame, text="Save", command = self.saveDetails)
        self.save_button.grid(row=rowIdx, column=1, pady=5)
        rowIdx +=1
        # Take picture button
        self.take_picture_button = ttk.Button(self.input_frame, text="Take Picture",command = self.takePicture, state=tk.DISABLED)
        self.take_picture_button.grid(row=rowIdx, column=1, pady=5)
        rowIdx +=1
         # Label for displaying rotation degrees
        self.degrees_label = ttk.Label(self.input_frame, text="--Rotation Degrees--")
        self.degrees_label.grid(row=rowIdx, column=1, pady=5)
        rowIdx +=1
        #Entry for the degree rotation so you can set manually
        self.rotation_degrees_entry = ttk.Entry(self.input_frame, width=numberWidth,textvariable= self.rotation_degrees_var, justify='center')
        self.rotation_degrees_entry.grid(row=rowIdx, column=1, pady=5)
        rowIdx +=1
        # Rotate button
        self.rotate_button = ttk.Button(self.input_frame, text="Rotate",state=tk.DISABLED, command= self.rotate90)
        self.rotate_button.grid(row=rowIdx, column=1, pady=5)
        rowIdx +=1
        # Zero button
        self.zero_button = ttk.Button(self.input_frame, text="Zero Rig",state=tk.DISABLED, command = self.zeroRig)
        self.zero_button.grid(row=rowIdx, column=1, pady=5)
        rowIdx +=1
        #Create empty space for divider
        ttk.Label(self.input_frame,text="").grid(row=rowIdx,column=1)
        rowIdx +=1
        # New Item button
        self.newitem_button = ttk.Button(self.input_frame, text="New Item",state=tk.DISABLED, command = self.newItem)
        self.newitem_button.grid(row=rowIdx, column=1, pady=5)
        rowIdx +=1

       
        # Label for displaying rotation degrees
        self.status_label = ttk.Label(self.input_frame, text="Status: Idle")
        self.status_label.grid(row=rowIdx, column=1, pady=5)
        rowIdx +=1

         #Setup motor
        self.kit = MotorKit()
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

        #The 1234 keys should NOT fire when we are typing in a text box
        #make variable to track that 
        self.entry_has_focus = tk.BooleanVar(value=False)

        #Add key bindings
        self.root.bind('<Escape>', lambda event: self.on_esc_pressed(event))
        self.root.bind('1', lambda event: self.on_1_pressed(event))
        self.root.bind('<KP_1>', lambda event: self.on_1_pressed(event))
        self.root.bind('2', lambda event: self.on_2_pressed(event))
        self.root.bind('<KP_2>', lambda event: self.on_2_pressed(event))
        self.root.bind('3', lambda event: self.on_3_pressed(event))
        self.root.bind('<KP_3>', lambda event: self.on_3_pressed(event))
        self.root.bind('4', lambda event: self.on_4_pressed(event))
        self.root.bind('<KP_4>', lambda event: self.on_4_pressed(event))
        

        # After initializing, call the function to capture and display frames
        self.update()

    def setupEntry(self, widthIn, item_var,rowIdx):
        entry = ttk.Entry(self.input_frame, width=widthIn,textvariable= item_var)
        entry.grid(row=rowIdx, column=1, pady=5)
        entry.bind("<FocusIn>", lambda event: self.on_entry_focus_in(event))
        entry.bind("<FocusOut>", lambda event: self.on_entry_focus_out(event))
        entry.bind("<Return>", lambda event: self.on_return_key(event))
        return entry

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
        description = self.description_var.get()
        description_long = self.description_long_var.get()

        #confirm that item_num is entered
        if item_num == '':
            messagebox.showerror("Error","You must fill in the item number!")
            return

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
                file.write(f"ItemNum:{item_num}\n")
                file.write(f"Length:{length}\n")
                file.write(f"Width:{width}\n")
                file.write(f"Height:{height}\n")
                file.write(f"Weight:{weight}\n")
                file.write(f"Descr:{description}\n")
                file.write(f"Long Descr:{description_long}")
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
        degreesStr = self.rotation_degrees_var.get()
        #Save all images
        cv2.imwrite(f"{self.path}/frame1_{degreesStr}.jpg",self.frame1)
        cv2.imwrite(f"{self.path}/frame2_{degreesStr}.jpg",self.frame2)
        cv2.imwrite(f"{self.path}/frame3_{degreesStr}.jpg",self.frame3)
        cv2.imwrite(f"{self.path}/frame4_{degreesStr}.jpg",self.frame4)

    def addTextToImage(self,frame,num, x,y):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        text_color=(255, 255, 255)
        box_color=(0, 0, 0)
        # Get the size of the text
        (text_width, text_height), baseline = cv2.getTextSize(num, font, font_scale, thickness)
        box_width = text_width
        padding = 5
        box_height = text_height + padding
        cv2.rectangle(frame, (x, y - padding), (x +  box_width, y + box_height), box_color, thickness=cv2.FILLED)
        # Draw the text
        cv2.putText(frame, num, (x, y + text_height), font, font_scale, text_color, thickness, cv2.LINE_AA)

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
            num_padding = 10
            #put the numbers on the images
            self.addTextToImage(topRow, "1",num_padding,num_padding)
            self.addTextToImage(topRow, "2",self.frame1.shape[1]+num_padding,num_padding)
            #make bottom row
            bottomRow = cv2.hconcat([self.frame3, self.frame4])
            #put text on images
            self.addTextToImage(bottomRow, "3",num_padding,num_padding)
            self.addTextToImage(bottomRow, "4",self.frame1.shape[1]+num_padding,num_padding)
            #combine into 4 corner 
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
        self.description_var.set("")
        self.description_long_var.set("")
        #clear the multiline text
        self.description_long_entry.delete("1.0", tk.END)
        #reset close up number
        self.numCloseUp = 1
        self.status_label.config(text="Status: Idle")
        #update the buttons
        self.take_picture_button.config(state=tk.DISABLED)
        self.rotate_button.config(state=tk.DISABLED)
        self.newitem_button.config(state=tk.DISABLED)
        self.zero_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)

    def rotate90(self):
        self.status_label.config(text=f"Rotating 90 degrees")
        degrees = 90
        self.rotation_degrees += degrees
        direction = self.CLOCKWISE
        #908 is 90 degrees
        '''
        steps = 908 
        for i in range(steps):
            if direction == self.CLOCKWISE:
                self.kit.stepper1.onestep(direction=stepper.BACKWARD, style = stepper.INTERLEAVE)
                self.pos += 1
            else:
                self.kit.stepper1.onestep(direction=stepper.BACKWARD)#, style=self.stepper.stepper1.MICROSTEP)
                self.pos -= 1
            time.sleep(.008)
        '''
        self.status_label.config(text=f"Rig rotated")
        self.rotation_degrees_var.set(str(self.rotation_degrees))
        print(f"Current stepper position: {self.pos}")

    def zeroRig(self):
        self.status_label.config(text=f"Moving Rig to Zero")
        '''
        #assume we're moving counter clockwise
        while(self.pos > 0):           
            self.kit.stepper1.onestep(direction=stepper.FORWARD, style = stepper.INTERLEAVE)
            self.pos -= 1
            time.sleep(.008)
        '''
        self.status_label.config(text=f"Rig is reset to zero")
        self.rotation_degrees = 0
        self.rotation_degrees_var.set(str(self.rotation_degrees))
        print(f"Current stepper position: {self.pos}")

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

    def on_long_description_changed(self,event):
        content =  self.description_long_entry.get("1.0", tk.END)
        #set the variable for long description
        self.description_long_var.set(content)
        self.save_button.config(state=tk.NORMAL)
    
    def on_esc_pressed(self, event):
        self.root.destroy()

    #Check this but the close up shouldn't have frame1 in it
    def on_1_pressed(self, event):
        if not self.entry_has_focus.get():
            cv2.imwrite(f"{self.path}/closeUp_{self.numCloseUp}.jpg",self.frame1)
            self.numCloseUp += 1

    def on_2_pressed(self, event):
        if not self.entry_has_focus.get():
            cv2.imwrite(f"{self.path}/closeUp_{self.numCloseUp}.jpg",self.frame2)
            self.numCloseUp += 1

    def on_3_pressed(self, event):
        if not self.entry_has_focus.get():
            cv2.imwrite(f"{self.path}/closeUp_{self.numCloseUp}.jpg",self.frame3)
            self.numCloseUp += 1

    def on_4_pressed(self, event):
        if not self.entry_has_focus.get():
            cv2.imwrite(f"{self.path}/closeUp_{self.numCloseUp}.jpg",self.frame4)
            self.numCloseUp += 1
    
    def on_entry_focus_in(self,event):
        self.entry_has_focus.set(True)

    def on_entry_focus_out(self,event):
        self.entry_has_focus.set(False)
    
    def on_return_key(self,event):
        self.root.focus_set()
