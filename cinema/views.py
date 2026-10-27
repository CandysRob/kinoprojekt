from django.db import DatabaseError, connection
from django.http import JsonResponse


def health(request):
    """Näitab, kas rakendus töötab ja andmebaas vastab."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
    except DatabaseError:
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})
