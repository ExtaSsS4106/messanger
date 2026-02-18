import eel
import os

    
    
def render(file_path, data=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        if data:
            return content, data
        return content
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