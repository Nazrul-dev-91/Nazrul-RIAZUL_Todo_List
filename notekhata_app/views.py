from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout 
from django.contrib import messages
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
    return render(request, 'baseform.html', {'form': form, 'action': 'Register'})

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
    return render(request, 'baseform.html', {'form': form, 'action': 'Login'})

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
    lists = board.lists.all().prefetch_related('tasks')
    return render(request, 'board_detail.html', {'board': board, 'lists': lists})


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
    return render(request, 'board_form.html', {'form': form, 'board': board, 'action': 'Update'})


@login_required
def board_delete(request, board_id):
    board = get_object_or_404(Board, id=board_id, user=request.user)
    if request.method == 'POST':
        title = board.title
        board.delete()
        messages.success(request, f"Board '{title}' was deleted successfully.")
        return redirect('dashboard')
    return render(request, 'board_confirm_delete.html', {'board': board})


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
    return render(request, 'list_form.html', {'form': form, 'board': board})


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
    return render(request, 'list_form.html', {'form': form, 'board': list_obj.board, 'list': list_obj, 'action': 'Update'}) 


@login_required
def list_delete(request, list_id):
    list_obj = get_object_or_404(List, id=list_id, board__user=request.user)
    board_id = list_obj.board.id
    if request.method == 'POST':
        list_obj.delete()
        messages.success(request, "List column deleted.")
        return redirect('board_detail', board_id=board_id)
    return render(request, 'list_confirm_delete.html', {'list': list_obj}) 


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
    return render(request, 'task_form.html', {'form': form, 'list': list_obj})


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
    return render(request, 'task_form.html', {'form': form, 'task': task, 'action': 'Update'})


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, list__board__user=request.user)
    board_id = task.list.board.id
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task card removed.")
        return redirect('board_detail', board_id=board_id)
    return render(request, 'task_confirm_delete.html', {'task': task})