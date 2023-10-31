# Provismet, 2023

from vmc_impl import ToggleBlend, SliderBlend, DurationBlend, AbstractBlend, createBlendApplyMessage

from pythonosc import udp_client, osc_bundle_builder
import tkinter as tk
from threading import Thread, Event
import json, subprocess, os, platform, webbrowser
from PIL import ImageTk, Image

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
        self.hoverBg = kwargs.pop("hoverBg")
        self.fg = kwargs.pop("fg")
        super().__init__(blend, *args, **kwargs)

        self.on_image = tk.PhotoImage(file="assets/on_button.png")
        self.off_image = tk.PhotoImage(file="assets/off_button.png")

        self.bg = kwargs["bg"]
        self.label = tk.Label(self, text=self.blendManager.title, bg=kwargs["bg"], font=self.defaultFont, fg=self.fg)
        self.button = tk.Canvas(master=self, width=56, height=56, bg=kwargs["bg"], bd=0, highlightthickness=0)
        self.button.create_image(0, 0, anchor=tk.NW, image=self.off_image)
        self.button.bind("<Enter>", self.onEnter)
        self.button.bind("<Leave>", self.onExit)
        self.button.bind("<Button-1>", self.toggle)
        
        self.label.pack(side=tk.TOP)
        self.button.pack(side=tk.BOTTOM)
    
    def toggle (self, event):
        self.blendManager.toggle()
        self.button.delete("all")
        if self.blendManager.state:
            self.button.create_image(0, 0, anchor=tk.NW, image=self.on_image)
        else:
            self.button.create_image(0, 0, anchor=tk.NW, image=self.off_image)
    
    def onEnter (self, event):
        self.button.configure(bg=self.hoverBg)
    
    def onExit (self, event):
        self.button.configure(bg=self.bg)

class DurationFrame (AbstractVMCFrame):
    def __init__ (self, blend: DurationBlend, *args, **kwargs):
        self.hoverBg = kwargs.pop("hoverBg")
        self.fg = kwargs.pop("fg")
        self.lineColour = kwargs.pop("lineColour")
        super().__init__(blend, *args, **kwargs)

        self.bg = kwargs["bg"]
        self.label = tk.Label(self, text=self.blendManager.title, bg=kwargs["bg"], font=self.defaultFont, fg=self.fg)

        self.swirl = [tk.PhotoImage(file="assets/timer_%i.png" % i) for i in range(1,25)]
        self.swirlOff = tk.PhotoImage(file="assets/timer_off.png")
        self.swirlPos = 0
        self.active = False

        self.canvas = tk.Canvas(master=self, width=56, height=56, bg=self.bg, bd=0, highlightthickness=0)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.swirlOff)
        self.canvas.bind("<Enter>", self.onEnter)
        self.canvas.bind("<Leave>", self.onExit)
        self.canvas.bind("<Button-1>", self.start)

        self.label.pack(side=tk.TOP)
        self.canvas.pack(side=tk.BOTTOM)

        self.delay = 50
        self.after(self.delay, self.canvasAfter)
    
    def start (self, event):
        self.active = True
        self.blendManager.index = 0

    def stop (self):
        self.active = False
        self.swirlPos = 0
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.swirlOff)
    
    def onEnter (self, event):
        self.canvas.configure(bg=self.hoverBg)
    
    def onExit (self, event):
        self.canvas.configure(bg=self.bg)

    def canvasAfter (self):
        if self.active:
            self.canvas.delete("all")

            self.swirlPos += 1
            if self.swirlPos >= len(self.swirl):
                self.swirlPos = 0
            
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.swirl[self.swirlPos])
            self.canvas.create_line(0, 0, self.lineEnd(0, 0.25), 0, fill=self.lineColour, width=4)
            self.canvas.create_line(56, 0, 56, self.lineEnd(0.25, 0.5), fill=self.lineColour, width=4)
            self.canvas.create_line(56, 56, 56 - self.lineEnd(0.5, 0.75), 56, fill=self.lineColour, width=4)
            self.canvas.create_line(0, 56, 0, 56 - self.lineEnd(0.75, 1), fill=self.lineColour, width=4)

            if not self.blendManager.step():
                self.stop()
        self.after(self.delay, self.canvasAfter)
            
    def lineEnd (self, minValue:float, maxValue:float) -> int:
        progress = self.blendManager.index / len(self.blendManager.values)
        
        if progress <= minValue:
            return 0
        elif progress >= maxValue:
            return 56
        else:
            progress -= minValue
            maxValue -= minValue
            return int(56 * (progress / maxValue))

