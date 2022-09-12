from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

class ProfileForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput({'maxlength':256, 'placeholder': 'New Username'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput({'maxlength':256, 'minlength':8, 'placeholder': 'New Password'}))
    passwordVerify = forms.CharField(required=False, widget=forms.PasswordInput({'maxlength':256, 'minlength':8, 'placeholder': 'Retype Password'}))
    email = forms.EmailField(widget=forms.TextInput({'maxlength':256, 'placeholder': 'E-Mail'}))
    profileImage = forms.ImageField(required=False)
    
    def __int__(self):
        self.fields['password'].required = False
        
    def clean_username(self):
        if ' ' in self.cleaned_data['username']:
            raise forms.ValidationError('Cannot contain spaces.')
            
    def clean_password(self):
        
        if self.cleaned_data['password'] == "":
            return
        
        errorList = []
        
        if ' ' in self.cleaned_data['password']:
            errorList.append('Cannot contain spaces.')
        numberCheck = any(i.isdigit() for i in self.cleaned_data['password'])
        if numberCheck == False:
            errorList.append('Must contain a number.')
        letterCheck = any(i.isalpha() for i in self.cleaned_data['password'])
        if letterCheck == False:
            errorList.append('Must contain a letter.')
            
        if len(errorList) > 0:
            raise forms.ValidationError(errorList)

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput({'maxlength':255, 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput({'maxlength':255, 'minlength':8, 'placeholder': 'Password'}))

class RegistrationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput({'maxlength':255, 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput({'maxlength':255, 'minlength':8, 'placeholder': 'Password'}))
    passwordVerify = forms.CharField(widget=forms.PasswordInput({'maxlength':255, 'minlength':8, 'placeholder': 'Retype Password'}))
    email = forms.EmailField(widget=forms.TextInput({'maxlength':255, 'placeholder': 'E-Mail'}))
    
    def clean_username(self):
        if ' ' in self.cleaned_data['username']:
            raise forms.ValidationError('Cannot contain spaces.')
            
    def clean_password(self):
        
        errorList = []
        
        if ' ' in self.cleaned_data['password']:
            errorList.append('Cannot contain spaces.')
        numberCheck = any(i.isdigit() for i in self.cleaned_data['password'])
        if numberCheck == False:
            errorList.append('Must contain a number.')
        letterCheck = any(i.isalpha() for i in self.cleaned_data['password'])
        if letterCheck == False:
            errorList.append('Must contain a letter.')
            
        if len(errorList) > 0:
            raise forms.ValidationError(errorList)
                
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'maxlength':255, 'placeholder': 'Email'}))
        
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        
class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'maxlength':255, 'minlength':8, 'placeholder': 'Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'maxlength':255, 'minlength':8, 'placeholder': 'Verify Password'}))
        
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetConfirmForm, self).__init__(*args, **kwargs)
