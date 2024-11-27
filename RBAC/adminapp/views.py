from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from RBAC.views import Signin
from django.http import HttpResponseForbidden

def users_list(request):
    if not request.user.is_authenticated:
        return redirect('Signin')  # Redirect to login if the user is not authenticated

    # Fetch the roles of the logged-in user
    user_roles = request.user.groups.values_list("name", flat=True)

    # Default: Admin sees all users
    if "Admin" in user_roles:
        users = User.objects.all()
    elif "Manager" in user_roles:
        # Managers see only users in the 'Client' group
        client_group = Group.objects.get(name="Client")
        users = User.objects.filter(groups=client_group)
    else:
        users = User.objects.none()  # No users for unauthorized roles

    # Prepare user data for the template
    user_data = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": ", ".join(user.groups.values_list("name", flat=True)),
            "is_active": user.is_active,
        }
        for user in users
    ]

    return render(request, 'users_list.html', {"users": user_data, "user_roles": user_roles})


def AddUser(request):
    user_roles = request.user.groups.values_list("name", flat=True)
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        pass1 = request.POST.get('pass1', '').strip()

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'adduser.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return render(request, 'adduser.html')

        try:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=pass1)

            # Add the user to the "Client" group
            client_group, created = Group.objects.get_or_create(name='Client')  # Ensure the group exists
            user.groups.add(client_group)

            user.save()
            messages.success(request, "Account created successfully!")
            return redirect(users_list)
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return render(request, 'user_list.html')

    return render(request, 'adduser.html',{"user_roles": user_roles})

@login_required
def Delete(request, user_id):
    # Fetch the user to delete
    user_to_delete = get_object_or_404(User, id=user_id)

    # Admins can delete anyone except superusers
    if request.user.groups.filter(name="Admin").exists():
        if user_to_delete.is_superuser:
            messages.error(request, "You cannot delete a superuser!")
            return redirect('users_list')
        try:
            user_to_delete.delete()
            messages.success(request, f"User {user_to_delete.username} deleted successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the user: {e}")
        return redirect('users_list')

    # Managers can only delete users in the "Client" group
    elif request.user.groups.filter(name="Manager").exists():
        if user_to_delete.groups.filter(name="Client").exists():
            try:
                user_to_delete.delete()
                messages.success(request, f"Client {user_to_delete.username} deleted successfully.")
            except Exception as e:
                messages.error(request, f"An error occurred while deleting the user: {e}")
        else:
            messages.error(request, "You do not have permission to delete this user.")
        return redirect('users_list')

    # All other roles are forbidden from deleting
    else:
        return HttpResponseForbidden("You do not have permission to perform this action.")
    

@login_required
def update_user_role(request, user_id):
    if request.method == "POST":
        new_role = request.POST.get('role')
        new_status = request.POST.get('status')  # Get the new status (active/inactive)
        
        user = get_object_or_404(User, id=user_id)

        # Prevent the logged-in admin from changing their own role
        if request.user == user:
            messages.error(request, "You cannot change your own role.")
            return redirect('users_list')

        # Check if the new role is valid
        if new_role not in ['Admin', 'Manager', 'Client']:  # Add other valid roles if necessary
            messages.error(request, "Invalid role selected.")
            return redirect('users_list')

        # Check if the new status is valid
        if new_status not in ['True', 'False']:  # Ensure status is either 'True' or 'False'
            messages.error(request, "Invalid status selected.")
            return redirect('users_list')

        # Update the user's roles
        user.groups.clear()  # Clear existing roles
        group, created = Group.objects.get_or_create(name=new_role)
        user.groups.add(group)  # Add the new role

        # Update the user's status (active or inactive)
        user.is_active = new_status == 'True'
        
        user.save()

        messages.success(request, f"Role and status for {user.username} updated.")
    
    return redirect('users_list')

@login_required
def Permission(request):
    user_roles = [group.name for group in request.user.groups.all()]
    return render(request, 'permission.html', {'user_roles': user_roles})