from .views import WHATSAPP_URL


def whatsapp(request):
    return {"whatsapp_url": WHATSAPP_URL}
