from django.contrib.auth.forms import UserCreationForm, UserChangeForm,AuthenticationForm,PasswordChangeForm
from .models import User
from django import forms

# Signup Form. Visible at /signup
class UserCreationForm(UserCreationForm):
    email = forms.EmailField(label="",widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    name = forms.CharField(label="",widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    password1 = forms.CharField(label="",widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(label="",widget=forms.PasswordInput(attrs={'placeholder': 'Password Confirmation'}))
    class Meta(UserCreationForm):
        model = User
        fields = ('email','name')

# Change user password without old password. Don't use this.
class UserChangeForm(UserChangeForm):
    
    class Meta:
        model = User
        fields = ('email','name')

# Login the user. Visible at /login
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label="",widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label="",widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    class Meta:
        model = User
        fields = ('email','password')

# Change user password with old password.
class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="",widget=forms.PasswordInput(attrs={'placeholder': 'Old Password'}))
    new_password1 = forms.CharField(label="",widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    new_password2 = forms.CharField(label="",widget=forms.PasswordInput(attrs={'placeholder': 'New Password Confirmation'}))
    class Meta:
        model = User

# class FeedBackForm(forms.Form):
#     name = forms.CharField(max_length=63, required=True)
#     email = forms.EmailField(max_length=254, required=True)
#     subject = forms.CharField(max_length=127, required=True)
#     message = forms.CharField(max_length=511, required=True)

#     def save(self):
#         try:
#             data = self.cleaned_data
#             feedback = Feedback(name=data['name'],email=data['email'], subject=data['subject'],message=data["message"])
#             feedback.save()
#         except:
#             return False
#         else:
#             return True

#     class Meta:
#         model = Feedback