"""
API vaated. Iga vaade loeb andmed PostgreSQL-ist Django ORM-iga ja tagastab
need JSON-ina. ReadOnlyModelViewSet annab kaks aadressi:

    /api/movies/       -> list (kõik filmid)
    /api/movies/5/     -> retrieve (üks film, puudumisel 404)
"""

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Cinema, Genre, Movie, Screening
from .serializers import (
    CinemaSerializer,
    GenreSerializer,
    MovieDetailSerializer,
    MovieListSerializer,
    ScreeningSerializer,
)


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    # prefetch_related laeb kõigi filmide žanrid ühe lisapäringuga, mitte iga filmi jaoks eraldi
    queryset = Movie.objects.prefetch_related("genres").order_by("title")

    def get_serializer_class(self):
        # Nimekirjas pole kirjeldust vaja, filmi lehel on
        return MovieDetailSerializer if self.action == "retrieve" else MovieListSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.order_by("name")
    serializer_class = GenreSerializer


class CinemaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cinema.objects.prefetch_related("halls").order_by("name")
    serializer_class = CinemaSerializer


class ScreeningViewSet(viewsets.ReadOnlyModelViewSet):
    """Seansid algusaja järgi. Nimekirjas ainult tulevased, `?movie=5` näitab ühe filmi seansse."""

    serializer_class = ScreeningSerializer

    def get_queryset(self):
        # select_related toob filmi, saali ja kino samas päringus (SQL JOIN)
        queryset = Screening.objects.select_related("movie", "hall__cinema").order_by("starts_at")
        if self.action != "list":
            return queryset

        queryset = queryset.filter(starts_at__gte=timezone.now())
        movie = self.request.query_params.get("movie")
        if movie:
            if not movie.isdigit():
                raise ValidationError({"movie": "Peab olema filmi id (täisarv)."})
            queryset = queryset.filter(movie_id=movie)
        return queryset
