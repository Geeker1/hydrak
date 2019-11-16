"""educa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from account import views as asit_view
from django.conf import settings
from django.conf.urls import url, static,include,handler404,handler500
from django.conf.urls.static import static
from courses import views
from courses.views import CourseListView

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^pqskban/', admin.site.urls),
    url(r'^all-courses/$', CourseListView.as_view(), name='course_list'),
    url(r'^cart/', include('cart.urls', namespace='cart')),
    url(r'^course/',include('courses.urls')),
    url(r'^api/',include('courses.api.urls', namespace='api')),
    url(r'^students/', include('students.urls')),
    url(r'^login/$', auth_views.LoginView.as_view(
        template_name='accounts/login.html'),  name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(
    	template_name='accounts/logged_out.html'), name='logout'),

	url(r'^settings/password/$',auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'),
         name='password_change'),
	url(r'^settings/password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
    name='password_change_done'),
    url(r'^signup/$', asit_view.signup, name='signup'),
    url(r'^instructor/update/(?P<pk>\d+)/$', asit_view.ProfileUpdate.as_view(),name='profile_update'),
    url(r'^reset/$',
        auth_views.PasswordResetView.as_view
        (template_name='accounts/password_reset.html',
         email_template_name='accounts/password_reset_email.html',
         subject_template_name='accounts/password_reset_subject.txt'
         ),
        name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'),name='password_reset_complete'
        ),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

    