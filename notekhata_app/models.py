from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    display_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Board(models.Model):
    """
    Represents a single Trello board.
    Crucial: Strongly linked to a Django User to guarantee database-level isolation.
    """
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='boards',
        help_text="The owner of this board. Ensures data isolation between users."
    )
    title = models.CharField(max_length=150, help_text="Title of the board.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Board"
        verbose_name_plural = "Boards"

    def __str__(self):
        return f"{self.title} (Owned by {self.user.username})"


class List(models.Model):
    """
    Represents a column list inside a board (e.g., 'To Do', 'In Progress', 'Done').
    """
    board = models.ForeignKey(
        Board, 
        on_delete=models.CASCADE, 
        related_name='lists',
        help_text="The board this list belongs to."
    )
    title = models.CharField(max_length=150)
    position = models.PositiveIntegerField(
        default=0, 
        help_text="Ordering position index of this column on the board."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position', 'created_at']
        verbose_name = "List"
        verbose_name_plural = "Lists"

    def __str__(self):
        return f"{self.title} on '{self.board.title}'"


class Task(models.Model):
    """
    Represents a specific Card or Task inside a list.
    """
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    list = models.ForeignKey(
        List, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        help_text="The list column this task cards resides in."
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Detailed objective of the task.")
    due_date = models.DateField(blank=True, null=True, help_text="Optional deadline for the task.")
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='MEDIUM',
        help_text="Task urgency level."
    )
    position = models.PositiveIntegerField(
        default=0, 
        help_text="Vertical position sorting order of this card in its list column."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

# models.py এর Board ক্লাসের ভেতর এটি যুক্ত করো:
@property
def total_tasks_count(self):
    return Task.objects.filter(list__board=self).count()