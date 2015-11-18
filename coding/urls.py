from django.conf.urls import include, url

urlpatterns = [
    # Examples:
    # url(r'^$', 'coding.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^kappa/', include('kappa.urls')),
    url(r'^entity/', include('entity.urls')),
]
