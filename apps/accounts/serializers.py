from rest_framework import serializers
from .models import User, Role

class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "phone_number", "must_change_password")
        read_only_fields = fields

class UserProvisionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)
    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "role", "phone_number", "faculty", "department", "password")
    def validate(self, attrs):
        if attrs.get("role") == Role.SUPER_ADMIN and not self.context["request"].user.is_superuser:
            raise serializers.ValidationError({"role": "Only an existing superuser can provision another super administrator."})
        faculty, department = attrs.get("faculty"), attrs.get("department")
        if department and faculty and department.faculty_id != faculty.id:
            raise serializers.ValidationError({"department": "Department must belong to the selected faculty."})
        if department and not faculty:
            attrs["faculty"] = department.faculty
        if attrs.get("role") == Role.FACULTY_ADMIN and not attrs.get("faculty"):
            raise serializers.ValidationError({"faculty": "Faculty administrators must be assigned a faculty."})
        if attrs.get("role") == Role.DEPARTMENT_ADMIN and not attrs.get("department"):
            raise serializers.ValidationError({"department": "Department administrators must be assigned a department."})
        return attrs
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.must_change_password = True
        user.save()
        return user
