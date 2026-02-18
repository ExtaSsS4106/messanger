import eel
import os, requests, json
from .settings import *
from .render import render

class Views:

    
    @eel.expose
    def GET_HOST():
        return HOST
    
    @eel.expose
    def start_page():
        return render("web/pages/registration/homepage.html")
    
    @eel.expose
    def main():
        return render("web/pages/main/main.html")
    
    @eel.expose
    def login(username=None, passwd=None):
        if username and passwd:
            print(username, passwd)
            r = requests.post(
                    url=f"{HOST}/api/login",
                    data=json.dumps({ 
                        "username": username,
                        "password": passwd
                    }),
                    headers={
                        'Content-Type': 'application/json'
                    }
                )
            print(r.status_code)
            print(r.json())
            if r.status_code == 200:
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(r.json(), f, indent=4, ensure_ascii=False)
                return True
            return False
        else:
            return render("web/pages/registration/login.html")
    
    
    @eel.expose
    def sign_up(username=None,email=None,password1=None,password2=None):
        if username and email and password1 and password2:
            print(username,email,password1,password2)
            r = requests.post(
                    url=f"{HOST}/api/sign_up",
                    data=json.dumps({
                        "username": username,
                        "email": email,
                        "password1": password1,
                        "password2": password2
                    }),
                    headers={
                        'Content-Type': 'application/json'
                    }
                )
            print(r.status_code)
            print(r.json())
            if r.status_code == 200:
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(r.json(), f, indent=4, ensure_ascii=False)
                return True
        else:
            return render("web/pages/registration/register.html")
        
    
    
    


    
