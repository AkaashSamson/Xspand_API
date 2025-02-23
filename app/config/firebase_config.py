from firebase_admin import credentials, initialize_app
# from dotenv import load_dotenv
import os
import base64
import json

def init_firebase():
    # load_dotenv()
    # Decode the base64 string and parse it as JSON
    firebase_config_cred = json.loads(base64.b64decode(os.getenv("FIREBASE_CONFIG_CRED")).decode('utf-8'))
    cred = credentials.Certificate(firebase_config_cred)
    initialize_app(cred)