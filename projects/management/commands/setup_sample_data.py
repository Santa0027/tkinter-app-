from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from projects.models import Client, Project, FolderStructure, PredefinedStructure


class Command(BaseCommand):
    help = 'Set up sample data for demonstration'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create sample clients
        sample_clients = [
            {
                'name': 'Acme Corporation',
                'email': 'contact@acme.com',
                'phone': '+1-555-0123',
                'address': '123 Business St, Corporate City, CC 12345'
            },
            {
                'name': 'Creative Studios',
                'email': 'hello@creativestudios.com',
                'phone': '+1-555-0456',
                'address': '456 Design Ave, Art District, AD 67890'
            },
            {
                'name': 'Tech Innovations',
                'email': 'info@techinnovations.com',
                'phone': '+1-555-0789',
                'address': '789 Innovation Blvd, Tech Valley, TV 13579'
            }
        ]

        created_clients = []
        for client_data in sample_clients:
            client, created = Client.objects.get_or_create(
                name=client_data['name'],
                created_by=admin_user,
                defaults=client_data
            )
            created_clients.append(client)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created client: {client.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Client already exists: {client.name}'))

        # Create sample projects
        sample_projects = [
            {
                'name': 'Brand Identity Package',
                'client': created_clients[0],
                'description': 'Complete brand identity design including logo, business cards, and marketing materials',
                'status': 'in_progress'
            },
            {
                'name': 'Product Launch Video',
                'client': created_clients[0],
                'description': 'Motion graphics video for new product launch campaign',
                'status': 'planning'
            },
            {
                'name': 'Website Redesign',
                'client': created_clients[1],
                'description': 'Modern responsive website redesign with improved UX',
                'status': 'in_progress'
            },
            {
                'name': 'Social Media Campaign',
                'client': created_clients[1],
                'description': 'Visual assets for 3-month social media campaign',
                'status': 'completed'
            },
            {
                'name': 'Mobile App UI Design',
                'client': created_clients[2],
                'description': 'User interface design for iOS and Android mobile application',
                'status': 'planning'
            }
        ]

        created_projects = []
        for project_data in sample_projects:
            project, created = Project.objects.get_or_create(
                name=project_data['name'],
                client=project_data['client'],
                defaults={
                    'description': project_data['description'],
                    'status': project_data['status'],
                    'created_by': admin_user
                }
            )
            created_projects.append(project)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created project: {project.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Project already exists: {project.name}'))

        # Create sample folder structures using predefined templates
        predefined_structures = PredefinedStructure.objects.filter(is_public=True, is_active=True)
        
        if predefined_structures.exists():
            # Brand Identity - Graphic Design structure
            if created_projects[0]:
                graphic_template = predefined_structures.filter(structure_type='graphic_design').first()
                if graphic_template:
                    structure, created = FolderStructure.objects.get_or_create(
                        project=created_projects[0],
                        name='Brand Identity Structure',
                        defaults={
                            'structure_data': graphic_template.structure_data,
                            'predefined_structure': graphic_template
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created folder structure for: {created_projects[0].name}'))

            # Product Launch Video - Motion Graphics structure
            if created_projects[1]:
                motion_template = predefined_structures.filter(structure_type='motion_graphics').first()
                if motion_template:
                    structure, created = FolderStructure.objects.get_or_create(
                        project=created_projects[1],
                        name='Video Production Structure',
                        defaults={
                            'structure_data': motion_template.structure_data,
                            'predefined_structure': motion_template
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created folder structure for: {created_projects[1].name}'))

            # Website Redesign - Web Development structure
            if created_projects[2]:
                web_template = predefined_structures.filter(structure_type='web_development').first()
                if web_template:
                    structure, created = FolderStructure.objects.get_or_create(
                        project=created_projects[2],
                        name='Website Development Structure',
                        defaults={
                            'structure_data': web_template.structure_data,
                            'predefined_structure': web_template
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created folder structure for: {created_projects[2].name}'))

        # Create a demo user
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )
        
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user (demo/demo123)'))

            # Create a client for demo user
            demo_client, created = Client.objects.get_or_create(
                name='Demo Client',
                created_by=demo_user,
                defaults={
                    'email': 'demo.client@example.com',
                    'phone': '+1-555-DEMO',
                    'address': 'Demo Address'
                }
            )

            if created:
                # Create a demo project
                demo_project, created = Project.objects.get_or_create(
                    name='Demo Project',
                    client=demo_client,
                    defaults={
                        'description': 'This is a demo project to showcase the application features',
                        'status': 'planning',
                        'created_by': demo_user
                    }
                )

                if created and predefined_structures.exists():
                    # Add a folder structure to demo project
                    demo_template = predefined_structures.first()
                    FolderStructure.objects.get_or_create(
                        project=demo_project,
                        name='Demo Structure',
                        defaults={
                            'structure_data': demo_template.structure_data,
                            'predefined_structure': demo_template
                        }
                    )

        self.stdout.write(
            self.style.SUCCESS(
                '\n' + '='*50 + '\n'
                'Sample data setup complete!\n'
                '='*50 + '\n'
                'Admin User: admin / admin123\n'
                'Demo User: demo / demo123\n'
                f'Created {len(created_clients)} clients\n'
                f'Created {len(created_projects)} projects\n'
                'Folder structures created with predefined templates\n'
                '='*50
            )
        )
