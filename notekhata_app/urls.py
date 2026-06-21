from django.urls import path
from .views import *

urlpatterns = [
    # Base/Home Page
    path('', home, name='home'),
    
    # Authentication URLs
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Dashboard (lists all user's boards)
    path('dashboard/', dashboard, name='dashboard'), 
    
    # Board CRUD Operations
    path('board/<int:board_id>', board_detail, name='board_detail'),
    path('board/<int:board_id>/update/', board_update, name='board_update'), 
    path('board/<int:board_id>/delete/', board_delete, name='board_delete'), 
    
    # List (Column) CRUD Operations
    path('board/<int:board_id>/list/add/', list_create, name='list_create'),
    path('list/<int:list_id>/update/', list_update, name='list_update'),
    path('list/<int:list_id>/delete/', list_delete, name='list_delete'),
    
    # Task (Card) CRUD Operations
    path('list/<int:list_id>/task/add/', task_create, name='task_create'),
    path('task/<int:task_id>/update/', task_update, name='task_update'),
    path('task/<int:task_id>/delete/', task_delete, name='task_delete'),
    path('task/<int:task_id>/complete/', task_complete, name='task_complete'),
]