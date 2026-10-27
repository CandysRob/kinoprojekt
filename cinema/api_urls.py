from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register("movies", api_views.MovieViewSet, basename="movie")
router.register("genres", api_views.GenreViewSet, basename="genre")
router.register("cinemas", api_views.CinemaViewSet, basename="cinema")
router.register("screenings", api_views.ScreeningViewSet, basename="screening")

urlpatterns = router.urls
