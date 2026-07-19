"""Organization object permissions."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.organizations.models import OrganizationMembership, OrganizationRole


class IsOrganizationMember(BasePermission):
    """Allow access if the user is a member of the organization."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        return OrganizationMembership.objects.filter(
            organization=obj,
            user=request.user,
        ).exists()


class IsOrganizationAdmin(BasePermission):
    """Allow unsafe methods only for org_admin (or superuser)."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return OrganizationMembership.objects.filter(
                organization=obj,
                user=request.user,
            ).exists()
        return OrganizationMembership.objects.filter(
            organization=obj,
            user=request.user,
            role=OrganizationRole.ORG_ADMIN,
        ).exists()
