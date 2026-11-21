from .models import Order

def store_language(request):
    return {"is_english": request.session.get("store_language", "sw") == "en"}
