"""Organization domain services."""

from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole


class MembershipError(Exception):
    """Domain error for membership mutations."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def count_org_admins(organization: Organization) -> int:
    return OrganizationMembership.objects.filter(
        organization=organization,
        role=OrganizationRole.ORG_ADMIN,
    ).count()


def ensure_not_last_admin(
    membership: OrganizationMembership, new_role: str | None = None
) -> None:
    """Raise if operation would leave the organization without an org_admin."""
    if membership.role != OrganizationRole.ORG_ADMIN:
        return
    if new_role is not None and new_role == OrganizationRole.ORG_ADMIN:
        return
    if count_org_admins(membership.organization) <= 1:
        raise MembershipError("Cannot remove or demote the last organization admin.")
