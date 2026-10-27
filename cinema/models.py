"""
Kinoprojekti mudelid.

Tabelid ja veerud vastavad failile project.sql: Pythonis on ingliskeelsed
nimed, andmebaasis jäävad `db_table` ja `db_column` abil eestikeelsed nimed.
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.functions import Now


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("Kasutajanimi on kohustuslik.")
        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("Superkasutajal peavad olema is_staff=True ja is_superuser=True.")
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # Django autentimise jaoks on project.sql-iga võrreldes juurde tulnud
    # last_login, is_active, is_staff ja is_superuser ning kasutajanimi on unikaalne.
    username = models.CharField(max_length=255, unique=True, db_column="user")
    first_name = models.CharField(max_length=1024)
    last_name = models.CharField(max_length=1024)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(max_length=1024)
    date_of_birth = models.DateField(null=True, blank=True)
    password = models.TextField(db_column="password_hash")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "first_name", "last_name", "phone_number"]

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.username


class Cinema(models.Model):
    name = models.CharField(max_length=255, db_column="kino_nimi")
    street_address = models.CharField(max_length=255, db_column="tänava_aadress")
    city = models.CharField(max_length=255, db_column="linn")
    postal_code = models.CharField(max_length=32, db_column="postiindeks")  # tekst, sest võib alata nulliga
    country = models.CharField(max_length=255, db_column="riik")

    class Meta:
        db_table = "kino"

    def __str__(self):
        return self.name


class Hall(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.PROTECT, related_name="halls", db_column="kino_id")
    name = models.CharField(max_length=50)
    screen_type = models.CharField(max_length=20, default="2D", db_default="2D", db_column="ekraani_tüüp")
    capacity = models.PositiveSmallIntegerField(db_column="mahutavus")

    class Meta:
        db_table = "kinosaalid"

    def __str__(self):
        return f"{self.cinema} – {self.name}"


class Seat(models.Model):
    id = models.AutoField(primary_key=True)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="seats", db_column="kinosaal_id")
    row = models.CharField(max_length=3, db_column="rida")
    number = models.PositiveSmallIntegerField(db_column="istekoht")

    class Meta:
        db_table = "istekohad"
        constraints = [
            models.UniqueConstraint(fields=["hall", "row", "number"], name="unique_seat_in_hall"),
        ]

    def __str__(self):
        return f"{self.hall}, rida {self.row}, koht {self.number}"


class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, db_column="nimi")

    class Meta:
        db_table = "žanrid"

    def __str__(self):
        return self.name


class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, default="", db_default="", db_column="pealkiri")
    description = models.TextField(null=True, blank=True, db_column="kirjeldus")
    duration_minutes = models.PositiveSmallIntegerField(default=0, db_default=0, db_column="filmi_pikkus")
    release_date = models.DateField(null=True, blank=True, db_column="väljalaskekuupäev")
    age_rating = models.CharField(max_length=10, null=True, blank=True, db_column="vanusepiirang")
    language = models.CharField(max_length=50, null=True, blank=True, db_column="keel")
    poster_url = models.URLField(max_length=500, null=True, blank=True, db_column="plakati_url")
    trailer_url = models.URLField(max_length=500, null=True, blank=True, db_column="treileri_url")
    is_featured = models.BooleanField(default=False, db_default=False, db_column="väikeväärtus")
    genres = models.ManyToManyField(Genre, through="MovieGenre", related_name="movies", blank=True)

    class Meta:
        db_table = "filmid"

    def __str__(self):
        return self.title


class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column="filmi_id")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, db_column="žanri_id")

    class Meta:
        db_table = "filmid_zanrid"
        constraints = [
            models.UniqueConstraint(fields=["movie", "genre"], name="unique_movie_genre"),
        ]


class Screening(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="screenings", db_column="filmi_id")
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="screenings", db_column="saali_id")
    starts_at = models.DateTimeField(db_column="algus_aeg")
    ends_at = models.DateTimeField(db_column="lopu_aeg")
    language = models.CharField(max_length=50, null=True, blank=True, db_column="keel")
    subtitles = models.CharField(max_length=50, null=True, blank=True, db_column="subtiitrid")
    base_price = models.DecimalField(max_digits=8, decimal_places=2, db_column="alghind")

    class Meta:
        db_table = "seansid"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ends_at__gt=models.F("starts_at")),
                name="screening_end_after_start",
                violation_error_message="Seansi lõpp peab olema pärast algust.",
            ),
        ]

    def __str__(self):
        return f"{self.movie} – {self.starts_at:%d.%m.%Y %H:%M}"


class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings", db_column="kasutaja_id")
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name="bookings", db_column="seansi_id")
    status = models.CharField(max_length=20, default="ootel", db_default="ootel", db_column="staatus")
    total = models.DecimalField(max_digits=8, decimal_places=2, db_column="kogusumma")
    created_at = models.DateTimeField(db_default=Now(), db_column="loodud")

    class Meta:
        db_table = "broneeringud"

    def __str__(self):
        return f"Broneering {self.pk}"


class BookedSeat(models.Model):
    id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="seats", db_column="broneeringu_id")
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name="booked_seats", db_column="seansi_id")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="bookings", db_column="istekoha_id")
    price = models.DecimalField(max_digits=8, decimal_places=2, db_column="hind")

    class Meta:
        db_table = "broneeritud_kohad"
        constraints = [
            # sama koht saab ühel seansil olla broneeritud ainult üks kord
            models.UniqueConstraint(
                fields=["screening", "seat"],
                name="unique_booked_seat_per_screening",
                violation_error_message="See koht on sellel seansil juba broneeritud.",
            ),
        ]


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments", db_column="broneeringu_id")
    amount = models.DecimalField(max_digits=8, decimal_places=2, db_column="summa")
    method = models.CharField(max_length=30, db_column="makseviis")
    status = models.CharField(max_length=20, db_column="staatus")
    reference = models.CharField(max_length=255, null=True, blank=True, db_column="makse_viide")  # tekib alles makseteenuselt
    paid_at = models.DateTimeField(null=True, blank=True, db_column="makstud")  # null, kuni makse pole tehtud

    class Meta:
        db_table = "maksed"


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews", db_column="kasutaja_id")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews", db_column="filmi_id")
    rating = models.SmallIntegerField(null=True, blank=True, db_column="hinnang")
    comment = models.TextField(null=True, blank=True, db_column="kommentaar")
    created_at = models.DateTimeField(db_default=Now(), db_column="loodud")

    class Meta:
        db_table = "arvustused"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_between_1_and_5",
                violation_error_message="Hinnang peab olema vahemikus 1–5.",
            ),
        ]


class News(models.Model):
    id = models.AutoField(primary_key=True)
    cinema = models.ForeignKey(  # null = uudis kõigile kinodele
        Cinema, on_delete=models.CASCADE, null=True, blank=True, related_name="news", db_column="kino_id"
    )
    author = models.ForeignKey(  # autori kustutamisel uudis jääb alles
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="news", db_column="autor_id"
    )
    title = models.CharField(max_length=255, db_column="pealkiri")
    body = models.TextField(db_column="sisu")
    image_url = models.URLField(max_length=500, null=True, blank=True, db_column="pildi_url")
    published_at = models.DateTimeField(null=True, blank=True, db_column="avaldatud")  # null = mustand
    created_at = models.DateTimeField(db_default=Now(), db_column="loodud")

    class Meta:
        db_table = "uudised"
        verbose_name_plural = "news"

    def __str__(self):
        return self.title
