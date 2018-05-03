from django.conf.urls import url
from django.contrib.auth.views import login, logout, password_change, password_change_done
from .forms import UserForm
from . import views

urlpatterns = [
    url(r'^$', views.cover, name='cover'),
    url(r'^about/', views.about, name="about"),
    url(r'^home/', views.analyze, name="analyze"),

    url(r'^(?P<form_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<form_id>[0-9]+)/classify/$', views.detail_classify, name='detail'),
    # ex: /polls/5/results/
    url(r'^results/$', views.results, name='results'),
    url(r'^recent/$', views.recent, name='results'),
    url(r'^classify/$', views.classify, name='classify'),
    # ex: /polls/5/vote/

    # Login 
    url(r'^login/$', login,
        {'template_name': 'registration/login.html', 'extra_context': 
        {'next':'/analyst/accounts/profile'}}, name='login'),
    # Logout
    url(r'^logout/$', logout,
        {'template_name': 'registration/logout.html', 'extra_context': {}}, name='logout'),
    # Password change page
    url(r'^password_change/$', password_change,
        {'template_name': 'registration/password_change.html',
        'post_change_redirect': 'analyst:password_change_done', 'extra_context': {}},
        name='password_change'),
    url(r'^password_change/done/$', password_change_done,
        {'template_name': 'registration/password_change_done.html', 'extra_context': {}},
        name='password_change_done'),
    
    url(r'^new_user_info/$', views.get_new_user_info, name='new_user_info'),
    # User Home/Profile
    url(r'^accounts/profile/$', views.user_home, name='user_home_page'),
    # Edit Personal Info
    url(r'^accounts/edit_info/$', views.edit_info, name="edit_info"),
]