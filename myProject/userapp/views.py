# from django.shortcuts import render,redirect
# from django.contrib.auth.models import User,auth
# from django.contrib import messages
# # Create your views here.
# def user(request):
#     if request.method=='POST':
#         username=request.POST.get('username')
#         email=request.POST.get('email')
#         password=request.POST.get('password')
#         confirmpassword=request.POST.get('confirmpassword')
#         if password==confirmpassword:
#             if User.objects.filter(username=username).exists():
#                 messages.info(request,"Username already taken")
#                 return redirect('register/')
#             elif User.objects.filter(email=email).exists():
#                 messages.info(request,"Email already taken")
#                 return redirect('register/')
#             else:
#                 user_reg=User.objects.create_user(username=username,email=email,password=password)
#                 user_reg.save()
#                 messages.info(request,"Successfully created")
#                 return redirect('/')
#         else:
#             messages.info(request,"Password doesn't match")
#             # return redirect('/register/')
#             return render(request, 'reg.html')

#     return render(request,'reg.html')
# def login(request):
#     if request.method=='POST':
#         username=request.POST.get('username')
#         password=request.POST.get('password')
#         user=auth.authenticate(username=username, password=password)
#         if user is not None:
#             auth.login(request,user)
#             messages.info(request,"Login Success")
#             return redirect('/')
#         else: 
#             # messages.info(request,"Invalid")
#             # return redirect('register/')
#             messages.error(request, "Invalid username or password")
        
#         # If authentication fails, stay on the login page and show the error
#         return render(request, 'log.html')


#     return render(request,'log.html')

# def logout(request):
#     auth.logout(request)
#     return redirect('/')


from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import UserProfile 

# Registration View
def user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        role = request.POST.get('role')

        if password == confirmpassword:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already taken")
                return render(request, 'reg.html')  # Stay on registration page to display error
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already taken")
                return render(request, 'reg.html')  # Stay on registration page to display error
            else:
                user_reg = User.objects.create_user(username=username, email=email, password=password)
                user_reg.save()

                user_profile = UserProfile(user=user_reg, role=role)
                user_profile.save()

                messages.success(request, "Account successfully created. You can now log in.")
                return redirect('login')  # Redirect to login page after successful registration
        else:
            messages.error(request, "Passwords do not match")
            return render(request, 'reg.html')  # Stay on registration page to display error

    return render(request, 'reg.html')


# Login View
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "Login successful!")
            # return redirect('home')  # Redirect to home page after successful login
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.role == 'Organizer':
                return redirect('organizer_dashboard')  # Redirect organizers to the dashboard
            else:
                return redirect('home')  # Redirect regular users to the home page
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'login.html')  # Stay on login page to display error

    return render(request, 'login.html')


# Logout View
def logout(request):
    auth.logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('/')  # Redirect to home or login page
