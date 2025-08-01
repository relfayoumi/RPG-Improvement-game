# main.py

import sys
from PyQt5.QtWidgets import QApplication
from gui import ApplicationController # Import ApplicationController instead of GameGUI
from game_manager import GameManager
# config, levels_csv, etc. are imported within GameManager via its init

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize the game manager.
    # Set 'force_new_game=True' to always start with fresh data,
    # discarding any existing save file at startup.
    # If you want to load previously saved data in the future, change this to 'False'.
    game_manager = GameManager(force_new_game=False)

    # Create and show the main window using ApplicationController
    controller = ApplicationController(game_manager) # Instantiate ApplicationController
    # The ApplicationController internally handles showing the welcome screen and then the main GUI.

    # Ensure the application exits cleanly
    sys.exit(app.exec_())