from django.contrib import admin
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    BookedSeat,
    Booking,
    Cinema,
    Genre,
    Hall,
    Movie,
    MovieGenre,
    News,
    Payment,
    Review,
    Screening,
    Seat,
    User,
)


class UserCreationForm(auth_forms.BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone_number")


class UserChangeForm(auth_forms.UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Isikuandmed", {"fields": ("first_name", "last_name", "email", "phone_number", "date_of_birth")}),
        ("Õigused", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Kuupäevad", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "first_name", "last_name", "phone_number", "password1", "password2"),
            },
        ),
    )


class HallInline(admin.TabularInline):
    model = Hall
    extra = 0


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country")
    inlines = [HallInline]


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "cinema", "screen_type", "capacity")
    list_filter = ("cinema", "screen_type")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("hall", "row", "number")
    list_filter = ("hall",)


class MovieGenreInline(admin.TabularInline):
    model = MovieGenre
    extra = 1


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "duration_minutes", "age_rating", "is_featured")
    list_filter = ("is_featured", "genres")
    search_fields = ("title",)
    inlines = [MovieGenreInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ("movie", "hall", "starts_at", "ends_at", "base_price")
    list_filter = ("hall__cinema", "movie")
    date_hierarchy = "starts_at"


class BookedSeatInline(admin.TabularInline):
    model = BookedSeat
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "screening", "status", "total", "created_at")
    list_filter = ("status",)
    inlines = [BookedSeatInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "amount", "method", "status", "paid_at")
    list_filter = ("status", "method")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "user", "rating", "created_at")
    list_filter = ("rating",)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "cinema", "author", "published_at")
    list_filter = ("cinema",)
    search_fields = ("title",)
