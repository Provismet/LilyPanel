from vmc_impl import ToggleBlend, SliderBlend, AbstractBlend, createBlendApplyMessage

from pythonosc import udp_client, osc_bundle_builder
import tkinter as tk
from tkinter import ttk
from threading import Thread, Event
import json
import subprocess, os, platform

class AbstractVMCFrame (tk.Frame):
    def __init__(self, blend: AbstractBlend, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blendManager = blend
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.defaultFont = ("Segoe UI", 12)
    
    def getMessage (self):
        return self.blendManager.getMessage()

class ToggleFrame (AbstractVMCFrame):
    def __init__ (self, blend: ToggleBlend, *args, **kwargs):
        super().__init__(blend, *args, **kwargs)

        self.on_image = tk.PhotoImage(file="assets/on_button.png")
        self.off_image = tk.PhotoImage(file="assets/off_button.png")

        self.label = tk.Label(self, text=self.blendManager.title, bg=kwargs["bg"], font=self.defaultFont, fg="#F6F6F6")
        self.button = tk.Button(master=self, image=self.off_image, command=self.toggle, bg=kwargs["bg"], relief=tk.FLAT, activebackground=kwargs["bg"])
        
        self.label.pack(side=tk.TOP)
        self.button.pack(side=tk.BOTTOM)
    
    def toggle (self):
        self.blendManager.toggle()
        if self.blendManager.state:
            self.button.config(image=self.on_image)
        else:
            self.button.config(image=self.off_image)


class SliderFrame (AbstractVMCFrame):
    def __init__ (self, blend: SliderBlend, orientation:str, *args, **kwargs):
        super().__init__(blend, *args, **kwargs)

        self.value = tk.DoubleVar()

        self.label = tk.Label(self, text=self.blendManager.title, bg=kwargs["bg"], font=self.defaultFont, fg="#F6F6F6")
        self.slider = tk.Scale(self, variable=self.value, from_=self.blendManager.minValue, to=self.blendManager.maxValue, resolution=self.blendManager.step, orient=orientation, bg=kwargs["bg"], fg="#F6F6F6")
        self.slider.set(self.blendManager.minValue)
        
        self.label.pack(side=tk.TOP)
        self.slider.pack(side=tk.BOTTOM)
    
    def getMessage(self):
        self.blendManager.set(self.value.get())
        return super().getMessage()

def main ():
    while True:
        if stopThread.is_set(): # This is a daemon thread and will be killed anyway, but try to exit cleanly if possible.
            break

        try:
            bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
            for frame in frameList:
                bundle.add_content(frame.getMessage())
            bundle.add_content(createBlendApplyMessage())
            bundle = bundle.build()
            client.send(bundle)
        except:
            pass

def onClose ():
    stopThread.set()
    root.destroy()

def setStayOnTop ():
    root.attributes("-topmost", shouldStayOnTop.get())

def openOptionsFile ():
    filepath = "lilypanel.json"
    if platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    elif platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

frameList: list[AbstractVMCFrame] = []
stopThread = Event()

if __name__ == "__main__":
    controlFrameColour = "#505050"
    optionsFrameColour = "#353535"

    file = open("lilypanel.json", "r")
    panelData = json.load(file)
    file.close()

    client = udp_client.SimpleUDPClient(panelData["ip"], panelData["port"])

    root = tk.Tk()
    root.title("LilyPanel")
    root.protocol("WM_DELETE_WINDOW", onClose)
    root.resizable(False, False)
    root.iconbitmap("assets/icon.ico")

    optionsFrame = tk.Frame(root, bg=optionsFrameColour)
    optionsFrame.pack(side=tk.TOP, fill=tk.X)
    
    shouldStayOnTop = tk.BooleanVar()
    tk.Checkbutton(optionsFrame, text="Stay On Top", command=setStayOnTop, onvalue=True, offvalue=False, variable=shouldStayOnTop, bg=optionsFrameColour, activeforeground="#F6F6F6", activebackground=optionsFrameColour, fg="#F6F6F6", selectcolor=optionsFrameColour).pack(side=tk.LEFT)
    tk.Button(optionsFrame, text="Open Settings", command=openOptionsFile).pack(side=tk.RIGHT)
    
    controlFrame = tk.Frame(root, bg=controlFrameColour)
    controlFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)
    controlFrame.columnconfigure(list(range(3)), weight=1)

    toggleGrid = tk.Frame(controlFrame, bg=controlFrameColour)
    toggleGrid.grid(row=0, column=0, padx=panelData["layout"]["xPadding"], pady=panelData["layout"]["yPadding"], sticky=tk.W)

    sep = ttk.Separator(controlFrame, orient=tk.VERTICAL)
    sep.grid(row=0, column=1, sticky="ns")

    sliderGrid = tk.Frame(controlFrame, bg=controlFrameColour)
    sliderGrid.grid(row=0, column=2, padx=panelData["layout"]["xPadding"], pady=panelData["layout"]["yPadding"], sticky=tk.E)

    currentButtonColumn = 0
    currentButtonRow = 0
    currentSliderColumn = 0
    currentSliderRow = 0

    buttonLayout = panelData["layout"]["buttons"]
    sliderLayout = panelData["layout"]["sliders"]

    for newBlend in panelData["blends"]:
        if newBlend["type"] == "toggle":
            newFrame = ToggleFrame(blend=ToggleBlend(newBlend["name"], float(newBlend["offValue"]), float(newBlend["onValue"])), master=toggleGrid, bg=controlFrameColour)
            frameList.append(newFrame)
            newFrame.grid(row=currentButtonRow, column=currentButtonColumn, padx=buttonLayout["xPadding"], pady=buttonLayout["yPadding"])
            
            currentButtonColumn += 1
            if currentButtonColumn == buttonLayout["columns"]:
                currentButtonColumn = 0
                currentButtonRow += 1
        elif newBlend["type"] == "slider":
            newFrame = SliderFrame(blend=SliderBlend(newBlend["name"], float(newBlend["minValue"]), float(newBlend["maxValue"]), float(newBlend["step"])), orientation=sliderLayout["orientation"], master=sliderGrid, bg=controlFrameColour)
            frameList.append(newFrame)
            newFrame.grid(row=currentSliderRow, column=currentSliderColumn, padx=sliderLayout["xPadding"], pady=sliderLayout["yPadding"])

            currentSliderColumn += 1
            if currentSliderColumn == sliderLayout["columns"]:
                currentSliderColumn = 0
                currentSliderRow += 1

    thread = Thread(target=main, daemon=True)
    thread.start()
    root.mainloop()
