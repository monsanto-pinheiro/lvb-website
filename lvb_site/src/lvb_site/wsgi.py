"""
WSGI config for lvb_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os, sys, platform
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lvb_site.settings")

path = '/var/www/html/lvb'
if path not in sys.path:
	sys.path.append(path)

## need because of lvb server
if (platform.node() <> 'anarin'):	
	os.environ['SGE_ROOT'] = '/opt/sge'

	
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
