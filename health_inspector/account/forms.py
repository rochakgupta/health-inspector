import re
from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from material import *
from .models import CustomUser, Doctor, Parent, Child, Task, Vaccine
from datetime import date, datetime

def phone_validator(val):
    if not re.match('^[789]\d{9}$', val):
        raise ValidationError('Should be a 10 digit valid phone number')
        
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
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].required = False
        self.fields['last_name'].label = 'Last Name'
        
    def clean_phone(self):
        data_phone = self.cleaned_data.get('phone', '')
        if data_phone and CustomUser.objects.filter(phone = data_phone).exists():
            raise forms.ValidationError('This phone number is already registered with')
        return data_phone

    def clean_confirm_password(self):
        data_password = self.cleaned_data.get('password')
        data_confirm_password = self.cleaned_data.get('confirm_password')
        if (data_password != data_confirm_password):
            raise forms.ValidationError("The two passwords field didn't match")
        return data_confirm_password

    class Meta:
        model = CustomUser
        fields = ['phone', 'first_name', 'last_name', 'gender','street','district', 'city', 'state', 'zipcode']
        
class DoctorSignupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DoctorSignupForm, self).__init__(*args, **kwargs)
        self.fields['hospital'].label = 'Hospital/Clinic'

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
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        
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
                    raise forms.ValidationError('This user is registered only as a doctor. Must register as parent too.')
                else:
                    self.valid_parent = parents[0]
        return data_parent_phone

    class Meta:
        model = Child
        fields = ['dob', 'first_name', 'last_name', 'gender', 'parent_phone'] 

class BaseEditForm(forms.ModelForm):
    old_password = forms.CharField(widget = forms.PasswordInput, required=False)
    new_password = forms.CharField(widget = forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        super(BaseEditForm, self).__init__(*args, **kwargs)
        self.fields['phone'].disabled = True
        self.fields['phone'].widget.attrs['disabled'] = 'disabled'
        self.fields['first_name'].required = True
        self.fields['last_name'].required = False
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
    
    def clean_old_password(self):
        data_old_password = self.cleaned_data.get('old_password','')
        if data_old_password and not self.instance.check_password(data_old_password):
            raise forms.ValidationError('Incorrect Password')
        return data_old_password

    def clean_new_password(self):
        data_old_password = self.cleaned_data.get('old_password','')
        data_new_password = self.cleaned_data.get('new_password','')
        if not data_old_password and data_new_password:
            raise forms.ValidationError('Please specify old password')
        if data_old_password and not data_new_password:
            raise forms.ValidationError('Please specify new password')
        if data_new_password and data_old_password and data_old_password == data_new_password:
            raise forms.ValidationError('New password should not be same as old password')
        return data_new_password

    class Meta:
        model = CustomUser
        fields = ['phone', 'first_name', 'last_name', 'gender','street','district', 'city', 'state', 'zipcode']
        
class DoctorEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DoctorEditForm, self).__init__(*args, **kwargs)
        self.fields['hospital'].label = 'Hospital/Clinic'

    class Meta:
        model = Doctor
        fields = ['hospital']
        
        
class ParentEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ParentEditForm, self).__init__(*args, **kwargs)
        self.fields['aadhar'].label = 'Aadhar Number'

    def clean_aadhar(self):
        data_aadhar = self.cleaned_data.get('aadhar', '')
        if data_aadhar and Parent.objects.filter(aadhar = data_aadhar).exists():
            raise forms.ValidationError('This aadhar number is already registered with.')
        return data_aadhar

    class Meta:
        model = Parent
        fields = ['aadhar']
        
class TaskCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.child_obj = kwargs.pop('child_obj')
        super(TaskCreateForm, self).__init__(*args, **kwargs)
        self.fields['due_date'].label = 'Due Date'
        self.fields['due_date'].initial = datetime.now()
        
    def clean_name(self):
        ALL_VACCINE_CHOICES = [vaccine.name for vaccine in Vaccine.objects.all()]
        CREATED_VACCINE_CHOICES = [task.name for task in Task.objects.filter(child=self.child_obj, category='V')]
        data_name = self.cleaned_data.get('name')
        data_category = self.cleaned_data.get('category')
        if data_category == 'V':
            if data_name in CREATED_VACCINE_CHOICES:
                raise forms.ValidationError('Task already created for this vaccine')
            elif data_name not in ALL_VACCINE_CHOICES: 
                raise forms.ValidationError('Choose a valid vaccine')
        return data_name
    
    def clean_due_date(self):
        data_due_date = self.cleaned_data.get('due_date', datetime.now())
        if data_due_date < date.today():
            raise forms.ValidationError('Due Date cannot be in the past.')
        return data_due_date
    
    class Meta:
        model = Task
        fields = ['category', 'name', 'reason', 'due_date']
        
class TaskEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskEditForm, self).__init__(*args, **kwargs)
        self.fields['due_date'].disabled = True
        self.fields['due_date'].widget.attrs['disabled'] = 'disabled'
        self.fields['category'].disabled = True
        self.fields['category'].widget.attrs['disabled'] = 'disabled'
        self.fields['name'].disabled = True
        self.fields['name'].widget.attrs['disabled'] = 'disabled'
        self.fields['given_date'].required = True
        self.fields['given_date'].label = 'Given Date'
        
    def clean_given_date(self):
        data_given_date = self.cleaned_data.get('given_date', None)
        print(self.instance.due_date)
        if data_given_date:
            if data_given_date < self.instance.due_date:
                raise forms.ValidationError('Given Date cannot precede Due Date.')
            elif data_given_date > date.today():
                raise forms.ValidationError('Given Date cannot be in the future.')
        return data_given_date

    class Meta:
        model = Task
        fields = ['category', 'name', 'reason', 'notes', 'due_date', 'given_date']