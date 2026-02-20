import eel
import os

    
    
def render(file_path=None, data=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        if file_path and data:
            return content, data
        elif file_path and data == None:
            return content
        elif data and file_path == None:
            return data
        else:
            raise ValueError("Не переданы ни file_path, ни data") 
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
    except Exception as e:
        print(e)       





"""@eel.expose
def login():
    try:
        filename = "login.html"
        file_path = os.path.join('web', 'pages', 'registration', filename)
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"<h1>Файл {filename} не найден</h1>"
    except Exception as e:
        print(e)

@eel.expose
def register():
    try:
        filename = "register.html"
        file_path = os.path.join('web', 'pages', 'registration', filename)
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"<h1>Файл {filename} не найден</h1>"
    except Exception as e:
        print(e)

@eel.expose
def main():
    try:
        filename = "main.html"
        file_path = os.path.join('web', 'pages', 'main', filename)
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"<h1>Файл {filename} не найден</h1>"
    except Exception as e:
        print(e)"""