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
from .models import CustomUser, Doctor, Parent, Child, Task
from .forms import LoginForm, BaseSignupForm, DoctorSignupForm, ParentSignupForm, ChildSignupForm, BaseEditForm, DoctorEditForm, ParentEditForm, TaskCreateForm, TaskEditForm
import twilio
import twilio.rest
from pprint import pprint
import json

gender = {
    'M' : 'Male',
    'F' : 'Female',
    'NS' : 'Not Specified'
}

task_category = {
    'U': 'Unscheduled Check Up',
    'S' : 'Scheduled Check Up',
    'V' : 'Vaccination'
}


@require_GET
@login_required
def home(request):
    if request.user.is_superuser:
        return redirect(reverse('admin:index'))
    else:
        context = {'children': Child.objects.filter(parent_id=request.user.id)}
        if request.user.is_doctor:
            context['doctor_tasks'] = Task.objects.filter(created_by=request.user.doctor_info)
        return render(request, 'account/auth/home.html', context)

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
@require_http_methods(['GET', 'POST'])
def signup_parent(request):
    if not request.user.is_doctor:
        return redirect(reverse('home'))
    children = Child.objects.filter(parent_id=request.user.id)
    if request.method == 'GET':
        context = {'b': BaseSignupForm(prefix='b'), 'p': ParentSignupForm(prefix='p'), 'children': children}
        return render(request, 'account/auth/parent_signup.html', context)
    else:
        pprint(json.dumps(request.POST, indent=4, sort_keys=True))
        b = BaseSignupForm(request.POST, prefix='b')
        p = ParentSignupForm(request.POST, prefix='p')
        if not b.is_valid() or not p.is_valid():
            return render(request, 'account/auth/parent_signup.html', {'b': b, 'p': p,  'children': children})
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
@require_http_methods(['GET', 'POST'])
def signup_child(request):
    if not request.user.is_doctor:
        return redirect(reverse('home'))
    children = Child.objects.filter(parent_id=request.user.id)
    if request.method == 'GET':
        context = {'f': ChildSignupForm(), 'children': children}
        return render(request, 'account/auth/child_signup.html', context)
    else:
        f = ChildSignupForm(request.POST)
        if not f.is_valid():
            return render(request, 'account/auth/child_signup.html', {'f': f, 'children': children})
        else:
            child = f.save(commit=False)
            child.parent = f.valid_parent
            child.save()
            return redirect(reverse('home'))
        

def logout(request):
    auth_logout(request)
    return redirect(reverse('login'))


@login_required
@require_http_methods(['GET', 'POST'])
def edit_profile(request):
    if request.method == 'GET':
        context = {'b': BaseEditForm(instance=request.user, prefix='b')}
        if request.user.is_doctor:
            context['d'] = DoctorEditForm(instance=Doctor.objects.get(doctor_id=request.user.id), prefix='d')
        else:
            context['d'] = DoctorEditForm(prefix='d')
        if request.user.is_parent:
            context['p'] = ParentEditForm(instance=Parent.objects.get(parent_id=request.user.id), prefix='p')
            context['children'] = Child.objects.filter(parent_id=request.user.id)
        else:
            context['p'] = ParentEditForm(prefix='p')
        return render(request, 'account/auth/user_edit.html', context)
    else:
        pprint(json.dumps(request.POST, indent=4, sort_keys=True))
        b = BaseEditForm(request.POST, instance=request.user, prefix='b')
        if request.user.is_doctor:
            d = DoctorEditForm(request.POST, instance=Doctor.objects.get(doctor_id=request.user.id), prefix='d')
        else:
            if request.POST.get('doctor_checkbox'):
                d = DoctorEditForm(request.POST, prefix='d')
            else:
                d = DoctorEditForm(prefix='d')
        is_parent_form_valid = True
        if request.user.is_parent:
            p = ParentEditForm(request.POST, instance=Parent.objects.get(parent_id=request.user.id), prefix='p')
            p.is_valid()
            p.errors.pop('aadhar')                
        else:
            if request.POST.get('parent_checkbox'):
                p = ParentEditForm(request.POST, prefix='p')
                is_parent_form_valid = p.is_valid()
            else:
                p = ParentEditForm(prefix='p')
        if not b.is_valid() or not d.is_valid() or not is_parent_form_valid:
            context = {'b': b, 'd': d, 'p': p}
            if request.POST.get('doctor_checkbox'):
                context['doctor_checkbox'] = 'Yes'
            else:
                context['doctor_checkbox'] = 'No'
            if request.POST.get('parent_checkbox'):
                context['parent_checkbox'] = 'Yes'
            else:
                context['parent_checkbox'] = 'No'
            if request.user.is_parent: 
                context['children'] = Child.objects.filter(parent_id=request.user.id)
            return render(request, 'account/auth/user_edit.html', context)
        else:
            custom_user = b.save(commit=False)
            new_password = b.cleaned_data.get('new_password','')
            if new_password:
                custom_user.set_password(new_password)
            if request.POST.get('doctor_checkbox'):
                custom_user.is_doctor = True
                doctor = d.save(commit=False)
                doctor.doctor = custom_user
                doctor.save()
            if request.POST.get('parent_checkbox'):
                custom_user.is_parent = True
                parent = p.save(commit=False)
                parent.parent = custom_user
                parent.save()
            custom_user.save()
            context = {}
            return redirect(reverse('edit-profile'))
        
