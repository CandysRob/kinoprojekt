"""
API vaated. Iga vaade loeb andmed PostgreSQL-ist Django ORM-iga ja tagastab
need JSON-ina. ReadOnlyModelViewSet annab kaks aadressi:

    /api/movies/       -> list (kõik filmid)
    /api/movies/5/     -> retrieve (üks film, puudumisel 404)

Filmide ja seansside nimekirja saab filtreerida kuupäeva järgi:
/api/movies/?date=2026-11-28 ja /api/screenings/?date=2026-11-28

Nimekirjad (list) on vahemälus, vaata README "Vahemälu plaan" ja cinema/signals.py.
"""

from datetime import date

from django.core.cache import cache
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Cinema, Genre, Movie, Screening
from .serializers import (
    CinemaSerializer,
    GenreSerializer,
    MovieDetailSerializer,
    MovieListSerializer,
    ScreeningSerializer,
)

MINUTE = 60
HOUR = 60 * MINUTE


class CachedListMixin:
    """Nimekiri tuleb vahemälust. Kui seal veel pole, tehakse päring ja vastus salvestatakse."""

    cache_seconds = MINUTE

    def get_cache_key(self):
        return f"api:{self.basename}:list"

    def list(self, request, *args, **kwargs):
        key = self.get_cache_key()
        data = cache.get(key)
        if data is None:
            data = super().list(request, *args, **kwargs).data
            cache.set(key, data, self.cache_seconds)
        return Response(data)


def get_date_filter(request):
    """`?date=2026-11-28` -> date(2026, 11, 28). Ilma kuupäevata None, vigase kuupäeva korral 400."""
    value = request.query_params.get("date")
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValidationError({"date": "Peab olema kuupäev kujul AAAA-KK-PP."})


class MovieViewSet(CachedListMixin, viewsets.ReadOnlyModelViewSet):
    """Filmid pealkirja järgi. `?date=2026-11-28` näitab ainult filme, millel on sel päeval seanss."""

    cache_seconds = 10 * MINUTE

    def get_cache_key(self):
        # Igal kuupäeval on oma kirje, ilma filtrita nimekirjal oma
        return f"api:movie:list:{get_date_filter(self.request) or 'all'}"

    def get_queryset(self):
        # prefetch_related laeb kõigi filmide žanrid ühe lisapäringuga, mitte iga filmi jaoks eraldi
        queryset = Movie.objects.prefetch_related("genres").order_by("title")
        selected_date = get_date_filter(self.request)
        if self.action == "list" and selected_date:
            # screenings__starts_at__date: seansi algusaja kuupäev Eesti aja järgi (settings.TIME_ZONE).
            # distinct(): film tuleb nimekirja ühe korra, ka siis, kui tal on sel päeval mitu seanssi.
            queryset = queryset.filter(screenings__starts_at__date=selected_date).distinct()
        return queryset

    def get_serializer_class(self):
        # Nimekirjas pole kirjeldust vaja, filmi lehel on
        return MovieDetailSerializer if self.action == "retrieve" else MovieListSerializer


class GenreViewSet(CachedListMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.order_by("name")
    serializer_class = GenreSerializer
    cache_seconds = HOUR


class CinemaViewSet(CachedListMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Cinema.objects.prefetch_related("halls").order_by("name")
    serializer_class = CinemaSerializer
    cache_seconds = HOUR


class ScreeningViewSet(CachedListMixin, viewsets.ReadOnlyModelViewSet):
    """
    Seansid algusaja järgi. Nimekirjas ainult tulevased.
    `?movie=5` näitab ühe filmi seansse, `?date=2026-11-28` ühe päeva seansse.
    """

    serializer_class = ScreeningSerializer
    # Lühike aeg, sest nimekirjas on ainult tulevased seansid
    cache_seconds = MINUTE

    def get_movie_filter(self):
        movie = self.request.query_params.get("movie")
        if movie and not movie.isdigit():
            raise ValidationError({"movie": "Peab olema filmi id (täisarv)."})
        return movie

    def get_cache_key(self):
        # Igal filmi ja kuupäeva kombinatsioonil on oma kirje, ilma filtrita nimekirjal oma
        movie = self.get_movie_filter() or "all"
        selected_date = get_date_filter(self.request) or "all"
        return f"api:screening:list:{movie}:{selected_date}"

    def get_queryset(self):
        # select_related toob filmi, saali ja kino samas päringus (SQL JOIN)
        queryset = Screening.objects.select_related("movie", "hall__cinema").order_by("starts_at")
        if self.action != "list":
            return queryset

        queryset = queryset.filter(starts_at__gte=timezone.now())
        movie = self.get_movie_filter()
        if movie:
            queryset = queryset.filter(movie_id=movie)
        selected_date = get_date_filter(self.request)
        if selected_date:
            # Algusaja kuupäev Eesti aja järgi (settings.TIME_ZONE)
            queryset = queryset.filter(starts_at__date=selected_date)
        return queryset
