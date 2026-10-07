from .models import StoreSettings

def store_settings(request):
    try:
        return {'store': StoreSettings.load()}
    except Exception:
        # Fallback if the database hasn't been migrated yet
        return {'store': None}
