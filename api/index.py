import sys
import os

# Add the root directory to sys.path to allow importing from 'web' and 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web.app import app

# This is required for Vercel to pick up the Flask app
# The variable must be named 'app'
# We just need to make sure 'app' is available in this module's scope
