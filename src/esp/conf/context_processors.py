import datetime
from esp.settings import MEDIA_URL
from esp.settings import VERSION
from esp.settings import SITE_NAME
from esp.settings import DATE_FORMAT

def path_definitions(request):
    return {
        'site_domain':'',
        'site_static_folder':MEDIA_URL,
        'site_javascript_folder': '%s/js/' % MEDIA_URL,
        'site_css_folder': '%s/css/' % MEDIA_URL,
        'site_image_folder': '%s/images/' % MEDIA_URL,
        'version': VERSION,
        'site_name': SITE_NAME,
        'date': datetime.datetime.now().strftime(DATE_FORMAT),
        }