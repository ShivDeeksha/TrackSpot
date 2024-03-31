from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import WebsiteUser, UploadedItem

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = WebsiteUser
        fields = ['first_name', 'middle_name', 'last_name', 'username', 'email', 'phone_number', 'prn_number', 'college_id_image']

    def clean_username(self):
        username = self.cleaned_data['username']
        if WebsiteUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Set the hashed password
        if commit:
            user.save()
        return user



class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = WebsiteUser
        fields = ['profile_image']

class UploadedItemForm(forms.ModelForm):
    class Meta:
        model = UploadedItem
        fields = ['name', 'description', 'location', 'image']