"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="Changelog", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Will show the latest changelog.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static" # = Panel
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import webview as wv

CHANGE_LOG_SHOWN = False

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        
        def exampleFunction(self):
            global CHANGE_LOG_SHOWN
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvas to the widgets
            self.root.pack_propagate(0)
                
            
            if CHANGE_LOG_SHOWN == False:
                helpers.OpenWebView("Changelog", "https://wiki.tumppi066.fi/blog/", width=800, height=600)
                CHANGE_LOG_SHOWN = True
            
            helpers.MakeLabel(self.root, "Close this window by middle clicking on the tab.", 0, 0)
            
            # variables.RELOAD = True # This will reload the UI when the panel is closed
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)