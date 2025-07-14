"""
WSGI config for arabic_store project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabic_store.settings')

application = get_wsgi_application()

# Auto-migrate on startup (for Render Free Plan)
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    # Auto-collectstatic on startup (for Render Free Plan)
    call_command('collectstatic', interactive=False, verbosity=0)
except Exception as e:
    print(f"Auto-migrate/collectstatic error: {e}")

try:
    from django.core.management import call_command
    call_command('loaddata', 'produk.json')
except Exception as e:
    print(f"Auto-loaddata error: {e}")
