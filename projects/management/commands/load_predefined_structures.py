from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from projects.models import PredefinedStructure


class Command(BaseCommand):
    help = 'Load predefined folder structures'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Motion Graphics structure
        motion_graphics_structure = [
            {
                "name": "audio",
                "children": []
            },
            {
                "name": "out_images",
                "children": [
                    {"name": "afterEffects", "children": []},
                    {"name": "photoshop", "children": []},
                    {"name": "premierePro", "children": []}
                ]
            },
            {
                "name": "out_movies",
                "children": [
                    {"name": "afterEffects", "children": []},
                    {"name": "photoshop", "children": []},
                    {"name": "premierePro", "children": []}
                ]
            },
            {
                "name": "reference",
                "children": [
                    {"name": "images", "children": []},
                    {"name": "videos", "children": []},
                    {"name": "template_files", "children": []}
                ]
            },
            {
                "name": "work_file",
                "children": [
                    {"name": "afterEffects", "children": []},
                    {"name": "photoshop", "children": []},
                    {"name": "premierePro", "children": []}
                ]
            },
            {
                "name": "client_Out",
                "children": []
            },
            {
                "name": "script",
                "children": []
            }
        ]

        # Graphic Design structure
        graphic_design_structure = [
            {
                "name": "out_images",
                "children": [
                    {"name": "photoshop", "children": []},
                    {"name": "Illustrator", "children": []},
                    {"name": "CorelDraw", "children": []}
                ]
            },
            {
                "name": "reference",
                "children": [
                    {"name": "images", "children": []},
                    {"name": "template_files", "children": []}
                ]
            },
            {
                "name": "work_file",
                "children": [
                    {"name": "photoshop", "children": []},
                    {"name": "Illustrator", "children": []},
                    {"name": "CorelDraw", "children": []}
                ]
            },
            {
                "name": "client_Out",
                "children": []
            }
        ]

        # Web Development structure
        web_development_structure = [
            {
                "name": "src",
                "children": [
                    {"name": "components", "children": []},
                    {"name": "pages", "children": []},
                    {"name": "styles", "children": []},
                    {"name": "assets", "children": [
                        {"name": "images", "children": []},
                        {"name": "fonts", "children": []},
                        {"name": "icons", "children": []}
                    ]},
                    {"name": "utils", "children": []},
                    {"name": "hooks", "children": []},
                    {"name": "context", "children": []}
                ]
            },
            {
                "name": "public",
                "children": [
                    {"name": "images", "children": []},
                    {"name": "icons", "children": []}
                ]
            },
            {
                "name": "docs",
                "children": [
                    {"name": "design", "children": []},
                    {"name": "requirements", "children": []}
                ]
            },
            {
                "name": "tests",
                "children": [
                    {"name": "unit", "children": []},
                    {"name": "integration", "children": []},
                    {"name": "e2e", "children": []}
                ]
            }
        ]

        # Video Editing structure
        video_editing_structure = [
            {
                "name": "footage",
                "children": [
                    {"name": "raw", "children": []},
                    {"name": "processed", "children": []},
                    {"name": "b_roll", "children": []}
                ]
            },
            {
                "name": "audio",
                "children": [
                    {"name": "music", "children": []},
                    {"name": "sfx", "children": []},
                    {"name": "voiceover", "children": []}
                ]
            },
            {
                "name": "graphics",
                "children": [
                    {"name": "titles", "children": []},
                    {"name": "lower_thirds", "children": []},
                    {"name": "transitions", "children": []}
                ]
            },
            {
                "name": "exports",
                "children": [
                    {"name": "final", "children": []},
                    {"name": "drafts", "children": []},
                    {"name": "client_review", "children": []}
                ]
            },
            {
                "name": "project_files",
                "children": [
                    {"name": "premiere", "children": []},
                    {"name": "after_effects", "children": []},
                    {"name": "davinci", "children": []}
                ]
            }
        ]

        # Photography structure
        photography_structure = [
            {
                "name": "raw_photos",
                "children": [
                    {"name": "session_1", "children": []},
                    {"name": "session_2", "children": []},
                    {"name": "session_3", "children": []}
                ]
            },
            {
                "name": "edited_photos",
                "children": [
                    {"name": "high_res", "children": []},
                    {"name": "web_res", "children": []},
                    {"name": "social_media", "children": []}
                ]
            },
            {
                "name": "client_delivery",
                "children": [
                    {"name": "final_selection", "children": []},
                    {"name": "contact_sheets", "children": []}
                ]
            },
            {
                "name": "backup",
                "children": [
                    {"name": "raw_backup", "children": []},
                    {"name": "edited_backup", "children": []}
                ]
            }
        ]

        # Create predefined structures
        structures = [
            {
                'name': 'Motion Graphics Default',
                'structure_type': 'motion_graphics',
                'structure_data': motion_graphics_structure,
                'description': 'Default structure for motion graphics projects with After Effects, Photoshop, and Premiere Pro workflows'
            },
            {
                'name': 'Graphic Design Default',
                'structure_type': 'graphic_design',
                'structure_data': graphic_design_structure,
                'description': 'Default structure for graphic design projects including Photoshop, Illustrator, and CorelDraw'
            },
            {
                'name': 'Web Development Default',
                'structure_type': 'web_development',
                'structure_data': web_development_structure,
                'description': 'Modern web development project structure with React/Next.js conventions'
            },
            {
                'name': 'Video Editing Default',
                'structure_type': 'video_editing',
                'structure_data': video_editing_structure,
                'description': 'Comprehensive video editing project structure for various editing software'
            },
            {
                'name': 'Photography Default',
                'structure_type': 'photography',
                'structure_data': photography_structure,
                'description': 'Professional photography workflow structure for client projects'
            }
        ]

        created_count = 0
        for structure_data in structures:
            structure, created = PredefinedStructure.objects.get_or_create(
                name=structure_data['name'],
                created_by=admin_user,
                defaults={
                    'structure_type': structure_data['structure_type'],
                    'structure_data': structure_data['structure_data'],
                    'description': structure_data['description'],
                    'is_public': True,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created predefined structure: {structure.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Structure already exists: {structure.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {created_count} predefined structures')
        )
