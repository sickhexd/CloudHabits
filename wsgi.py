import sys
import os
from app.main import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
application = app

