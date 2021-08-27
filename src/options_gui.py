# imports
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
import tkinter as tk

# ----------------------------------------- INPUTS -----------------------------------------
column_names = ["Stock Symbol","Expiry","Type","Buy/Sell","Open\nPrice/Share","# Shares",\
                "Current\nPrice/Share","Strike","Premium","# Contracts","Close\nStrategy",\
                "Close\nPrice/Share","Close\nPremium","Fee","Profit/Loss",\
                "Net Realized P/L\nFor Underlier","Status","Account"]
maxColumns = 26
maxRows = 30
# ------------------------------------------------------------

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
seriesOffset = 11
col = 0
for label in column_names:
    columnLabel = tk.Label( text=label,\
                            font='"Helvetica Neue" 14 bold')
    columnLabel.grid(column=col, row=seriesOffset)
    col=col+1

window.lift()
window.attributes('-topmost',True)
window.after_idle(window.attributes,'-topmost',False)
window.mainloop()