class SliderFrame (AbstractVMCFrame):
    def __init__ (self, blend: SliderBlend, orientation:str, *args, **kwargs):
        self.fg = kwargs.pop("fg")
        self.hoverBg = kwargs.pop("hoverBg")
        self.trough = kwargs.pop("trough")
        super().__init__(blend, *args, **kwargs)

        self.value = tk.DoubleVar()
        self.label = tk.Label(self, text=self.blendManager.title, bg=kwargs["bg"], font=self.defaultFont, fg=self.fg)

        self.label = tk.Label(self, text=self.blendManager.title, bg=kwargs["bg"], font=self.defaultFont, fg=self.fg)
        self.slider = tk.Scale(self, variable=self.value, from_=self.blendManager.minValue, to=self.blendManager.maxValue, resolution=self.blendManager.step, orient=orientation, bg=kwargs["bg"], fg=self.fg, bd=5, activebackground=self.hoverBg, sliderrelief=tk.FLAT, troughcolor=self.trough)
        self.slider.set(self.blendManager.minValue)
        
        self.label.pack(side=tk.TOP)
        self.slider.pack(side=tk.BOTTOM)
    
    def getMessage(self):
        self.blendManager.set(self.value.get())
        return super().getMessage()

class HoverButton (tk.Label):
    def __init__ (self, *args, **kwargs):
        self.hoverBg = kwargs.pop("hoverBg")
        self.standardBg = kwargs["bg"]
        self.command = kwargs.pop("command")
        super().__init__(*args, **kwargs)
        self.bind("<Enter>", self.onEnter)
        self.bind("<Leave>", self.onExit)
        self.bind("<Button-1>", self.command)
    
    def onEnter (self, event):
        self.configure(bg=self.hoverBg, activebackground=self.hoverBg)
    
    def onExit (self, event):
        self.configure(bg=self.standardBg, activebackground=self.standardBg)

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

def openOptionsFile (event = None):
    filepath = "lilypanel.json"
    if platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    elif platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

def openGithub (event = None):
    webbrowser.open_new_tab("https://github.com/Provismet/LilyPanel")

frameList: list[AbstractVMCFrame] = []
stopThread = Event()

