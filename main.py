import eel 

eel.init("web")


if __name__ == "__main__":
    from src.views import Views
    eel.start("pages/index.html", size=(1900, 1000), port=0)