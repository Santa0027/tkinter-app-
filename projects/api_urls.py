from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard API
    path('dashboard/stats/', api_views.api_dashboard_stats, name='api_dashboard_stats'),
    
    # Client API endpoints
    path('clients/', api_views.ClientListCreateAPIView.as_view(), name='api_client_list_create'),
    path('clients/<int:pk>/', api_views.ClientRetrieveUpdateDestroyAPIView.as_view(), name='api_client_detail'),
    
    # Project API endpoints
    path('projects/', api_views.ProjectListCreateAPIView.as_view(), name='api_project_list_create'),
    path('projects/<int:pk>/', api_views.ProjectRetrieveUpdateDestroyAPIView.as_view(), name='api_project_detail'),
    
    # Folder Structure API endpoints
    path('projects/<int:project_id>/structures/', 
         api_views.FolderStructureListCreateAPIView.as_view(), 
         name='api_folder_structure_list_create'),
    path('projects/<int:project_id>/structures/<int:pk>/', 
         api_views.FolderStructureRetrieveUpdateDestroyAPIView.as_view(), 
         name='api_folder_structure_detail'),
    
    # Predefined Structures API
    path('predefined-structures/', 
         api_views.PredefinedStructureListAPIView.as_view(), 
         name='api_predefined_structure_list'),
    
    # Folder Operations API
    path('projects/<int:project_id>/structures/<int:structure_id>/create-folders/', 
         api_views.CreatePhysicalFoldersAPIView.as_view(), 
         name='api_create_physical_folders'),
    path('projects/<int:project_id>/import-structure/', 
         api_views.ImportStructureAPIView.as_view(), 
         name='api_import_structure'),
]
