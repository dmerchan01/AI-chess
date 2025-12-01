import tkinter as tk
from interface import ChessGUI

# Main function to start the GUI
def main():

    # Create the main window and start the GUI
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

# Entry point
if __name__ == "__main__":
    main()
