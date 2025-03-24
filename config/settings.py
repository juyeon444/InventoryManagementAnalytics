import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_stylesheet():
    """Load the application stylesheet from QSS file."""
    qss_file = os.path.join(BASE_DIR, "styles", "app_styles.qss")
    try:
        with open(qss_file, "r") as f:
            return f.read()
    except FileNotFoundError:
        print("[WARNING] Stylesheet file not found.")
        return "" 
