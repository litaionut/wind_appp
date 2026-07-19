"""Project object permissions."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.projects.models import ProjectMembership, ProjectRole


class IsProjectAdminOrReadMember(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        membership = ProjectMembership.objects.filter(
            project=obj, user=request.user
        ).first()
        if membership is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return membership.role == ProjectRole.PROJECT_ADMIN
