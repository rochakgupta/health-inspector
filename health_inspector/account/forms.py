import re
from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from material import *
from .models import CustomUser, Doctor, Parent, Child
from datetime import date, datetime

def phone_validator(val):
    if not re.match('^[789]\d{9}$', val):
        raise forms.ValidationError('Should be a 10 digit valid phone number')
        
def aadhar_validator(val):
    if not re.match('^\d{16}$', val):
        raise ValidationError('Should be a 16 digit valid aadhar number')

class LoginForm(forms.Form):
    phone = forms.CharField(label='Phone Number', max_length = 10, validators=[phone_validator])
    password = forms.CharField(widget = forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.authenticated_user = None
        super(LoginForm, self).__init__(*args, **kwargs)
    
    def clean_phone(self):
        data_phone = self.cleaned_data.get('phone', '')
        if data_phone and not CustomUser.objects.filter(phone = data_phone).exists():
            raise forms.ValidationError('Unregistered Number')
        return data_phone

    def clean(self):
        data_phone = self.cleaned_data.get('phone', '')
        data_password = self.cleaned_data.get('password', '')
        user = authenticate(phone = data_phone, password = data_password)
        if data_phone and data_password and not user:
            raise forms.ValidationError('Phone Number/Password do not match')
        self.authenticated_user = user
        return self.cleaned_data


class BaseSignupForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput)
    confirm_password = forms.CharField(widget = forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(BaseSignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = False
        
    def clean_phone(self):
        data_phone = self.cleaned_data.get('phone', '')
        if data_phone and CustomUser.objects.filter(phone = data_phone).exists():
            raise forms.ValidationError('User with this phone number already exists')
        return data_phone

    def clean_confirm_password(self):
        data_password = self.cleaned_data.get('password')
        data_confirm_password = self.cleaned_data.get('confirm_password')
        if (data_password != data_confirm_password):
            raise forms.ValidationError("The two passwords field didn't match")
        return data_confirm_password

    class Meta:
        model = CustomUser
        fields = ['phone', 'first_name', 'last_name', 'gender']
        
class DoctorSignupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DoctorSignupForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Doctor
        fields = ['hospital']
        
        
class ParentSignupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ParentSignupForm, self).__init__(*args, **kwargs)
        self.fields['aadhar'].label = 'Aadhar Number'

    def clean_aadhar(self):
        data_aadhar = self.cleaned_data.get('aadhar', '')
        if data_aadhar and Parent.objects.filter(aadhar = data_aadhar).exists():
            raise forms.ValidationError('This aadhar number is already registered with')
        return data_aadhar

    class Meta:
        model = Parent
        fields = ['aadhar']
        
class ChildSignupForm(forms.ModelForm):
    parent_phone = forms.CharField(label="Parent's Phone Number", max_length = 10, validators=[phone_validator])
    
    def __init__(self, *args, **kwargs):
        self.valid_parent = None
        super(ChildSignupForm, self).__init__(*args, **kwargs)
        self.fields['dob'].input_formats=['%d/%m/%Y']
        self.fields['dob'].label='Date of Birth'
        self.fields['dob'].initial=datetime.now()
        
    def clean_dob(self):
        data_dob = self.cleaned_data.get('dob', '')
        if data_dob and (not data_dob <= date.today()):
            raise forms.ValidationError('Date of birth cannot be in the future')
        return data_dob
        
    def clean_parent_phone(self):
        data_parent_phone = self.cleaned_data.get('parent_phone', '')
        if data_parent_phone:
            custom_user = CustomUser.objects.filter(phone = data_parent_phone)
            if not custom_user.exists():
                raise forms.ValidationError('Unregistered Number')
            else:
                parents = Parent.objects.filter(parent_id=custom_user[0].id)
                if not parents.exists():
                    raise forms.ValidationError('User is registered only as a doctor. Must register as parent too.')
                else:
                    self.valid_parent = parents[0]
        return data_parent_phone

    class Meta:
        model = Child
        fields = ['dob', 'first_name', 'last_name', 'gender', 'parent_phone'] 


#class ProfileForm(forms.ModelForm):
#    old_password = forms.CharField(widget = forms.PasswordInput, required = False)
#    new_password = forms.CharField(widget = forms.PasswordInput, required = False)
#    layout = Layout(
#        Row('username'),
#        Row('email'),
#        Row(Span6('first_name'), Span6('last_name')),
#        Row(Span2('gender'), Span4('dob'), Span6('phone')),
#        Row('profile_pic'),
#        Row('old_password', 'new_password')
#    )
#
#    def __init__(self, *args, **kwargs):
#        super(ProfileForm, self).__init__(*args, **kwargs)
#        self.fields['username'].widget.attrs['readonly'] = True
#        self.fields['email'].widget.attrs['readonly'] = True
##        self.fields['first_name'].required = True
#
#    def clean_gender(self):
#        data_gender = self.cleaned_data['gender']
#        if data_gender and (data_gender != 'M' and data_gender != 'F'):
#            raise forms.ValidationError('You must specify a valid gender')
#        return data_gender
#
#    def clean_old_password(self):
#        data_old_password = self.cleaned_data['old_password']
#        if data_old_password and not self.instance.check_password(data_old_password):
#            raise forms.ValidationError('Incorrect Password')
#        return data_old_password
#
#    def clean_new_password(self):
#        data_old_password = self.cleaned_data['old_password']
#        data_new_password = self.cleaned_data['new_password']
#        if not data_old_password and data_new_password:
#            raise forms.ValidationError('Please specify old password')
#        if data_old_password and not data_new_password:
#            raise forms.ValidationError('Please specify new password')
#        if data_new_password and data_old_password and data_old_password == data_new_password:
#            raise forms.ValidationError('New password should not be same as old password')
#        return data_new_password
#    
#    def clean_username(self):
#        data_username = self.cleaned_data['username']
#        if data_username != self.instance.username:
#            raise forms.ValidationError('Invalid Username')
#        return data_username
#    
#    def clean_email(self):
#        data_email = self.cleaned_data['email']
#        if data_email != self.instance.email:
#            raise forms.ValidationError('Invalid Email')
#        return data_email
#    
#    class Meta:
#        model = MyUser
#        fields = ['username', 'email', 'first_name', 'last_name', 'profile_pic', 'gender', 'dob', 'phone']
