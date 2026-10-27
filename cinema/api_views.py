from datetime import date, datetime, time, timedelta

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from .models import Cinema, Genre, Movie, Screening
from .serializers import (
    CinemaSerializer,
    GenreSerializer,
    MovieDetailSerializer,
    MovieListSerializer,
    ScreeningSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 100


def int_param(request, name):
    value = request.query_params.get(name)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        raise ValidationError({name: "Peab olema täisarv."})


def bool_param(request, name):
    value = request.query_params.get(name)
    if value in (None, ""):
        return None
    if value.lower() in ("1", "true"):
        return True
    if value.lower() in ("0", "false"):
        return False
    raise ValidationError({name: "Peab olema true või false."})


def date_param(request, name):
    value = request.query_params.get(name)
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValidationError({name: "Kuupäev peab olema kujul AAAA-KK-PP."})


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Filmid. Filtrid: `search` (pealkiri), `genre` (žanri id), `featured`
    (esiletõstetud) ja `now_showing` (ainult tulevate seanssidega filmid).
    """

    pagination_class = StandardPagination

    def get_serializer_class(self):
        return MovieDetailSerializer if self.action == "retrieve" else MovieListSerializer

    def get_queryset(self):
        queryset = Movie.objects.prefetch_related("genres").order_by("title", "id")
        if self.action != "list":
            return queryset

        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(title__icontains=search)
        genre = int_param(self.request, "genre")
        if genre is not None:
            queryset = queryset.filter(genres__id=genre)
        featured = bool_param(self.request, "featured")
        if featured is not None:
            queryset = queryset.filter(is_featured=featured)
        if bool_param(self.request, "now_showing"):
            upcoming = Screening.objects.filter(starts_at__gte=timezone.now()).values("movie_id")
            queryset = queryset.filter(id__in=upcoming)
        return queryset


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.order_by("name")
    serializer_class = GenreSerializer
    pagination_class = None


class CinemaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cinema.objects.prefetch_related("halls").order_by("name")
    serializer_class = CinemaSerializer
    pagination_class = None


class ScreeningViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tulevased seansid algusaja järgi. Filtrid: `movie` (filmi id),
    `cinema` (kino id) ja `date` (AAAA-KK-PP, Eesti aja järgi).
    """

    serializer_class = ScreeningSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Screening.objects.select_related("movie", "hall__cinema").order_by("starts_at", "id")
        if self.action != "list":
            return queryset

        queryset = queryset.filter(starts_at__gte=timezone.now())
        movie = int_param(self.request, "movie")
        if movie is not None:
            queryset = queryset.filter(movie_id=movie)
        cinema = int_param(self.request, "cinema")
        if cinema is not None:
            queryset = queryset.filter(hall__cinema_id=cinema)
        day = date_param(self.request, "date")
        if day is not None:
            start = timezone.make_aware(datetime.combine(day, time.min))
            queryset = queryset.filter(starts_at__gte=start, starts_at__lt=start + timedelta(days=1))
        return queryset
