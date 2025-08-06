from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import json
import os
import zipfile
import tempfile
from .models import Client, Project, FolderStructure, PredefinedStructure


@login_required
def dashboard(request):
    """Main dashboard view"""
    user = request.user

    # Get recent projects
    recent_projects = user.projects.filter(is_active=True).order_by('-updated_at')[:5]

    # Get statistics
    stats = {
        'total_clients': user.clients.filter(is_active=True).count(),
        'total_projects': user.projects.filter(is_active=True).count(),
        'active_projects': user.projects.filter(is_active=True, status__in=['planning', 'in_progress']).count(),
        'completed_projects': user.projects.filter(is_active=True, status='completed').count(),
    }

    context = {
        'recent_projects': recent_projects,
        'stats': stats,
    }
    return render(request, 'projects/dashboard.html', context)


@login_required
def client_list(request):
    """List all clients"""
    search_query = request.GET.get('search', '')
    clients = request.user.clients.filter(is_active=True)

    if search_query:
        clients = clients.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    paginator = Paginator(clients, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'projects/client_list.html', context)


@login_required
def client_detail(request, client_id):
    """Client detail view"""
    client = get_object_or_404(Client, id=client_id, created_by=request.user)
    projects = client.projects.filter(is_active=True).order_by('-updated_at')

    context = {
        'client': client,
        'projects': projects,
    }
    return render(request, 'projects/client_detail.html', context)


@login_required
def client_create(request):
    """Create new client"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not name:
            messages.error(request, 'Client name is required.')
            return render(request, 'projects/client_form.html')

        # Check if client already exists for this user
        if Client.objects.filter(name=name, created_by=request.user).exists():
            messages.error(request, 'A client with this name already exists.')
            return render(request, 'projects/client_form.html')

        client = Client.objects.create(
            name=name,
            email=email or None,
            phone=phone or None,
            address=address or None,
            created_by=request.user
        )

        messages.success(request, f'Client "{client.name}" created successfully!')
        return redirect('client_detail', client_id=client.id)

    return render(request, 'projects/client_form.html')


@login_required
def client_edit(request, client_id):
    """Edit client"""
    client = get_object_or_404(Client, id=client_id, created_by=request.user)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not name:
            messages.error(request, 'Client name is required.')
            return render(request, 'projects/client_form.html', {'client': client})

        # Check if another client with same name exists
        existing = Client.objects.filter(name=name, created_by=request.user).exclude(id=client.id)
        if existing.exists():
            messages.error(request, 'A client with this name already exists.')
            return render(request, 'projects/client_form.html', {'client': client})

        client.name = name
        client.email = email or None
        client.phone = phone or None
        client.address = address or None
        client.save()

        messages.success(request, f'Client "{client.name}" updated successfully!')
        return redirect('client_detail', client_id=client.id)

    return render(request, 'projects/client_form.html', {'client': client})


@login_required
def project_list(request):
    """List all projects"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    client_filter = request.GET.get('client', '')

    projects = request.user.projects.filter(is_active=True)

    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(client__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if status_filter:
        projects = projects.filter(status=status_filter)

    if client_filter:
        projects = projects.filter(client_id=client_filter)

    projects = projects.order_by('-updated_at')

    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    clients = request.user.clients.filter(is_active=True).order_by('name')
    status_choices = Project.STATUS_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'client_filter': client_filter,
        'clients': clients,
        'status_choices': status_choices,
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, project_id):
    """Project detail view"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    folder_structures = project.folder_structures.filter(is_active=True).order_by('-updated_at')

    context = {
        'project': project,
        'folder_structures': folder_structures,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create(request):
    """Create new project"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        client_id = request.POST.get('client_id')
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'planning')
        save_location = request.POST.get('save_location', '').strip()

        if not name:
            messages.error(request, 'Project name is required.')
            return render(request, 'projects/project_form.html', {
                'clients': request.user.clients.filter(is_active=True)
            })

        if not client_id:
            messages.error(request, 'Please select a client.')
            return render(request, 'projects/project_form.html', {
                'clients': request.user.clients.filter(is_active=True)
            })

        try:
            client = Client.objects.get(id=client_id, created_by=request.user)
        except Client.DoesNotExist:
            messages.error(request, 'Invalid client selected.')
            return render(request, 'projects/project_form.html', {
                'clients': request.user.clients.filter(is_active=True)
            })

        # Check if project already exists for this client
        if Project.objects.filter(name=name, client=client).exists():
            messages.error(request, 'A project with this name already exists for this client.')
            return render(request, 'projects/project_form.html', {
                'clients': request.user.clients.filter(is_active=True)
            })

        project = Project.objects.create(
            name=name,
            client=client,
            description=description or None,
            status=status,
            save_location=save_location or r"\\192.168.29.136\EFX_Projects\clients",
            created_by=request.user
        )

        messages.success(request, f'Project "{project.name}" created successfully!')
        return redirect('project_detail', project_id=project.id)

    clients = request.user.clients.filter(is_active=True).order_by('name')
    return render(request, 'projects/project_form.html', {'clients': clients})


