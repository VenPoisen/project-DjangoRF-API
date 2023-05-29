from .environment import BASE_DIR, DEBUG
import mimetypes

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'base_static',
]

if not DEBUG:
    STATIC_ROOT = str(BASE_DIR / 'static')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

mimetypes.add_type("text/html", ".html", True)
