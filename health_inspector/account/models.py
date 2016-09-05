import re
import operator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date, datetime

# Create your models here.

GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('NS', '--'))

CATEGORY_CHOICES = (('V', 'Vaccination'),('U', 'Unscheduled Check Up'), ('S', 'Scheduled Check Up'))

#STATE_CHOICE = sorted((('KA', 'Karnataka'), ('AP', 'Andhra Pradesh'), ('KL', 'Kerala'), ('TN', 'Tamil Nadu'), ('MH', 'Maharashtra'), ('UP', 'Uttar Pradesh'), ('GA', 'Goa'), ('GJ', 'Gujarat'), ('RJ', 'Rajasthan'), ('HP', 'Himachal Pradesh'), ('JK', 'Jammu and Kashmir'), ('TG', 'Telangana'), ('AR', 'Arunachal Pradesh'), ('AS', 'Assam'), ('BR', 'Bihar'), ('CG', 'Chattisgarh'), ('HR', 'Haryana'), ('JH', 'Jharkhand'), ('MP', 'Madhya Pradesh'), ('MN', 'Manipur'), ('ML', 'Meghalaya'), ('MZ', 'Mizoram'), ('NL', 'Nagaland'), ('OR', 'Orissa'), ('PB', 'Punjab'), ('SK', 'Sikkim'), ('TR', 'Tripura'), ('UA', 'Uttarakhand'), ('WB', 'West Bengal'), ('AN', 'Andaman and Nicobar'), ('CH', 'Chandigarh'), ('DN', 'Dadra and Nagar Haveli'), ('DD', 'Daman and Diu'), ('DL', 'Delhi'), ('LD', 'Lakshadweep'), ('PY', 'Pondicherry')), key=operator.itemgetter(1))

def phone_validator(val):
    if not re.match('^[789]\d{9}$', val):
        raise ValidationError('Should be a 10 digit valid phone number')
        
def aadhar_validator(val):
    if not re.match('^\d{16}$', val):
        raise ValidationError('Should be a 16 digit valid aadhar number')
        
def zipcode_validator(val):
    if not re.match('^[1-9][0-9]{5}$', val):
        raise ValidationError('Should be a valid Zip Code')

class CustomUser(AbstractUser):
    phone = models.CharField(unique=True, max_length=10,validators=[phone_validator])
    is_doctor = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default=GENDER_CHOICES[2][0])
    street = models.CharField(max_length=128, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.CharField(max_length=6, null=True, blank=True, validators=[zipcode_validator])
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username', 'email']
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
    class Meta:
        verbose_name = 'User'
        
class Doctor(models.Model):
    doctor = models.OneToOneField(CustomUser, primary_key = True, on_delete=models.CASCADE, related_name="doctor_info")
    hospital = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Doctor'
        
class Parent(models.Model):
    parent = models.OneToOneField(CustomUser, primary_key = True, on_delete=models.CASCADE, related_name="parent_info")
    aadhar = models.CharField(unique=True, max_length=16,validators=[aadhar_validator])

    class Meta:
        verbose_name = 'Parent'
        
class Child(models.Model):
    dob = models.DateField(null=False, blank=False)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default=GENDER_CHOICES[2][0])
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="children")
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        verbose_name = 'Child'
        verbose_name_plural = 'Children'

class Vaccine(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    base = models.DurationField(null=False, blank=False)
    delta = models.DurationField(null=False, blank=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ('name',)
        verbose_name = 'Vaccine'
    
    
class Task(models.Model):
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES[0][0])
    name = models.CharField(max_length=128)
    reason = models.CharField(max_length=128, null=True, blank=True)
    date_created = models.DateField(null=False, blank=False, auto_now_add=True)
    due_date = models.DateField(null=False, blank=False)
    given_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=128, null=True, blank=True)
    created_by = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="tasks_created")
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="tasks")
    
    def __str__(self):
        return self.category + ' - ' + self.name + ', ' + self.reason

    class Meta:
        verbose_name = 'Task'


#from django.db import models
#from django.contrib.auth.models import AbstractUser
#from django.core.validators import RegexValidator
#
## Create your models here.
#
#class CustomUser(AbstractUser):
#    is_doctor = models.BooleanField(default=False)
#    phone = models.CharField(max_length=10,validators=[RegexValidator(regex=r'^\d{10}$', message='Should be a 10 digit number not starting with 0', code='invalid_phone_number')])
#    class Meta:
#        unique_together = ('is_doctor', 'phone')
#        verbose_name = 'CustomUser'
#        
#GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('NS', '--'))
#        
#class Doctor(models.Model):
#    first_name = models.CharField(max_length=30)
#    last_name = models.CharField(max_length=30)
#    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default=GENDER_CHOICES[2][0])
#    email = models.CharField(max_length=254, null=True, blank=True)
#    hospital = models.CharField(max_length=128, null=True, blank=True)
#    doctor = models.OneToOneField(CustomUser, primary_key = True, on_delete=models.CASCADE, related_name="doctor")
#    
#    def __str__(self):
#        return self.first_name + ' ' + self.last_name
#
#    class Meta:
#        verbose_name = 'Doctor'
#        
#class Parent(models.Model):
#    first_name = models.CharField(max_length=30)
#    last_name = models.CharField(null=True, blank=False, max_length=30)
#    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default=GENDER_CHOICES[2][0])
#    parent = models.OneToOneField(CustomUser, primary_key = True, on_delete=models.CASCADE, related_name="parent")
#    aadhar = models.CharField(unique=True, max_length=16,validators=[RegexValidator(regex=r'^\d{16}$', message='Should be a 16 digit number', code='invalid_aadhar_number')])
#    
#    def __str__(self):
#        return self.first_name + ' ' + self.last_name
#
#    class Meta:
#        verbose_name = 'Parent'
#        
#class Child(models.Model):
#    dob = models.DateField(null=False, blank=False)
#    first_name = models.CharField(max_length=30, null=True, blank=True)
#    last_name = models.CharField(max_length=30, null=True, blank=True)
#    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default=GENDER_CHOICES[2][0])
#    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="children")
#    id = models.IntegerField(primary_key=True)
#
#    class Meta:
#        verbose_name = 'Child'
#        verbose_name_plural = 'Children'