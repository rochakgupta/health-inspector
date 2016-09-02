from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count
from .models import CustomUser, Doctor, Parent, Child
from .forms import LoginForm, BaseSignupForm, DoctorSignupForm, ParentSignupForm, ChildSignupForm
import twilio
import twilio.rest
from pprint import pprint

@require_GET
@login_required
def home(request):
    if request.user.is_superuser:
        return redirect(reverse('admin:index'))
    else:
        return render(request, 'account/auth/home.html')

@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated():
        return redirect(reverse('home'))
    if request.method == 'GET':
        context = {'f': LoginForm()}
        return render(request, 'account/auth/login.html', context)
    else:
        f = LoginForm(request.POST)
        if not f.is_valid():
            context = {'f': f}
            return render(request, 'account/auth/login.html', context)
        else:
            user = f.authenticated_user
            auth_login(request, user)
            return redirect(reverse('home'))


def signup_doctor(request):
    if request.user.is_authenticated():
        return redirect(reverse('home'))
    if request.method == 'GET':
        context = {'b': BaseSignupForm(prefix='b'), 'd': DoctorSignupForm(prefix='d')}
        return render(request, 'account/auth/doctor_signup.html', context)
    else:
        b = BaseSignupForm(request.POST, prefix='b')
        d = DoctorSignupForm(request.POST, prefix='d')
        if not b.is_valid() or not d.is_valid():
            return render(request, 'account/auth/doctor_signup.html', {'b': b, 'd': d})
        else:
            custom_user = b.save(commit=False)
            custom_user.username = b.cleaned_data['phone']
            custom_user.set_password(b.cleaned_data['password'])
            custom_user.is_doctor = True
            custom_user.is_parent = False
            custom_user.save()
            doctor = d.save(commit=False)
            doctor.doctor = custom_user
            doctor.save()
            return redirect(reverse('home'))
        
@login_required
def signup_parent(request):
    if not request.user.is_doctor:
        return redirect(reverse('home'))
    if request.method == 'GET':
        context = {'b': BaseSignupForm(prefix='b'), 'p': ParentSignupForm(prefix='p')}
        return render(request, 'account/auth/parent_signup.html', context)
    else:
        b = BaseSignupForm(request.POST, prefix='b')
        p = ParentSignupForm(request.POST, prefix='p')
        if not b.is_valid() or not p.is_valid():
            return render(request, 'account/auth/parent_signup.html', {'b': b, 'p': p})
        else:
            custom_user = b.save(commit=False)
            custom_user.username = b.cleaned_data['phone']
            custom_user.set_password(b.cleaned_data['password'])
            custom_user.is_doctor = False
            custom_user.is_parent=True
            custom_user.save()
            parent = p.save(commit=False)
            parent.parent = custom_user
            parent.save()
            return redirect(reverse('home'))
        
@login_required
def signup_child(request):
    if not request.user.is_doctor:
        return redirect(reverse('home'))
    if request.method == 'GET':
        context = {'f': ChildSignupForm()}
        return render(request, 'account/auth/child_signup.html', context)
    else:
        f = ChildSignupForm(request.POST)
        if not f.is_valid():
            return render(request, 'account/auth/child_signup.html', {'f': f})
        else:
            child = f.save(commit=False)
            child.parent = f.valid_parent
            child.save()
            return redirect(reverse('home'))
        
def logout(request):
#    client = twilio.rest.TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#    obj = client.messages.create(
#        body='You are now logging out',
#        to='+91' + request.user.phone,
#        from_=settings.TWILIO_PHONE_NUMBER
#    )
#    pprint(obj.__dict__)
    auth_logout(request)
    return redirect(reverse('login'))

#from django.shortcuts import render, get_object_or_404, redirect
#from django.http import Http404, JsonResponse, HttpResponse
#from django.views.decorators.http import require_GET, require_POST, require_http_methods
#from django.views.decorators.csrf import csrf_exempt
#from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
#from django.core.urlresolvers import reverse
#from django.core.mail import EmailMultiAlternatives
#from django.conf import settings
#from django.contrib.auth.decorators import login_required
#from django.template import loader
#from django.core.paginator import Paginator
#from django.db.models import Q
#from django.db.models import Count
#from .models import CustomUser, Doctor, Parent, Child 
#
#@require_GET
#@login_required
#def home(request):
#    if request.user.is_doctor:
#        return redirect(reverse('home-doctor', kwargs={'id': request.user.id}))
#    else:
#        return redirect(reverse('home-parent', kwargs={'id': request.user.id}))
#    
#@require_GET
#@login_required
#def home_doctor(request, id=None):
#    return render(request, 'account/auth/home_doctor.html', Doctor.get(doctor_id=id))
#
#@require_GET
#@login_required
#def home_parent(request, id=None):
#    return render(request, 'account/auth/home_parent.html', Parent.get(parent_id=id))
#
#@require_http_methods(['GET', 'POST'])
#def login(request):
#    if request.user.is_authenticated():
#        return redirect(reverse('home'))
#    if request.method == 'GET' or (request.GET.get('type') != 'doctor' and request.GET.get('type') != 'parent'):
#        context = {'f_doctor': DoctorLoginForm(), 'f_parent': ParentLoginForm()}
#        return render(request, 'account/auth/login.html', context)
#    else:
#        if request.GET.get('type') == 'doctor':
#            f_doctor = DoctorLoginForm(request.POST)
#            if not f_doctor.is_valid():
#                context = {'f_doctor': f_doctor, 'f_parent': ParentLoginForm()}
#                return render(request, 'account/auth/login.html', context)
#            user = f_doctor.authenticated_user
#            auth_login(request, user)
#            return redirect(reverse('home-doctor', kwargs={'id': user.id}))
#        else:
#            f_parent = ParentLoginForm(request.POST)
#            if not f_parent.is_valid():
#                context = {'f_doctor': DoctorLoginForm(), 'f_parent': f_parent}
#                return render(request, 'account/auth/login.html', context)
#            user = f_parent.authenticated_user
#            auth_login(request, user)
#            return redirect(reverse('home-parent', kwargs={'id': user.id}))
#
#
#def signup_doctor(request):
#    if request.user.is_authenticated():
#        return redirect(reverse('home-doctor', kwargs={'id': request.user.id}))
#    if request.method == 'GET':
#        context = {'f': DoctorSignupForm()}
#        return render(request, 'account/auth/doctor_signup.html', context)
#    else:
#        f = DoctorSignupForm(request.POST)
#        if not f.is_valid():
#            return render(request, 'account/auth/doctor_signup.html', {'f': f})
#        else:
#            user = f.save(commit=False)
#            user.set_password(f.cleaned_data['password'])
#            user.is_active = True
#            user.save()
#            return redirect(reverse('home-doctor', kwargs={'id': user.id}))