from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
import json

from .models import Client, Project, FolderStructure, PredefinedStructure
from .serializers import (
    ClientSerializer, ClientListSerializer, ProjectSerializer, 
    ProjectListSerializer, ProjectCreateSerializer, FolderStructureSerializer,
    FolderStructureCreateSerializer, PredefinedStructureSerializer,
    StructureImportSerializer
)


class ClientListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating clients"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Client.objects.filter(created_by=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClientListSerializer
        return ClientSerializer


class ClientRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting clients"""
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Client.objects.filter(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating projects"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Project.objects.filter(created_by=self.request.user, is_active=True)
        
        # Filter by client
        client_id = self.request.query_params.get('client', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(client__name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-updated_at')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectCreateSerializer


class ProjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting projects"""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


class FolderStructureListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating folder structures"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id, created_by=self.request.user)
        return FolderStructure.objects.filter(project=project, is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FolderStructureSerializer
        return FolderStructureCreateSerializer
    
    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id, created_by=self.request.user)
        serializer.save(project=project)


class FolderStructureRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting folder structures"""
    serializer_class = FolderStructureSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id, created_by=self.request.user)
        return FolderStructure.objects.filter(project=project)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


class PredefinedStructureListAPIView(generics.ListAPIView):
    """API view for listing predefined structures"""
    serializer_class = PredefinedStructureSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = PredefinedStructure.objects.filter(
            Q(created_by=self.request.user) | Q(is_public=True),
            is_active=True
        )
        
        # Filter by structure type
        structure_type = self.request.query_params.get('type', None)
        if structure_type:
            queryset = queryset.filter(structure_type=structure_type)
        
        return queryset.order_by('structure_type', 'name')


class CreatePhysicalFoldersAPIView(APIView):
    """API view for creating physical folders"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, project_id, structure_id):
        project = get_object_or_404(Project, id=project_id, created_by=request.user)
        folder_structure = get_object_or_404(FolderStructure, id=structure_id, project=project)
        
        if folder_structure.is_created:
            return Response({
                'success': False,
                'message': 'Folders have already been created for this structure.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            import os
            
            # Create base project directory
            project_path = os.path.join(project.save_location, project.client.name, project.name)
            os.makedirs(project_path, exist_ok=True)
            
            # Create folder structure
            def create_folders_recursive(structure, current_path):
                for item in structure:
                    folder_name = item.get('name', '').strip()
                    if not folder_name:
                        continue
                        
                    folder_path = os.path.join(current_path, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    
                    # Create subfolders if they exist
                    children = item.get('children', [])
                    if children:
                        create_folders_recursive(children, folder_path)
            
            structure_data = folder_structure.get_structure_as_dict()
            create_folders_recursive(structure_data, project_path)
            
            # Update folder structure record
            folder_structure.is_created = True
            folder_structure.created_path = project_path
            folder_structure.save()
            
            return Response({
                'success': True,
                'message': f'Folders created successfully at: {project_path}',
                'created_path': project_path
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating folders: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImportStructureAPIView(APIView):
    """API view for importing structure from JSON file"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, created_by=request.user)
        serializer = StructureImportSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                uploaded_file = serializer.validated_data['structure_file']
                custom_name = serializer.validated_data.get('name')
                
                # Read and parse JSON file
                file_content = uploaded_file.read().decode('utf-8')
                import_data = json.loads(file_content)
                
                # Validate import data structure
                if 'structure' not in import_data or 'data' not in import_data['structure']:
                    return Response({
                        'success': False,
                        'message': 'Invalid JSON structure format.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                structure_data = import_data['structure']['data']
                structure_name = custom_name or import_data['structure'].get('name', 'Imported Structure')
                
                # Create new folder structure
                folder_structure = FolderStructure.objects.create(
                    project=project,
                    name=f"{structure_name} (Imported)",
                    structure_data=structure_data
                )
                
                return Response({
                    'success': True,
                    'message': f'Structure "{folder_structure.name}" imported successfully!',
                    'structure_id': folder_structure.id
                })
                
            except json.JSONDecodeError:
                return Response({
                    'success': False,
                    'message': 'Invalid JSON file format.'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Error importing structure: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_dashboard_stats(request):
    """API endpoint for dashboard statistics"""
    user = request.user
    
    stats = {
        'total_clients': user.clients.filter(is_active=True).count(),
        'total_projects': user.projects.filter(is_active=True).count(),
        'active_projects': user.projects.filter(
            is_active=True, 
            status__in=['planning', 'in_progress']
        ).count(),
        'completed_projects': user.projects.filter(
            is_active=True, 
            status='completed'
        ).count(),
    }
    
    # Recent projects
    recent_projects = user.projects.filter(is_active=True).order_by('-updated_at')[:5]
    recent_projects_data = ProjectListSerializer(recent_projects, many=True).data
    
    return Response({
        'stats': stats,
        'recent_projects': recent_projects_data
    })
