from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import patterns, url
from maps.categories import views

urlpatterns = patterns(
    '',
    url(r'^$', 'maps.categories.views.category', name='category-list'),
    url(r'^add-category$', 'maps.categories.views.category_add'),
    url(r'^update-category/(?P<cat_id>[\w]{24})/$', 'maps.categories.views.category_update'),

    url(r'^add-taxonomy$', 'maps.categories.views.taxonomy_add'),
    url(r'^update-taxonomy/(?P<tax_id>[\w]{24})/$', 'maps.categories.views.taxonomy_update'),
)

urlpatterns = format_suffix_patterns(urlpatterns)

jsonurls = patterns(
    '',
    url(r'^categories/$', views.AddCategories.as_view()),
    url(r'^categories/(?P<id>[\w]{24})/$', views.UpdateCategory.as_view()),
    url(r'^categories/form-data/(?P<category_id>[\w]{24})?', views.CategoryFormData.as_view()),
    url(r'^categories/external-data/(?P<id>[\w]{24})?', views.CategoryExternalData.as_view()),

    url(r'^taxonomy/$', views.AddTaxonomy.as_view()),
    url(r'^taxonomy/(?P<id>[\w]{24})/$', views.UpdateTaxonomy.as_view()),
    url(r'^taxonomy/form-data/(?P<taxonomy_id>[\w]{24})?', views.TaxonomyFormData.as_view()),
    url(r'^taxonomy-tags/(?P<id>[\w]{24})/$', views.GetTaxonomyTags.as_view()),

    url(r'^cat_del/(?P<id>[\w]{24})/$', 'maps.categories.views.category_delete_view'),
    url(r'^tag_del/(?P<id>[\w]{24})/$', 'maps.categories.views.tag_delete_view'),        
    url(r'^categories/datatable', views.tags_datatable, name='tags-datatable'),
    url(r'^taxonomy/datatable', views.cats_datatable, name='category-datatable'),
)

jsonurls = format_suffix_patterns(jsonurls)
