from rest_framework import permissions

class IsTutor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'tutor'
    


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Ensure the user is authenticated and has the role 'admin'
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

