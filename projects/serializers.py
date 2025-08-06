from rest_framework import serializers
from .models import Client, Project, FolderStructure, PredefinedStructure


class ClientSerializer(serializers.ModelSerializer):
    project_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'address', 
            'created_at', 'updated_at', 'is_active', 'project_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'project_count']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ClientListSerializer(serializers.ModelSerializer):
    project_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'phone', 'project_count', 'created_at']


class PredefinedStructureSerializer(serializers.ModelSerializer):
    structure_type_display = serializers.CharField(source='get_structure_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = PredefinedStructure
        fields = [
            'id', 'name', 'structure_type', 'structure_type_display',
            'structure_data', 'description', 'is_public', 'is_active',
            'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_username']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class FolderStructureSerializer(serializers.ModelSerializer):
    predefined_structure_name = serializers.CharField(
        source='predefined_structure.name', 
        read_only=True
    )
    
    class Meta:
        model = FolderStructure
        fields = [
            'id', 'name', 'structure_data', 'predefined_structure',
            'predefined_structure_name', 'is_active', 'is_created',
            'created_path', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'predefined_structure_name']


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    folder_structure_count = serializers.ReadOnlyField()
    full_project_path = serializers.ReadOnlyField()
    folder_structures = FolderStructureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client', 'client_name', 'description',
            'status', 'status_display', 'save_location', 'start_date',
            'end_date', 'budget', 'folder_structure_count', 'full_project_path',
            'folder_structures', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'client_name', 'status_display',
            'folder_structure_count', 'full_project_path', 'folder_structures'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate_client(self, value):
        """Ensure the client belongs to the current user"""
        if value.created_by != self.context['request'].user:
            raise serializers.ValidationError("You can only assign your own clients to projects.")
        return value


class ProjectListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    folder_structure_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client_name', 'status', 'status_display',
            'folder_structure_count', 'created_at', 'updated_at'
        ]


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name', 'client', 'description', 'status', 'save_location',
            'start_date', 'end_date', 'budget'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate_client(self, value):
        """Ensure the client belongs to the current user"""
        if value.created_by != self.context['request'].user:
            raise serializers.ValidationError("You can only assign your own clients to projects.")
        return value


class FolderStructureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderStructure
        fields = ['name', 'structure_data', 'predefined_structure']

    def validate_structure_data(self, value):
        """Validate the structure data format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Structure data must be a list of folders.")
        
        def validate_folder_item(item):
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each folder must be an object.")
            
            if 'name' not in item:
                raise serializers.ValidationError("Each folder must have a name.")
            
            if not item['name'].strip():
                raise serializers.ValidationError("Folder names cannot be empty.")
            
            children = item.get('children', [])
            if children:
                if not isinstance(children, list):
                    raise serializers.ValidationError("Children must be a list.")
                for child in children:
                    validate_folder_item(child)
        
        for item in value:
            validate_folder_item(item)
        
        return value


class StructureExportSerializer(serializers.Serializer):
    """Serializer for structure export data"""
    project = ProjectListSerializer(read_only=True)
    structure = FolderStructureSerializer(read_only=True)
    export_info = serializers.DictField(read_only=True)


class StructureImportSerializer(serializers.Serializer):
    """Serializer for structure import"""
    structure_file = serializers.FileField()
    name = serializers.CharField(max_length=100, required=False)
    
    def validate_structure_file(self, value):
        if not value.name.endswith('.json'):
            raise serializers.ValidationError("File must be a JSON file.")
        return value
