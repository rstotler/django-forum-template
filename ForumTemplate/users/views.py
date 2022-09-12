from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as user_login
from django.contrib.auth import logout as user_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from forum import models as forum_models
from .forms import RegistrationForm, LoginForm, ProfileForm

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            data = request.POST.copy()
            updateList = updateProfileCheck(request)
            if updateList != []:
            
                # Update Profile #
                if 'form invalid' not in updateList:
                    
                    # Reset/Update Username #
                    if 'update username' in updateList:
                        request.user.username = request.POST['username']
                        request.user.save()
                        messages.info(request, f'Username updated.')
                        
                    # Password #
                    if 'update password' in updateList:
                        request.user.set_password(request.POST['password'])
                        request.user.save()
                        user_login(request, request.user)
                        messages.info(request, f'Password updated.')
                        
                    # Email #
                    if 'update email' in updateList:
                        request.user.email = request.POST['email']
                        request.user.save()
                        messages.info(request, f'Email updated.')
                        
                    # Profile Picture Message #
                    if 'update profile picture' in updateList:
                        imageFile = request.FILES['profileImage']
                        request.user.profile.image = imageFile
                        request.user.profile.save()
                        messages.info(request, f'Profile picture updated.')
                    
                # Reset Form Data #
                else:
                    if 'form invalid' in updateList:
                        data['username'] = request.user.username
                        data['email'] = request.user.email
            
            form = ProfileForm(data)
            
    else:
        form = ProfileForm(initial={'username': request.user.username, 'email': request.user.email})
        
    return render(request, 'users/profile.html', {'form': form})

def updateProfileCheck(request):
    
    updateList = []
    
    # Check If Entered Username Is Different & Unique #
    if request.POST['username'].lower() != request.user.username.lower():
        targetUserList = User.objects.filter(username__iexact=request.POST['username'])
        if len(targetUserList) == 0:
            updateList.append('update username')
        else:
            updateList.append('form invalid')
            updateList.append('username exists')
            messages.warning(request, f'Username already exists.')
        
    # Check If Entered Password Is Different & Match #
    if request.POST['password'] == "" and request.POST['passwordVerify'] != "":
        updateList.append('form invalid')
        messages.warning(request, f'Passwords do not match.')
    elif request.POST['password'] != "":
        userCheck = authenticate(request, username=request.user.username, password=request.POST['password'])
        if request.POST['password'] != request.POST['passwordVerify']:
            updateList.append('form invalid')
            messages.warning(request, f'Passwords do not match.')
        elif userCheck != None:
            updateList.append('form invalid')
            messages.warning(request, f'New password must be different than current password.')
        else:
            updateList.append('update password')
            
    # Check If Entered Email Is Different & Unique #
    if request.POST['email'].lower() != request.user.email.lower():
        targetUserList = User.objects.filter(email__iexact=request.POST['email'])
        if len(targetUserList) == 0:
            updateList.append('update email')
        else:
            updateList.append('form invalid')
            updateList.append('email exists')
            messages.warning(request, f'Email already exists.')
            
    # Profile Picture #
    if 'profileImage' in request.FILES:
        updateList.append('update profile picture')
           
    return updateList

def publicProfile(request, username):
    userData = User.objects.filter(username=username).first()
    if userData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'User not found!'})
        
    latestThreadList = forum_models.Thread.objects.filter(author=userData).exclude(isLocked=True).order_by('-date_posted')[:5]
    lastReplyList = forum_models.Post.objects.filter(author=userData).order_by('-date_posted')[:5]
    
    return render(request, 'users/public_profile.html', {'userData': userData, 'latestThreadList': latestThreadList, 'lastReplyList': lastReplyList})

def login(request):
    if request.user.is_authenticated:
        return redirect('subforum-list')
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        targetUser = loginCheck(request)
        if targetUser != None:
            user_login(request, targetUser)
            return redirect(request.GET.get('next', 'subforum-list'))
        else:
            messages.warning(request, f'Incorrect Username/Password.')
        
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def loginCheck(request):

    # Check If Username Exists #
    inputUser = request.POST['username']
    targetUserList = User.objects.filter(username__iexact=inputUser)
    if len(targetUserList) == 1:
        
        # Check Username/Password #
        targetUser = authenticate(request, username=targetUserList.first().username, password=request.POST['password'])
        if targetUser != None:
            return targetUser
        
    return None

def logout(request):
    if request.user.is_authenticated:
        user_logout(request)
        messages.info(request, f'You have been logged out.')
        
    return redirect(request.META.get('HTTP_REFERER'))
    
def register(request):
    if request.user.is_authenticated:
        return redirect('subforum-list')
    
    elif request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            if registerCheck(request):
                targetUser = User.objects.create_user(username=request.POST['username'],
                                         password=request.POST['password'],
                                         email=request.POST['email'])
                user_login(request, targetUser)
                messages.info(request, f'Account created. You are now logged in.')
                return redirect('subforum-list')
    
    else:
        form = RegistrationForm()
        
    return render(request, 'users/register.html', {'form': form})
    
def registerCheck(request):

    check = True

    # Check If Username Exists #
    inputUser = request.POST['username']
    targetUserList = User.objects.filter(username__iexact=inputUser)
    if len(targetUserList) >= 1:
        messages.warning(request, f'Username already exists.')
        check = False
        
    # Check If Passwords Match #
    if request.POST['password'] != request.POST['passwordVerify']:
        messages.warning(request, f'Passwords do not match.')
        check = False
        
    # Check If Email Exists #
    inputEmail = request.POST['email']
    targetUserEmailList = User.objects.filter(email__iexact=inputEmail)
    if len(targetUserEmailList) >= 1:
        messages.warning(request, f'Email already exists.')
        check = False
        
    return check
