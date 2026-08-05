from django.urls import path
from .views import CompanyViewSet

app_name = 'companies'

# Explicitly map the ViewSet methods to match the requested API endpoints
company_list = CompanyViewSet.as_view({
    'get': 'list',
})

company_create = CompanyViewSet.as_view({
    'post': 'create'
})

company_detail = CompanyViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', company_list, name='company-list'),
    path('create/', company_create, name='company-create'),
    path('<int:pk>/', company_detail, name='company-detail'),
]
