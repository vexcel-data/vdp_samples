import requests
import json
import os

def login(credentials=None, vdp_password_var="VDP_PASSWORD", vdp_username_var="VDP_USERNAME"):
    if credentials is None:
        password = os.environ.get(vdp_password_var)
        username = os.environ.get(vdp_username_var)
        if password is None:
            raise ValueError(f"No password found for environment variable {vdp_password_var}. Make sure to set it before calling this function")
        if username is None:
            raise ValueError(f"No username found for environment variable {vdp_username_var}. Make sure to set it before calling this function")
        credentials = {'password': password, 'username': username}
    
    r = requests.post("https://api.gic.org/auth/Login/", data=credentials)
    token = r.json()['token']
    return token