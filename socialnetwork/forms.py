from django import forms

from django.contrib.auth.models import User
from models import *

MAX_UPLOAD_SIZE = 2500000

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=20)
    firstname = forms.CharField(max_length= 40, label="First Name")
    lastname = forms.CharField(max_length=40, label="Last Name")
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())

    def save(self, commit = True):
        user= super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['firstname']
        user.last_name = self.cleaned_data['lastname']
        
    

 # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()
         # We must return the cleaned data we got from our parent.

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        # Did not use code below because already validating via views.py
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        # Did not use code below because already validating via views.py
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class EditProfile(forms.ModelForm):
    firstname = forms.CharField(max_length= 40, label="First Name")
    lastname = forms.CharField(max_length=40, label="Last Name")
    class Meta:
        model = Person
        fields = ('photo', 'firstname', 'lastname', 'age', 'bio')

    def clean_photo(self):
        photo = self.cleaned_data['photo']
        if photo:
            if photo.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
            try:
                if not photo.content_type or not photo.content_type.startswith('image'):
                    raise forms.ValidationError('Must be an image file')
                    # in practice, will just have the user redirected and keep original photo they uploaded
                    # will still allow them to submit other, valid data from the form
            except:
                return photo
        else:
            return photo

    def clean_age(self):
        age = self.cleaned_data['age']
        try:
            int(age)
            if age < 0:
                raise forms.ValidationError('Age must be a positive number')
        except:
            raise forms.ValidationError('Age must be a valid number')
        return age

class MakePost(forms.ModelForm):
    text = forms.CharField(max_length=160, widget=forms.Textarea, label="")
    class Meta:
        model = Message
        exclude = (
            'user',
            'messageTime',
        )

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text)<1:
            raise forms.ValidationError('You must enter some text to post')
        if len(text)>160:
            raise forms.ValidationError('You cannot post more than 160 characters')
        return text
