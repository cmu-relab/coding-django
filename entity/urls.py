from django.conf.urls import include, url
from . import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'coding.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index),
    url(r'^annotated$', views.annotated),
    url(r'^ontology$', views.ontology),
    url(r'^download$', views.download),
    url(r'^editor$', views.editor),
]
