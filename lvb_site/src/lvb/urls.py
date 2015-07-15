from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static
from lvb import views



urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^result/(?P<key_id>[A-Z,0-9]{6}_[a-z,0-9]{32})$', views.result, name='result'), #	re.search('(?P<key_id>[a-z]{3}_[a-z]{3})', b)
	url(r'^result/?key_id=(?P<key_id>[A-Z,0-9]{6}_[a-z,0-9]{32})&refresh=$', views.result, name='result'), #	re.search('(?P<key_id>[a-z]{3}_[a-z]{3})', b)
	url(r'^result_output_lvb/(?P<key_id>[A-Z,0-9]{6}_[a-z,0-9]{32})$', 'lvb.views.result_output_lvb', name='result_output_lvb'),
	url(r'^result_tree_lvb/(?P<key_id>[A-Z,0-9]{6}_[a-z,0-9]{32})$', 'lvb.views.result_tree_lvb', name='result_tree_lvb'),
	url(r'^result/', views.result_empty, name='result'),
	url(r'^otherOption/', views.other_option, name='result'),
	url(r'^contact/', views.contact),
	url(r'^about/', views.about),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)