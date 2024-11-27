from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

def index(request):
    user_roles = request.session.get('user_roles', [])
    return render(request, 'dashboard.html', {'user_roles': user_roles})


def Signup(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        pass1 = request.POST.get('pass1', '').strip()
        pass2 = request.POST.get('pass2', '').strip()

        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'Signup.html')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'Signup.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return render(request, 'Signup.html')

        try:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=pass1)

            # Add the user to the "Client" group
            client_group, created = Group.objects.get_or_create(name='Client')  # Ensure the group exists
            user.groups.add(client_group)

            user.save()
            messages.success(request, "Account created successfully!")
            return redirect(Signin)
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return render(request, 'Signup.html')

    return render(request, 'Signup.html')


def Signin(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        pass1 = request.POST.get('pass1', '').strip()

        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=pass1)

            if user is not None:
                login(request, user)
                # Fetch user's role(s)
                user_roles = user.groups.values_list('name', flat=True)  # Get roles as a list
                role_display = ', '.join(user_roles) if user_roles else 'No role assigned'

                messages.success(request, f"Login successful! Your role: {role_display}.")
                # Pass roles as context to the dashboard
                request.session['user_roles'] = list(user_roles)  # Save roles in session
                return redirect(index)  # Redirect to the dashboard

            else:
                messages.error(request, "Invalid email or password!")
                return render(request, 'Signin.html', {'email': email})

        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist!")
            return render(request, 'Signin.html', {'email': email})

    return render(request, 'Signin.html')



def Signout(request):
    logout(request)
    messages.success(request,"Logout Successfully!")
    return redirect(index)


@login_required
def Profile(request):
    if request.method == "POST":
        # Get data from the form
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        old_password = request.POST.get('old_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()

        try:
            user = request.user

            # Validate username and email
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, "Username is already taken!")
                return render(request, "profile.html")

            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "Email is already in use!")
                return render(request, "profile.html")

            # Update username and email
            user.username = username
            user.email = email

            # Verify and update password if provided
            if old_password and new_password:  # Both old and new passwords must be filled
                if not check_password(old_password, user.password):
                    messages.error(request, "Old password is incorrect!")
                    return render(request, "profile.html", {'user': user})

                if len(new_password) < 8:
                    messages.error(request, "New password must be at least 8 characters long!")
                    return render(request, "profile.html", {'user': user})

                user.set_password(new_password)  # Hash and set the new password
                user.save()

                # Log out the user and redirect to login page
                logout(request)
                messages.success(request, "Your password has been updated. Please log in again.")
                return redirect(Signin)  

            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect(Profile)  # Redirect to avoid form resubmission

        except Exception as e:
            messages.error(request, f"Error updating profile: {e}")
            return render(request, "profile.html", {'user': user})
    user_roles = request.session.get('user_roles', [])
    return render(request, "profile.html", {'user': request.user,'user_roles': user_roles})
