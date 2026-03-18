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
        with open('data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(data)
        return render("web/pages/main/main.html", data)
    
    @eel.expose
    def add_friends():
        return render("web/pages/main/add-friend.html")
    
    @eel.expose
    def create_channel():
        return render("web/pages/main/create-channel.html")
    
    
    
    
    
    
    @eel.expose
    def send_friend_request(id):
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.post(
                url=f"{HOST}send_friend_request",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                },
                data=json.dumps({
                    "user_id": id,
                })
            )
            

        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
        
    @eel.expose
    def remove_friend_api(user_id):
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.post(
                url=f"{HOST}remove_friend_api",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                },
                data=json.dumps({
                    "user_id": user_id,
                })
            )
            

        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
    
    
    
    @eel.expose
    def select_chats():
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.get(
                url=f"{HOST}select_chats",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                }
            )
            
            
            response_data = response.json()
            print(response_data.get('users_chats', []))
            return response_data.get('users_chats', [])
            
                
        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
    
    @eel.expose
    def select_products():
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.get(
                url=f"{HOST}select_all",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                print(response_data.get('data', []))
                return response_data['data']['data']
            else:
                return render(data={'error': True, 'message': f'Ошибка {response.status_code}'})
                
        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
        
        

        


        
        
        
    
    @eel.expose
    def login(username=None, passwd=None):
        if username and passwd:
            print(username, passwd)
            r = requests.post(
                    url=f"{HOST}login",
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
                    url=f"{HOST}sign_up",
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
        
        
        
    



    
