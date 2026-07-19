"""Project domain services."""

from apps.projects.models import Project, ProjectMembership, ProjectRole


class ProjectMembershipError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def count_project_admins(project: Project) -> int:
    return ProjectMembership.objects.filter(
        project=project,
        role=ProjectRole.PROJECT_ADMIN,
    ).count()


def ensure_not_last_project_admin(
    membership: ProjectMembership, new_role: str | None = None
) -> None:
    if membership.role != ProjectRole.PROJECT_ADMIN:
        return
    if new_role is not None and new_role == ProjectRole.PROJECT_ADMIN:
        return
    if count_project_admins(membership.project) <= 1:
        raise ProjectMembershipError("Cannot remove or demote the last project admin.")
