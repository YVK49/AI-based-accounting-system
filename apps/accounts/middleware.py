import threading
from django.shortcuts import get_object_or_404
from .models import Business

# Thread-local storage for current multitenancy context
_thread_locals = threading.local()

def get_current_business():
    return getattr(_thread_locals, 'business', None)

class MultitenancyMiddleware:
    """
    Middleware to handle multitenancy context.
    Expects 'X-Business-ID' header or session/query param.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        business_id = request.headers.get('X-Business-ID') or request.GET.get('business_id')
        
        if business_id and request.user.is_authenticated:
            # Security: Ensure user belongs to the organization that owns this business
            # or is a superuser.
            business = Business.objects.filter(
                id=business_id, 
                organization=request.user.organization
            ).first()
            
            if business:
                request.business = business
                _thread_locals.business = business
            else:
                request.business = None
                _thread_locals.business = None
        else:
            request.business = None
            _thread_locals.business = None

        response = self.get_response(request)
        
        # Cleanup
        if hasattr(_thread_locals, 'business'):
            del _thread_locals.business
            
        return response
