from django.urls import path, include

urlpatterns = [
    # Include HR API under a named namespace to satisfy reverse('hr_api:...')
    path('', include(('Hr.api.urls', 'hr_api'), namespace='hr_api')),
]

