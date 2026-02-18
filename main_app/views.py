from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout
from .forms import RegisterForm

# Авторизация\Регистрация

def index(request):
    return render(request, 'registration/index.html')

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('/')


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})


#Главная

@login_required()
def home(request):
    return render(request, 'main/home.html')

