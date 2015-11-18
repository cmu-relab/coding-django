from django.conf.urls import include, url
from . import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'coding.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.kappa),
    url(r'^input.html$', views.input),
    url(r'^newinput$', views.newinput),
    url(r'^analyze$', views.analyze),
]
