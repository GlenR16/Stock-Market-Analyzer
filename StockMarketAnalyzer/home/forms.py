from django.contrib.auth.forms import UserCreationForm, UserChangeForm,AuthenticationForm,PasswordChangeForm
from .models import User

# Signup Form. Visible at /signup
class UserCreationForm(UserCreationForm):
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
    class Meta:
        model = User
        fields = ('email','password')

# Change user password with old password.
class PasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User