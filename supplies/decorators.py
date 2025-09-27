"""
Custom decorators for role-based access control.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def manager_required(view_func):
    """Decorator to require manager role for accessing a view."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Allow superusers to access all pages
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if hasattr(request.user, 'profile') and request.user.profile.is_manager:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. Manager privileges required.")
            # Redirect to appropriate dashboard based on user role
            if hasattr(request.user, 'profile') and request.user.profile.is_customer:
                return redirect('customer_dashboard')
            return redirect('login')
    return _wrapped_view


def customer_required(view_func):
    """Decorator to require customer role for accessing a view."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Allow superusers to access all pages
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if hasattr(request.user, 'profile') and request.user.profile.is_customer:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. Customer access only.")
            # Redirect to appropriate dashboard based on user role
            if hasattr(request.user, 'profile') and request.user.profile.is_manager:
                return redirect('manager_dashboard')
            return redirect('login')
    return _wrapped_view


def role_required(*roles):
    """Decorator to require specific roles for accessing a view."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Allow superusers to access all pages
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if hasattr(request.user, 'profile'):
                user_role = request.user.profile.role
                if user_role in roles:
                    return view_func(request, *args, **kwargs)
                
                # Redirect to appropriate dashboard based on user role
                messages.error(request, "Access denied. Insufficient privileges.")
                if user_role == 'MANAGER':
                    return redirect('manager_dashboard')
                elif user_role == 'CUSTOMER':
                    return redirect('customer_dashboard')
            
            return redirect('login')
        return _wrapped_view
    return decorator