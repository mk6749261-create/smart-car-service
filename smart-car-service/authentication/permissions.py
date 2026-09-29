from rest_framework.permissions import BasePermission

from .models import User


class IsCustomer(BasePermission):
    message = "This action is restricted to Customer accounts."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role == User.Role.CUSTOMER
        )


class IsTechnician(BasePermission):
    message = "This action is restricted to Technician accounts."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role == User.Role.TECHNICIAN
        )


class IsManager(BasePermission):
    message = "This action is restricted to Manager accounts."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role == User.Role.MANAGER
        )


class IsManagerOrTechnician(BasePermission):
    message = "This action is restricted to Manager or Technician accounts."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in (User.Role.MANAGER, User.Role.TECHNICIAN)
        )
