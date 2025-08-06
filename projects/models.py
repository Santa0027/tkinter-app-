from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
import json


class Client(models.Model):
    """Model to store client information"""
    name = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        help_text="Client name (minimum 2 characters)"
    )
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'created_by']

    def __str__(self):
        return self.name

    @property
    def project_count(self):
        return self.projects.filter(is_active=True).count()


class PredefinedStructure(models.Model):
    """Model to store predefined folder structures"""
    STRUCTURE_TYPES = [
        ('motion_graphics', 'Motion Graphics'),
        ('graphic_design', 'Graphic Design (Poster/Flyer)'),
        ('web_development', 'Web Development'),
        ('video_editing', 'Video Editing'),
        ('photography', 'Photography'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    structure_type = models.CharField(max_length=20, choices=STRUCTURE_TYPES)
    structure_data = models.JSONField(
        help_text="JSON representation of the folder structure"
    )
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predefined_structures')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False, help_text="Make this structure available to all users")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['structure_type', 'name']
        unique_together = ['name', 'created_by']

    def __str__(self):
        return f"{self.get_structure_type_display()} - {self.name}"

    def get_structure_as_dict(self):
        """Return structure data as Python dict"""
        if isinstance(self.structure_data, str):
            return json.loads(self.structure_data)
        return self.structure_data


class Project(models.Model):
    """Model to store project information"""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        help_text="Project name (minimum 2 characters)"
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    save_location = models.CharField(
        max_length=500,
        default=r"\\192.168.29.136\EFX_Projects\clients",
        help_text="Base directory where project folders will be created"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Project metadata
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['name', 'client']

    def __str__(self):
        return f"{self.client.name} - {self.name}"

    @property
    def full_project_path(self):
        """Return the full path where project will be created"""
        return f"{self.save_location}/{self.client.name}/{self.name}"

    @property
    def folder_structure_count(self):
        return self.folder_structures.filter(is_active=True).count()


class FolderStructure(models.Model):
    """Model to store folder structure for each project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='folder_structures')
    name = models.CharField(max_length=100, default="Main Structure")
    structure_data = models.JSONField(
        help_text="JSON representation of the folder structure"
    )
    predefined_structure = models.ForeignKey(
        PredefinedStructure,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Reference to predefined structure if used"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_created = models.BooleanField(default=False, help_text="Whether folders have been physically created")
    created_path = models.CharField(max_length=500, blank=True, null=True, help_text="Actual path where folders were created")

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.project} - {self.name}"

    def get_structure_as_dict(self):
        """Return structure data as Python dict"""
        if isinstance(self.structure_data, str):
            return json.loads(self.structure_data)
        return self.structure_data

    def save(self, *args, **kwargs):
        """Override save to ensure structure_data is properly formatted"""
        if isinstance(self.structure_data, str):
            try:
                self.structure_data = json.loads(self.structure_data)
            except json.JSONDecodeError:
                pass
        super().save(*args, **kwargs)
