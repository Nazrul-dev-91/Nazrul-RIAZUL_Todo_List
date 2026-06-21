from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout 
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import Board, List, Task
from .forms import RegisterForm, BoardForm, ListForm, TaskForm
from django.contrib.auth.forms import AuthenticationForm

def home(request):
    return render(request, "base.html")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user) 
            messages.success(request, "Registration successful!")
            return redirect('login')
    else:
        form = RegisterForm()
    
    context = {
        'form': form,
        'title': 'User Registration',
        'action_button_text': 'Register Dashboard',
        'cancel_url': reverse('home'),
        'auth_flow': 'register',
    }
    return render(request, 'baseform.html', context)

def login_view(request): 
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
        
    context = {
        'form': form,
        'title': 'Secure Account Login',
        'action_button_text': 'Sign In',
        'cancel_url': reverse('home'),
        'auth_flow': 'login',
    }
    return render(request, 'baseform.html', context)

def logout_view(request): 
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login') 


@login_required
def dashboard(request):
    boards = Board.objects.filter(user=request.user)
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.user = request.user
            board.save()
            messages.success(request, f"Board '{board.title}' created successfully!")
            return redirect('dashboard')
    else:
        form = BoardForm()
    return render(request, 'dashboard.html', {'boards': boards, 'form': form})


@login_required
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id, user=request.user)
    lists = board.lists.prefetch_related('tasks').all()
    all_tasks = Task.objects.filter(list__board=board)
    
    return render(request, 'board_detail.html', {
        'board': board,
        'lists': lists,
        'all_tasks': all_tasks
    })

@login_required
def board_update(request, board_id):
    board = get_object_or_404(Board, id=board_id, user=request.user)
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            messages.success(request, f"Board updated to '{board.title}'.")
            return redirect('board_detail', board_id=board.id)
    else:
        form = BoardForm(instance=board)
        
    context = {
        'form': form,
        'title': 'Edit Board Title',
        'action_button_text': 'Save Changes',
        'cancel_url': reverse('board_detail', args=[board.id]),
    }
    return render(request, 'baseform.html', context)


@login_required
def board_delete(request, board_id):
    board = get_object_or_404(Board, id=board_id, user=request.user)
    if request.method == 'POST':
        title = board.title
        board.delete()
        messages.success(request, f"Board '{title}' was deleted successfully.")
        return redirect('dashboard')
        
    context = {
        'title': 'Delete Board?',
        'warning_message': f'Are you sure you want to delete the board <strong>"{board.title}"</strong>?<br>This action will permanently remove the board and all lists/tasks associated with it.',
        'delete_btn_text': 'Yes, Delete Board',
        'cancel_url': reverse('dashboard'),
    }
    return render(request, 'baseformdelete.html', context)


@login_required
def list_create(request, board_id):
    board = get_object_or_404(Board, id=board_id, user=request.user)
    if request.method == 'POST':
        form = ListForm(request.POST)
        if form.is_valid():
            new_list = form.save(commit=False)
            new_list.board = board
            new_list.position = board.lists.count()
            new_list.save()
            messages.success(request, f"List column '{new_list.title}' added.")
            return redirect('board_detail', board_id=board.id)
    else:
        form = ListForm()
        
    context = {
        'form': form,
        'title': 'Create New List Column',
        'action_button_text': 'Add List',
        'cancel_url': reverse('board_detail', args=[board.id]),
    }
    return render(request, 'baseform.html', context)


@login_required
def list_update(request, list_id):
    list_obj = get_object_or_404(List, id=list_id, board__user=request.user)
    if request.method == 'POST':
        form = ListForm(request.POST, instance=list_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"List renamed to '{list_obj.title}'.")
            return redirect('board_detail', board_id=list_obj.board.id) 
    else:
        form = ListForm(instance=list_obj)
        
    context = {
        'form': form,
        'title': 'Rename List Column',
        'action_button_text': 'Apply Changes',
        'cancel_url': reverse('board_detail', args=[list_obj.board.id]),
    }
    return render(request, 'baseform.html', context) 


@login_required
def list_delete(request, list_id):
    list_obj = get_object_or_404(List, id=list_id, board__user=request.user)
    board_id = list_obj.board.id
    if request.method == 'POST':
        list_obj.delete()
        messages.success(request, "List column deleted.")
        return redirect('board_detail', board_id=board_id)
        
    context = {
        'title': 'Remove List Column?',
        'warning_message': f'Are you sure you want to delete the list column <strong>"{list_obj.title}"</strong>?<br>This will also permanently delete all task cards inside it.',
        'delete_btn_text': 'Delete List',
        'cancel_url': reverse('board_detail', args=[board_id]),
    }
    return render(request, 'baseformdelete.html', context) 


@login_required
def task_create(request, list_id):
    list_obj = get_object_or_404(List, id=list_id, board__user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.list = list_obj
            task.position = list_obj.tasks.count()
            task.save()
            messages.success(request, f"Task '{task.title}' created.")
            return redirect('board_detail', board_id=list_obj.board.id)
    else:
        form = TaskForm()
        
    context = {
        'form': form,
        'title': 'Create Task Card',
        'action_button_text': 'Create Task',
        'cancel_url': reverse('board_detail', args=[list_obj.board.id]),
    }
    return render(request, 'baseform.html', context)


@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id, list__board__user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f"Task '{task.title}' modified.")
            return redirect('board_detail', board_id=task.list.board.id)
    else:
        form = TaskForm(instance=task)
        
    context = {
        'form': form,
        'title': 'Edit Task Details',
        'action_button_text': 'Update Task',
        'cancel_url': reverse('board_detail', args=[task.list.board.id]),
    }
    return render(request, 'baseform.html', context)


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, list__board__user=request.user)
    board_id = task.list.board.id
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task card removed.")
        return redirect('board_detail', board_id=board_id)
        
    context = {
        'title': 'Remove Task Card?',
        'warning_message': f'Are you sure you want to delete the task card <strong>"{task.title}"</strong>?<br>Your changes will be lost permanently.',
        'delete_btn_text': 'Remove Card',
        'cancel_url': reverse('board_detail', args=[board_id]),
    }
    return render(request, 'baseformdelete.html', context)

@login_required
def task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id, list__board__user=request.user)
    task.is_completed = True
    task.save()
    messages.success(request, f"Task '{task.title}' marked as completed.")
    return redirect('board_detail', board_id=task.list.board.id)