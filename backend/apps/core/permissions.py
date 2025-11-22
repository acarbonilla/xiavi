from rest_framework import permissions


class IsHRUser(permissions.BasePermission):
    """
    Permission to only allow HR users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_hr


class IsApplicant(permissions.BasePermission):
    """
    Permission to only allow applicant users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_applicant


class IsOwnerOrHR(permissions.BasePermission):
    """
    Permission to allow owners or HR users to access.
    """
    def has_object_permission(self, request, view, obj):
        # HR can access everything
        if request.user.is_hr:
            return True
        
        # Check if object has applicant field
        if hasattr(obj, 'applicant'):
            return obj.applicant == request.user
        
        # Check if object has user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