@login_required
def project_edit(request, project_id):
    """Edit project"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        client_id = request.POST.get('client_id')
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'planning')
        save_location = request.POST.get('save_location', '').strip()

        if not name:
            messages.error(request, 'Project name is required.')
            return render(request, 'projects/project_form.html', {
                'project': project,
                'clients': request.user.clients.filter(is_active=True)
            })

        if not client_id:
            messages.error(request, 'Please select a client.')
            return render(request, 'projects/project_form.html', {
                'project': project,
                'clients': request.user.clients.filter(is_active=True)
            })

        try:
            client = Client.objects.get(id=client_id, created_by=request.user)
        except Client.DoesNotExist:
            messages.error(request, 'Invalid client selected.')
            return render(request, 'projects/project_form.html', {
                'project': project,
                'clients': request.user.clients.filter(is_active=True)
            })

        # Check if another project with same name exists for this client
        existing = Project.objects.filter(name=name, client=client).exclude(id=project.id)
        if existing.exists():
            messages.error(request, 'A project with this name already exists for this client.')
            return render(request, 'projects/project_form.html', {
                'project': project,
                'clients': request.user.clients.filter(is_active=True)
            })

        project.name = name
        project.client = client
        project.description = description or None
        project.status = status
        project.save_location = save_location or r"\\192.168.29.136\EFX_Projects\clients"
        project.save()

        messages.success(request, f'Project "{project.name}" updated successfully!')
        return redirect('project_detail', project_id=project.id)

    clients = request.user.clients.filter(is_active=True).order_by('name')
    return render(request, 'projects/project_form.html', {
        'project': project,
        'clients': clients
    })


@login_required
def folder_structure_create(request, project_id):
    """Create folder structure for a project"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)

    if request.method == 'POST':
        name = request.POST.get('name', 'Main Structure').strip()
        structure_data = request.POST.get('structure_data', '[]')
        predefined_id = request.POST.get('predefined_structure')

        try:
            # Validate JSON structure
            structure_dict = json.loads(structure_data)
        except json.JSONDecodeError:
            messages.error(request, 'Invalid folder structure format.')
            return redirect('project_detail', project_id=project.id)

        predefined_structure = None
        if predefined_id:
            try:
                predefined_structure = PredefinedStructure.objects.get(
                    id=predefined_id,
                    is_active=True
                )
            except PredefinedStructure.DoesNotExist:
                pass

        folder_structure = FolderStructure.objects.create(
            project=project,
            name=name,
            structure_data=structure_dict,
            predefined_structure=predefined_structure
        )

        messages.success(request, f'Folder structure "{folder_structure.name}" created successfully!')
        return redirect('folder_structure_detail', project_id=project.id, structure_id=folder_structure.id)

    # Get predefined structures
    predefined_structures = PredefinedStructure.objects.filter(
        Q(created_by=request.user) | Q(is_public=True),
        is_active=True
    ).order_by('structure_type', 'name')

    context = {
        'project': project,
        'predefined_structures': predefined_structures,
    }
    return render(request, 'projects/folder_structure_form.html', context)


@login_required
def folder_structure_detail(request, project_id, structure_id):
    """Folder structure detail view"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    folder_structure = get_object_or_404(FolderStructure, id=structure_id, project=project)

    context = {
        'project': project,
        'folder_structure': folder_structure,
        'structure_tree': folder_structure.get_structure_as_dict(),
    }
    return render(request, 'projects/folder_structure_detail.html', context)


@login_required
def folder_structure_edit(request, project_id, structure_id):
    """Edit folder structure"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    folder_structure = get_object_or_404(FolderStructure, id=structure_id, project=project)

    if request.method == 'POST':
        name = request.POST.get('name', 'Main Structure').strip()
        structure_data = request.POST.get('structure_data', '[]')

        try:
            # Validate JSON structure
            structure_dict = json.loads(structure_data)
        except json.JSONDecodeError:
            messages.error(request, 'Invalid folder structure format.')
            return render(request, 'projects/folder_structure_form.html', {
                'project': project,
                'folder_structure': folder_structure,
            })

        folder_structure.name = name
        folder_structure.structure_data = structure_dict
        folder_structure.save()

        messages.success(request, f'Folder structure "{folder_structure.name}" updated successfully!')
        return redirect('folder_structure_detail', project_id=project.id, structure_id=folder_structure.id)

    context = {
        'project': project,
        'folder_structure': folder_structure,
    }
    return render(request, 'projects/folder_structure_form.html', context)


