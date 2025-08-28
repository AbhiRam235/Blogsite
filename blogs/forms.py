
from django import forms
from .models import Blog, BlogBlock, User
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border rounded', 'placeholder': 'Username'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded', 'placeholder': 'Password'}))

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded', 'placeholder': 'Password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
    
class BlogBlockInlineForm(forms.ModelForm):
    class Meta:
        model = BlogBlock
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BlogBlockInlineForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.content_type == 'image':
            self.fields['content'].widget = forms.HiddenInput()
        else:
            self.fields['image'].widget = forms.HiddenInput()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'profile_photo', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
        }

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Blog Title'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

class BlogBlockForm(forms.ModelForm):
    class Meta:
        model = BlogBlock
        fields = ['block_number', 'content_type', 'content', 'image']
        widgets = {
            'block_number': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Block Number'}),
            'content_type': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'content': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Content'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }