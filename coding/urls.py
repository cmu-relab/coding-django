from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'coding.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^kappa/', include('kappa.urls')),
    url(r'^entity/', include('entity.urls')),
    url(r'^ontology/', include('ontology.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
