from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from django.contrib.auth import logout
class LoginPage(View):
    def get(self, request):
        return render(request, 'account/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = authenticate(request, username=username, password=password)

        if user_obj is not None:
            if user_obj.groups.filter(name='Database Admin').exists():
                login(request, user_obj)
                return redirect('index_page')
            else:
                message_error = "This user group can't login on this page"
                return render(request, 'account/login.html', {'message_error': message_error})
        else:
            message_error = 'Invalid username or password'
            context = {'username': username, 'message_error': message_error}
            return render(request, 'account/login.html', context)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')