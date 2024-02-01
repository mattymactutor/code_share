from ImageAutomatorGUI import ImageAutomatorGUI
import tkinter as tk
# Create the Tkinter root window
root = tk.Tk()

# Specify the window title and video source (0 for default camera)
app = ImageAutomatorGUI(root, "Image Automator", video_source1=0)

# Run the Tkinter main loop
root.mainloop()