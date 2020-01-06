from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.static import serve
from . import views
app_name = 'App'

urlpatterns = [
    # Login
    path('', auth_views.LoginView.as_view(), name='login'),
    # Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Home
    path('index/', views.homepage, name='homepage'),
    # Search
    path('search/', views.search_paper, name='search_paper'),
    # User Information
    path('user_information/', views.user_information, name='user_information'),
    # Paper list
    path('paper_list/', views.paper_list, name='paper_list'),
    # Paper detail
    path('<int:year>/<int:month>/<int:day>/<slug:paper>/', views.paper_detail,
         name='paper_detail'),
    # Paper Submit
    path('submit/', views.submit_paper, name='submit_paper'),
    # show
    re_path(r'^data/(?P<path>.*)$', serve, {'document_root': 'data'}),
    # download
    re_path('^download/', views.download, name='download'),
    # register
    path('register/', views.register, name='register'),
    # edit
    path('edit/', views.edit, name='edit')
]