from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Client URLs
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    path('clients/<int:client_id>/edit/', views.client_edit, name='client_edit'),
    
    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    
    # Folder Structure URLs
    path('projects/<int:project_id>/structure/', views.folder_structure_create, name='folder_structure_create'),
    path('projects/<int:project_id>/structure/<int:structure_id>/', views.folder_structure_detail, name='folder_structure_detail'),
    path('projects/<int:project_id>/structure/<int:structure_id>/edit/', views.folder_structure_edit, name='folder_structure_edit'),
    path('projects/<int:project_id>/structure/<int:structure_id>/create-folders/', views.create_physical_folders, name='create_physical_folders'),
    path('projects/<int:project_id>/structure/<int:structure_id>/download-zip/', views.download_structure_zip, name='download_structure_zip'),
    path('projects/<int:project_id>/structure/<int:structure_id>/export-json/', views.export_structure_json, name='export_structure_json'),
    path('projects/<int:project_id>/structure/<int:structure_id>/duplicate/', views.duplicate_structure, name='duplicate_structure'),
    path('projects/<int:project_id>/import-structure/', views.import_structure_json, name='import_structure_json'),

    # API URLs
    path('api/predefined-structures/', views.api_predefined_structures, name='api_predefined_structures'),
    path('api/validate-structure/', views.api_validate_structure, name='api_validate_structure'),
    path('api/save-structure/', views.api_save_structure, name='api_save_structure'),
]