@require_GET
def search_child(request):
    query_term = request.GET.get('c')
    data = {'children': []}
    if not query_term:
        return JsonResponse(data)
    custom_users = CustomUser.objects.filter(Q(phone__startswith=query_term) & Q(is_parent=True))
    children = []
    for custom_user in custom_users:
        parent_children = Child.objects.filter(parent_id=custom_user.id)
        children = children + [{
                'name': parent_child.first_name + ' ' + parent_child.last_name,
                'gender': gender[parent_child.gender],
                'dob': parent_child.dob,
                'parent_name': custom_user.first_name + ' ' + custom_user.last_name,
                'parent_phone': custom_user.phone,
                'parent_aadhar': Parent.objects.get(parent=custom_user).aadhar,
                'home': reverse('home-child', kwargs={'id': parent_child.id})
            } for parent_child in parent_children
        ]
    data['children'] = children
    return JsonResponse(data)

@login_required
def home_child(request, id=None):
    child_obj = get_object_or_404(Child, id=id)
    if request.user.is_doctor or (request.user.is_parent and child_obj.parent_id == request.user.id):
        child_metadata = {}
        child_metadata['parent_name'] = child_obj.parent.parent.first_name + ' ' + child_obj.parent.parent.last_name
        child_metadata['parent_phone'] = child_obj.parent.parent.phone
        child_metadata['parent_aadhar'] = child_obj.parent.aadhar 
        child_metadata['gender'] = gender[child_obj.gender]
        tasks = [
            {
                'category': task_category[task.category],
                'name': task.name,
                'reason': task.reason,
                'notes': task.notes,
                'date_created': task.date_created,
                'due_date': task.due_date,
                'given_date': task.given_date,
                'created_by_id': task.created_by.doctor_id,
                'edit': reverse('edit-task', kwargs={'id': id, 't_id': task.id})
            } for task in Task.objects.filter(child=child_obj).order_by('due_date')
        ]
        return render(request, 'account/auth/child_home.html', {'child': child_obj, 'child_metadata': child_metadata, 'children': Child.objects.filter(parent_id=request.user.id), 'tasks': tasks})
    else:
        return redirect(reverse('home'))
    
@login_required
@require_http_methods(['GET', 'POST'])
def create_task(request, id=None):
    child_obj = get_object_or_404(Child, id=id)
    if request.user.is_doctor:
        if request.method == 'GET':
            context = {'t': TaskCreateForm(), 'child_obj': child_obj}
            return render(request, 'account/auth/task_create.html', context)
        else:
            t = TaskCreateForm(request.POST)
            if not t.is_valid():
                return render(request, 'account/auth/task_create.html', {'t': t, 'child_obj': child_obj})
            else:
                task = t.save(commit=False)
                task.created_by=request.user.doctor_info
                task.child = child_obj
                if task.category != 'U':
                    client = twilio.rest.TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    custom_user_obj = CustomUser.objects.get(id=task.created_by.doctor_id)
                    message = 'You are scheduled for the "' + task_category[task.category] + ' - ' + task.name + '" by ' + 'Dr. ' + custom_user_obj.first_name + ' ' + custom_user_obj.last_name + ' of your child ' + child_obj.first_name + ' ' + child_obj.last_name + ' at ' + task.created_by.hospital + ' on ' + task.due_date.strftime('%-d %b, %Y')
                    obj = client.messages.create(
                        body=message,
                        to='+91' + CustomUser.objects.get(id=child_obj.parent_id).phone,
                        from_=settings.TWILIO_PHONE_NUMBER
                    )
                task.save()
                return redirect(reverse('home-child', kwargs={'id': id}))
    else:
        return redirect(reverse('home-child', kwargs={'id': id}))
    
@login_required
@require_http_methods(['GET', 'POST'])
def edit_task(request, id=None, t_id=None):
    child_obj = get_object_or_404(Child, id=id)
    task_obj = get_object_or_404(Task, id=t_id)
    if request.user.id == task_obj.created_by.doctor_id:
        if request.method == 'GET':
            context = {'t': TaskEditForm(instance=task_obj), 'task': task_obj}
            return render(request, 'account/auth/task_edit.html', context)
        else:
            t = TaskEditForm(request.POST, instance=task_obj)
            if not t.is_valid():
                return render(request, 'account/auth/task_edit.html', {'t': t, 'task': task_obj})
            else:
                task = t.save(commit=False)
                task.save()
                return redirect(reverse('home-child', kwargs={'id': id}))
    else:
        return redirect(reverse('home-child', kwargs={'id': id}))

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