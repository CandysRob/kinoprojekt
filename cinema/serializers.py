"""
API serialiseerijad.

API on ainult lugemiseks ja näitab avalikke andmeid (filmid, žanrid, kinod,
seansid). Kasutajate, broneeringute ja maksete andmeid siit ei väljastata.
"""

from rest_framework import serializers

from .models import Cinema, Genre, Hall, Movie, Screening


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = ["id", "name", "screen_type", "capacity"]


class CinemaSerializer(serializers.ModelSerializer):
    halls = HallSerializer(many=True, read_only=True)

    class Meta:
        model = Cinema
        fields = ["id", "name", "street_address", "city", "postal_code", "country", "halls"]


class MovieListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "duration_minutes",
            "release_date",
            "age_rating",
            "language",
            "poster_url",
            "is_featured",
            "genres",
        ]


class MovieDetailSerializer(MovieListSerializer):
    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + ["description", "trailer_url"]


class ScreeningMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "duration_minutes", "age_rating", "poster_url"]


class ScreeningHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = ["id", "name", "screen_type"]


class ScreeningCinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ["id", "name", "city"]


class ScreeningSerializer(serializers.ModelSerializer):
    movie = ScreeningMovieSerializer(read_only=True)
    hall = ScreeningHallSerializer(read_only=True)
    cinema = ScreeningCinemaSerializer(source="hall.cinema", read_only=True)

    class Meta:
        model = Screening
        fields = ["id", "starts_at", "ends_at", "language", "subtitles", "base_price", "movie", "hall", "cinema"]