if __name__ == "__main__":
    file = open("./lilypanel.json", "r")
    panelData = json.load(file)
    file.close()

    controlFrameColour = panelData["layout"]["colour"]["controlFrame"]
    controlFrameColourHover = panelData["layout"]["colour"]["controlButtonHover"]
    optionsFrameColour = panelData["layout"]["colour"]["optionsFrame"]
    optionsButtonColourHover = panelData["layout"]["colour"]["optionsButtonHover"]
    textColour = panelData["layout"]["colour"]["text"]

    durationLineColour = panelData["layout"]["colour"]["durationLine"]
    sliderTroughColour = panelData["layout"]["colour"]["sliderTrough"]

    client = udp_client.SimpleUDPClient(panelData["ip"], panelData["port"])

    root = tk.Tk()
    root.title("LilyPanel")
    root.protocol("WM_DELETE_WINDOW", onClose)
    root.resizable(False, False)
    root.wm_iconphoto(False, ImageTk.PhotoImage(Image.open("assets/icon.png")))

    optionsFrame = tk.Frame(root, bg=optionsFrameColour)
    optionsFrame.pack(side=tk.TOP, fill=tk.X)
    
    shouldStayOnTop = tk.BooleanVar()
    tk.Checkbutton(optionsFrame, text="Stay On Top", command=setStayOnTop, onvalue=True, offvalue=False, variable=shouldStayOnTop, bg=optionsFrameColour, activeforeground=textColour, activebackground=optionsFrameColour, fg=textColour, selectcolor=optionsFrameColour).pack(side=tk.LEFT)
    HoverButton(optionsFrame, text=" Settings ", command=openOptionsFile, bg=optionsFrameColour, activebackground=optionsFrameColour, hoverBg=optionsButtonColourHover, fg=textColour, activeforeground=textColour, relief=tk.FLAT).pack(side=tk.RIGHT, fill=tk.Y)
    HoverButton(optionsFrame, text=" GitHub ", command=openGithub, bg=optionsFrameColour, activebackground=optionsFrameColour, hoverBg=optionsButtonColourHover, fg=textColour, activeforeground=textColour, relief=tk.FLAT).pack(side=tk.RIGHT, fill=tk.Y)
    
    controlFrame = tk.Frame(root, bg=controlFrameColour)
    controlFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)
    controlFrame.columnconfigure(list(range(3)), weight=1)

    toggleGrid = tk.Frame(controlFrame, bg=controlFrameColour)
    toggleGrid.grid(row=0, column=0, padx=panelData["layout"]["xPadding"], pady=panelData["layout"]["yPadding"], sticky=tk.W)

    sliderGrid = tk.Frame(controlFrame, bg=controlFrameColour)
    sliderGrid.grid(row=0, column=1, padx=panelData["layout"]["xPadding"], pady=panelData["layout"]["yPadding"], sticky=tk.E)

    currentButtonColumn = 0
    currentButtonRow = 0
    currentSliderColumn = 0
    currentSliderRow = 0

    buttonLayout = panelData["layout"]["buttons"]
    sliderLayout = panelData["layout"]["sliders"]

    for newBlend in panelData["blends"]:
        if newBlend["type"] == "toggle":
            newFrame = ToggleFrame(blend=ToggleBlend(newBlend["name"], float(newBlend["offValue"]), float(newBlend["onValue"])), master=toggleGrid, bg=controlFrameColour, hoverBg=controlFrameColourHover, fg=textColour)
            frameList.append(newFrame)
            newFrame.grid(row=currentButtonRow, column=currentButtonColumn, padx=buttonLayout["xPadding"], pady=buttonLayout["yPadding"])
            
            currentButtonColumn += 1
            if currentButtonColumn == buttonLayout["columns"]:
                currentButtonColumn = 0
                currentButtonRow += 1
        elif newBlend["type"] == "duration":
            newFrame = DurationFrame(blend=DurationBlend(newBlend["name"], dict(newBlend["checkpoints"]), float(newBlend["defaultValue"])), master=toggleGrid, bg=controlFrameColour, hoverBg=controlFrameColourHover, fg=textColour, lineColour=durationLineColour)
            frameList.append(newFrame)
            newFrame.grid(row=currentButtonRow, column=currentButtonColumn, padx=buttonLayout["xPadding"], pady=buttonLayout["yPadding"])
            
            currentButtonColumn += 1
            if currentButtonColumn == buttonLayout["columns"]:
                currentButtonColumn = 0
                currentButtonRow += 1
        elif newBlend["type"] == "slider":
            newFrame = SliderFrame(blend=SliderBlend(newBlend["name"], float(newBlend["minValue"]), float(newBlend["maxValue"]), float(newBlend["step"])), orientation=sliderLayout["orientation"], master=sliderGrid, bg=controlFrameColour, fg=textColour, hoverBg=controlFrameColourHover, trough=sliderTroughColour)
            frameList.append(newFrame)
            newFrame.grid(row=currentSliderRow, column=currentSliderColumn, padx=sliderLayout["xPadding"], pady=sliderLayout["yPadding"])

            currentSliderColumn += 1
            if currentSliderColumn == sliderLayout["columns"]:
                currentSliderColumn = 0
                currentSliderRow += 1

    thread = Thread(target=main, daemon=True)
    thread.start()
    root.mainloop()
