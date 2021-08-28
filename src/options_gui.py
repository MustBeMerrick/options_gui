# imports
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
import tkinter as tk

# ----------------------------------------- INPUTS -----------------------------------------
column_names = ["Stock Symbol"]
maxColumns = 10
maxRows = 10
# ------------------------------------------------------------
# derive parameters
newEntryButtonOffset = 3
seriesOffset = newEntryButtonOffset + 1

# create scrollable window
window = tk.Tk()

# get width x height of display
width= window.winfo_screenwidth() 
height= window.winfo_screenheight()
window.geometry("%dx%d" % (width, height))
window.title("Options Positions")

# configure grid cells
[window.columnconfigure(i, weight=1) for i in range(maxColumns)]
[window.rowconfigure(i, weight=1) for i in range(maxRows)]

# Create column headers
col = 0
for label in column_names:
    columnLabel = tk.Label( text=label,\
                            font='"Helvetica Neue" 14 bold')
    columnLabel.grid(column=col, row=seriesOffset)
    col=col+1

# create "new entry" fields
col = 0
for j in range(1):
    addEntryButton = tk.Button(window, text="+ Entry")
    addEntryButton.grid(column=col, row=newEntryButtonOffset)
    col = col + 1

window.lift()
window.attributes('-topmost',True)
window.after_idle(window.attributes,'-topmost',False)
window.mainloop()