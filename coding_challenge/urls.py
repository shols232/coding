from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('users/<int:user_id>/<int:task_id>/', views.user_list_view, name='users'),
    path('tasks/<int:user_id>/', views.task_list_view, name='tasks'),
    path('users/<int:request_user_id>/<int:task_id>/<int:user_id>/', views.user_send_request_view, name='user_send_request'),
    path('notifications/<int:user_id>/', views.notifications_view, name='notifications'),
    path('challenges/<int:user_id>/', views.challenges_view, name='challenges'),
    path('notification/process/<int:user_id>/<int:task_id>/<str:notification_status>/', views.notifications_processing_view, name='user_process_request')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)