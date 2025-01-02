from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, MBTIType
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, MBTIType, Feedback
class UserRegistrationForm(UserCreationForm):
    mbti_type = forms.ModelChoiceField(
        queryset=MBTIType.objects.all(),
        empty_label="Select MBTI Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'mbti_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ['username', 'password']



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']  # Only include the 'message' field for feedback

class EditBioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell others about yourself!'}),
        }

from django import forms
from .models import PersonalizedList, PersonalizedMovie, PersonalizedBook

class PersonalizedListForm(forms.ModelForm):
    class Meta:
        model = PersonalizedList
        fields = ['list_name']

class PersonalizedMovieForm(forms.ModelForm):
    class Meta:
        model = PersonalizedMovie
        fields = ['movie', 'rating', 'review']

class PersonalizedBookForm(forms.ModelForm):
    class Meta:
        model = PersonalizedBook
        fields = ['book', 'rating', 'review']