@login_required
@require_http_methods(["POST"])
def create_physical_folders(request, project_id, structure_id):
    """Create physical folders on the file system"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    folder_structure = get_object_or_404(FolderStructure, id=structure_id, project=project)

    if folder_structure.is_created:
        messages.warning(request, 'Folders have already been created for this structure.')
        return redirect('folder_structure_detail', project_id=project.id, structure_id=folder_structure.id)

    try:
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

        messages.success(request, f'Folders created successfully at: {project_path}')

    except Exception as e:
        messages.error(request, f'Error creating folders: {str(e)}')

    return redirect('folder_structure_detail', project_id=project.id, structure_id=folder_structure.id)


# AJAX API Views
@login_required
@csrf_exempt
def api_predefined_structures(request):
    """API endpoint to get predefined structures"""
    if request.method == 'GET':
        structure_type = request.GET.get('type', '')

        structures = PredefinedStructure.objects.filter(
            Q(created_by=request.user) | Q(is_public=True),
            is_active=True
        )

        if structure_type:
            structures = structures.filter(structure_type=structure_type)

        structures = structures.order_by('structure_type', 'name')

        data = []
        for structure in structures:
            data.append({
                'id': structure.id,
                'name': structure.name,
                'structure_type': structure.structure_type,
                'structure_type_display': structure.get_structure_type_display(),
                'structure_data': structure.get_structure_as_dict(),
                'description': structure.description or '',
            })

        return JsonResponse({'success': True, 'data': data})

    return JsonResponse({'success': False, 'message': 'Method not allowed'})


@login_required
@csrf_exempt
def api_validate_structure(request):
    """API endpoint to validate folder structure JSON"""
    if request.method == 'POST':
        try:
            structure_data = request.POST.get('structure_data', '[]')
            structure_dict = json.loads(structure_data)

            # Basic validation
            if not isinstance(structure_dict, list):
                return JsonResponse({
                    'success': False,
                    'message': 'Structure must be a list of folders'
                })

            # Validate structure format
            def validate_structure_item(item):
                if not isinstance(item, dict):
                    return False, 'Each folder must be an object'

                if 'name' not in item:
                    return False, 'Each folder must have a name'

                if not item['name'].strip():
                    return False, 'Folder names cannot be empty'

                children = item.get('children', [])
                if children and not isinstance(children, list):
                    return False, 'Children must be a list'

                for child in children:
                    is_valid, error_msg = validate_structure_item(child)
                    if not is_valid:
                        return False, error_msg

                return True, ''

            for item in structure_dict:
                is_valid, error_msg = validate_structure_item(item)
                if not is_valid:
                    return JsonResponse({'success': False, 'message': error_msg})

            return JsonResponse({'success': True, 'message': 'Structure is valid'})

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON format'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Validation error: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Method not allowed'})


@login_required
@csrf_exempt
def api_save_structure(request):
    """API endpoint to save folder structure"""
    if request.method == 'POST':
        try:
            project_id = request.POST.get('project_id')
            structure_id = request.POST.get('structure_id')
            name = request.POST.get('name', 'Main Structure').strip()
            structure_data = request.POST.get('structure_data', '[]')

            # Validate project
            project = get_object_or_404(Project, id=project_id, created_by=request.user)

            # Validate structure data
            structure_dict = json.loads(structure_data)

            if structure_id:
                # Update existing structure
                folder_structure = get_object_or_404(
                    FolderStructure,
                    id=structure_id,
                    project=project
                )
                folder_structure.name = name
                folder_structure.structure_data = structure_dict
                folder_structure.save()
                message = 'Structure updated successfully'
            else:
                # Create new structure
                folder_structure = FolderStructure.objects.create(
                    project=project,
                    name=name,
                    structure_data=structure_dict
                )
                message = 'Structure created successfully'

            return JsonResponse({
                'success': True,
                'message': message,
                'structure_id': folder_structure.id
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON format'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error saving structure: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Method not allowed'})


@login_required
def download_structure_zip(request, project_id, structure_id):
    """Download folder structure as ZIP file"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    folder_structure = get_object_or_404(FolderStructure, id=structure_id, project=project)

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the project structure in temp directory
        project_path = os.path.join(temp_dir, f"{project.client.name}_{project.name}")
        os.makedirs(project_path, exist_ok=True)

        def create_folders_recursive(structure, current_path):
            for item in structure:
                folder_name = item.get('name', '').strip()
                if not folder_name:
                    continue

                folder_path = os.path.join(current_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)

                # Create a placeholder file in each folder
                placeholder_file = os.path.join(folder_path, '.gitkeep')
                with open(placeholder_file, 'w') as f:
                    f.write('# This file keeps the folder in version control\n')

                # Create subfolders if they exist
                children = item.get('children', [])
                if children:
                    create_folders_recursive(children, folder_path)

        structure_data = folder_structure.get_structure_as_dict()
        create_folders_recursive(structure_data, project_path)

        # Create ZIP file
        zip_filename = f"{project.client.name}_{project.name}_structure.zip"
        zip_path = os.path.join(temp_dir, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        # Read ZIP file and return as response
        with open(zip_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
            return response


@login_required
def export_structure_json(request, project_id, structure_id):
    """Export folder structure as JSON file"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    folder_structure = get_object_or_404(FolderStructure, id=structure_id, project=project)

    # Prepare export data
    export_data = {
        'project': {
            'name': project.name,
            'client': project.client.name,
            'description': project.description,
            'status': project.status,
        },
        'structure': {
            'name': folder_structure.name,
            'created_at': folder_structure.created_at.isoformat(),
            'updated_at': folder_structure.updated_at.isoformat(),
            'data': folder_structure.get_structure_as_dict(),
        },
        'export_info': {
            'exported_by': request.user.username,
            'exported_at': json.dumps(timezone.now(), default=str),
            'version': '1.0',
        }
    }

    # Create JSON response
    json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
    filename = f"{project.client.name}_{project.name}_structure.json"

    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def import_structure_json(request, project_id):
    """Import folder structure from JSON file"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)

    if request.method == 'POST':
        if 'structure_file' not in request.FILES:
            messages.error(request, 'Please select a JSON file to import.')
            return redirect('project_detail', project_id=project.id)

        uploaded_file = request.FILES['structure_file']

        if not uploaded_file.name.endswith('.json'):
            messages.error(request, 'Please upload a valid JSON file.')
            return redirect('project_detail', project_id=project.id)

        try:
            # Read and parse JSON file
            file_content = uploaded_file.read().decode('utf-8')
            import_data = json.loads(file_content)

            # Validate import data structure
            if 'structure' not in import_data or 'data' not in import_data['structure']:
                messages.error(request, 'Invalid JSON structure format.')
                return redirect('project_detail', project_id=project.id)

            structure_data = import_data['structure']['data']
            structure_name = import_data['structure'].get('name', 'Imported Structure')

            # Create new folder structure
            folder_structure = FolderStructure.objects.create(
                project=project,
                name=f"{structure_name} (Imported)",
                structure_data=structure_data
            )

            messages.success(request, f'Structure "{folder_structure.name}" imported successfully!')
            return redirect('folder_structure_detail', project_id=project.id, structure_id=folder_structure.id)

        except json.JSONDecodeError:
            messages.error(request, 'Invalid JSON file format.')
        except Exception as e:
            messages.error(request, f'Error importing structure: {str(e)}')

        return redirect('project_detail', project_id=project.id)

    return render(request, 'projects/import_structure.html', {'project': project})


@login_required
def duplicate_structure(request, project_id, structure_id):
    """Duplicate an existing folder structure"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    original_structure = get_object_or_404(FolderStructure, id=structure_id, project=project)

    # Create duplicate
    duplicate_structure = FolderStructure.objects.create(
        project=project,
        name=f"{original_structure.name} (Copy)",
        structure_data=original_structure.structure_data,
        predefined_structure=original_structure.predefined_structure
    )

    messages.success(request, f'Structure duplicated as "{duplicate_structure.name}"!')
    return redirect('folder_structure_detail', project_id=project.id, structure_id=duplicate_structure.id)
