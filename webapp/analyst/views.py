from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import sys
sys.path.insert(0, "/Users/mbyrnes/docs/school/class/ current/cs490/form_d")
from edgar import single_day
from classifier import tree_predict
import datetime as dt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import UserForm, AnalystForm
from .models import FormD, Analyst
import pandas as pd


# cover page for site
def cover(request):
  return render(request, 'analyst/cover.html', {})

def about(request):
    return render(request, 'analyst/about.html', {})

def analyze(request):
    return render(request, 'analyst/analyze.html', {})

def recent(request):
    form_d_list = FormD.objects.order_by("-date_added")[:20]
    context = {
        'form_d_list': form_d_list,
    }
    return render(request, 'analyst/recent.html', context)  

def classify(request):
    form_d_list = FormD.objects.order_by("-date_added")[:20]
    predictions = []
    for form in form_d_list:
        firm = [[form.state, form.min_investment_accepted, form.total_offering_amount, form.total_amount_sold, form.total_remaining, form.ind_group_type, form.has_non_accred, form.num_non_accred, form.tot_number_investors, True, True]]
        firm = pd.DataFrame(firm)
        classification = tree_predict(firm)
        predictions.append(classification)

    form_d_list = zip(form_d_list, predictions)
    context = {
        'form_d_list': form_d_list,
    }
    return render(request, 'analyst/classify.html', context)  


def detail(request, form_id):
    form = FormD.objects.filter(cik=form_id)[0]
    context = {
        'form_id': form_id,
        'form': form,
    }

    return render(request, 'analyst/detail.html', context)

def detail_classify(request, form_id):
    form = FormD.objects.filter(cik=form_id)[0]
    # convert back to df format
    firm = [[form.state, form.min_investment_accepted, form.total_offering_amount, form.total_amount_sold, form.total_remaining, form.ind_group_type, form.has_non_accred, form.num_non_accred, form.tot_number_investors, True, True]]
    firm = pd.DataFrame(firm)
    classification = tree_predict(firm)

    context = {
        'form_id': form_id,
        'form': form,
        'classification': classification,
    }

    return render(request, 'analyst/detail.html', context)

def results(request):
    # put edgar function here
    yesterday = dt.datetime.now() - dt.timedelta(days=1)
    results = single_day(yesterday)
    results = [val["Primary Issuer"]["entity_name"] for key,val in results.iteritems() if val != {}]
    context = {
        "results": results,
    }
    return render(request, "analyst/results.html", context)

# New User Information page
def get_new_user_info(request):
  error = 0

  if request.method == 'POST':
    form = AnalystForm(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      email = form.cleaned_data['email']
    else:
      error = "Be sure to fill in all of the fields!"

    form = UserForm(request.POST)
    if form.is_valid() and error == 0:
      username = form.cleaned_data['username']
      password = form.cleaned_data['password']

      if User.objects.filter(username=username).count() != 0:
        error = "The username you selected is already in use. Please choose a new one"
      elif password != form.cleaned_data['confirm_password']:
        error = "The passwords entered do not match"
      else:
        new_user = User.objects.create_user(username, email=None, password=password, first_name=first_name, 
          last_name=last_name)
        new_user.save()
        student = Analyst.objects.create(first_name=first_name, last_name=last_name,
          email=email, user=new_user)
        student.save()
        user = authenticate(username=username, password=password)
        if user is not None:
          if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/analyst/accounts/profile')
          else:
            error = "An account for this user already exists, but it is deactivated"
        else:
          error = "There was a problem creating your account. Please try again"

    else:
      error = "Be sure to fill in all of the fields!"


  form = UserForm()
  form2 = AnalystForm()
  context = {
    'form': form,
    'form2': form2,
    'error': error,
  }
  return render(request, 'analyst/user_info.html', context)

# User Home Page
def user_home(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/analyst/login')

  student = Analyst.objects.get(user=request.user)
  context = {
    'first_name': student.first_name,
    'last_name': student.last_name,
    'email': student.email,
    'username': request.user.username,
  }
  return render(request, 'analyst/user_home_page.html', context)

# Edit Personal Info page
def edit_info(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/analyst/login')

  student = Analyst.objects.get(user=request.user)

  if request.method == 'POST':
    form = AnalystForm(request.POST)
    if form.is_valid():
      student.first_name = form.cleaned_data['first_name']
      student.last_name = form.cleaned_data['last_name']
      student.email = form.cleaned_data['email']
      student.save()
    return HttpResponseRedirect('/analyst/accounts/profile/')

  form = AnalystForm({'first_name': student.first_name, 'last_name': student.last_name,
    'email': student.email})
  context = {
    'form': form,
  }
  return render(request, 'analyst/edit_info.html', context)

