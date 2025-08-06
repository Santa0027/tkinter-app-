from django.contrib import admin
from .models import Client, Project, FolderStructure, PredefinedStructure


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_by', 'project_count', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'project_count']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('System Information', {
            'fields': ('created_by', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PredefinedStructure)
class PredefinedStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'structure_type', 'created_by', 'is_public', 'is_active', 'created_at']
    list_filter = ['structure_type', 'is_public', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'structure_type', 'description')
        }),
        ('Structure Data', {
            'fields': ('structure_data',)
        }),
        ('Settings', {
            'fields': ('is_public', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'status', 'created_by', 'folder_structure_count', 'created_at', 'is_active']
    list_filter = ['status', 'is_active', 'created_at', 'client']
    search_fields = ['name', 'client__name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'folder_structure_count', 'full_project_path']
    autocomplete_fields = ['client']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'client', 'description', 'status')
        }),
        ('Project Details', {
            'fields': ('start_date', 'end_date', 'budget', 'save_location', 'full_project_path')
        }),
        ('System Information', {
            'fields': ('created_by', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FolderStructure)
class FolderStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'predefined_structure', 'is_created', 'is_active', 'updated_at']
    list_filter = ['is_created', 'is_active', 'updated_at', 'predefined_structure']
    search_fields = ['name', 'project__name', 'project__client__name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['project', 'predefined_structure']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'project', 'predefined_structure')
        }),
        ('Structure Data', {
            'fields': ('structure_data',)
        }),
        ('Creation Status', {
            'fields': ('is_created', 'created_path')
        }),
        ('System Information', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
