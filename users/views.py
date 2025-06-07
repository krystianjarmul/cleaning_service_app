from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test


def not_logged_in(user):
    return not user.is_authenticated


@user_passes_test(not_logged_in, login_url='home')
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")  # przekierowanie po zalogowaniu
        else:
            return render(request, "users/login.html", {"error": "Nieprawidłowe dane logowania"})

    return render(request, "users/login.html", {"error": None})


def logout_view(request):
    logout(request)
    return redirect("login")
