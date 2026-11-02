"""
Vahemälu tühistamine.

API nimekirjad on vahemälus (api_views.CachedListMixin). Kui filmi, žanri,
kino, saali või seanssi lisatakse, muudetakse või kustutatakse (näiteks
admin-paneelis või käsuga seed_dev_data), tühjendatakse vahemälu ja järgmine
päring loeb värsked andmed andmebaasist.
"""

from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save

from .models import Cinema, Genre, Hall, Movie, MovieGenre, Screening

CACHED_MODELS = [Movie, Genre, MovieGenre, Cinema, Hall, Screening]


def clear_api_cache(sender, **kwargs):
    # Neid andmeid muudetakse harva, seega on lihtsam tühjendada kogu vahemälu
    # kui otsida üles kõik võtmed, kus muudetud rida võib olla (nt iga filmi seansid)
    cache.clear()


for model in CACHED_MODELS:
    post_save.connect(clear_api_cache, sender=model)
    post_delete.connect(clear_api_cache, sender=model)

# movie.genres.add(...) ja .remove(...) ei saada post_save signaali
m2m_changed.connect(clear_api_cache, sender=MovieGenre)
