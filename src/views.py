import eel
import os, requests, json
from .settings import *
from .render import render

class Views:

    """                        data=json.dumps({ 
                        "token": data['token'],
                    }),"""
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
    def select_friends():
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.get(
                url=f"{HOST}select_friends",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                print(response_data.get('friends_list', []))
                return response_data.get('friends_list', [])
            else:
                return render(data={'error': True, 'message': f'Ошибка {response.status_code}'})
                
        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
        
        
    @eel.expose
    def accept_friend_request(request_id):
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.post(
                url=f"{HOST}accept_friend_request",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                },
                data=json.dumps({
                    "request_id": request_id,
                })
            )
            
            response_data = response.json()
            print(response_data.get('messages', []))
            return response_data.get('messages', [])
        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
        
        
    @eel.expose
    def get_messages(chat_id):
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.post(
                url=f"{HOST}get_messages",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                },
                data=json.dumps({
                    "chat_id": chat_id,
                })
            )
            
            response_data = response.json()
            print(response_data.get('messages', []))
            return response_data.get('messages', [])
        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
        
    @eel.expose
    def send_message(message_data):
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(message_data.get('chat'))
            response = requests.post(
                url=f"{HOST}send_message",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                },
                data=json.dumps({
                    "chat_id": message_data.get('chat'),
                    "text": message_data.get('text'),
                    "type": message_data.get('type'),
                    "file": message_data.get('file')
                    
                })
            )
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
        
    @eel.expose
    def chek_for_friends_requests():
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.get(
                url=f"{HOST}chek_for_friends_requests",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                },

            )
            
            friends_requsets = response.json()
            print(friends_requsets.get('friends_requsets', []))
            return friends_requsets.get('friends_requsets', [])
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
        
        
        
    
    @eel.expose
    def select_users_for_add():
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            response = requests.get(
                url=f"{HOST}select_users_for_add",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Token {data["token"]}'
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                print(response_data.get('users', []))
                return response_data.get('users', [])
            else:
                return render(data={'error': True, 'message': f'Ошибка {response.status_code}'})
                
        except Exception as e:
            print(f"Ошибка: {e}")
            return render(data={'error': True, 'message': str(e)})
    


    
