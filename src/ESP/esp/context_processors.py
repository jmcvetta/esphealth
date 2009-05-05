from ESP import settings

def path_definitions(request):
    return {
        'site_domain':'',
        'site_static_folder':settings.MEDIA_URL,
        'site_javascript_folder': '%s/js/' % settings.MEDIA_URL,
        'site_css_folder': '%s/css/' % settings.MEDIA_URL
        }
