from django.conf.urls import url, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('courses', views.CourseViewSet)

urlpatterns = [
	url(r'^subjects/$',
		views.SubjectListView.as_view(),
		name='subject_list'),
	url(r'^subjects/(?P<pk>\d+)/$',
		views.SubjectDetailView.as_view(),
		name='subject_detail'),
	url(r'^', include(router.urls)),
]