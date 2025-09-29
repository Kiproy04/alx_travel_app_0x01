from django.db import models
import uuid
from decimal import Decimal

class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("canceled", "Canceled"),
    ]

    booking_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    property = models.ForeignKey(
        "Listing",
        on_delete=models.CASCADE,
        related_name="bookings"
    )


    start_date = models.DateField(
        null=False,
        blank=False
    )
    end_date = models.DateField(
        null=False,
        blank=False
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
        default=Decimal("0.00")
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Booking {self.property} - {self.total_price} ({self.status})"

class Listing(models.Model):
    property_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    name = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )

    description = models.TextField(
        null=False,
        blank=False
    )

    location = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )

    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
        default=Decimal("0.00")
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.name} - {self.location} (${self.price_per_night}/night)"

class Review(models.Model):
    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    property = models.ForeignKey(
        "Listing",
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.IntegerField(
        null=False,
        blank=False
    )

    comment = models.TextField(
        null=False,
        blank=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Review {self.review_id} - {self.rating}⭐"

    def clean(self):
        """Ensure rating is between 1 and 5."""
        from django.core.exceptions import ValidationError
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")
