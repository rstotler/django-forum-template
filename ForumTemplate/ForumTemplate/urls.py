from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from forum import views as forum_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', forum_views.subforumListView, name='subforum-list'),
    path('<str:subforum_url>/', forum_views.threadListView, name='thread-list'),
    path('<str:subforum_url>/post/', forum_views.threadCreateView, name='thread-create'),
    path('<str:subforum_url>/thread-<int:thread_id>/edit/', forum_views.threadEditView, name='thread-edit'),
    path('<str:subforum_url>/thread-<int:thread_id>/delete/', forum_views.threadDeleteView, name='thread-delete'),
    path('<str:subforum_url>/thread-<int:thread_id>/', forum_views.postListView, name='post-list'),
    path('<str:subforum_url>/thread-<int:thread_id>/reply/', forum_views.postCreateView, name='post-create'),
    path('<str:subforum_url>/thread-<int:thread_id>/post-<int:post_id>/reply/', forum_views.postCreateReplyView, name='post-create-reply'),
    path('<str:subforum_url>/thread-<int:thread_id>/post-<int:post_id>/edit/', forum_views.postEditView, name='post-edit'),
    path('<str:subforum_url>/thread-<int:thread_id>/post-<int:post_id>/delete/', forum_views.postDeleteView, name='post-delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
