from rest_framework import serializers
from datetime import date

from .models import Booking, Listing


class BookingSerializer(serializers.ModelSerializer):
    property = serializers.StringRelatedField(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        source="property",
        queryset=Listing.objects.all(),
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "property",      
            "property_id",  
            "start_date",
            "end_date",
            "total_price",
            "status",
            "created_at",
        ]
        read_only_fields = ["booking_id", "created_at", "total_price"]

    def validate(self, data):
        start = data.get("start_date")
        end = data.get("end_date")
        property_instance = data.get("property")

        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        if property_instance and start and end:
            overlapping = Booking.objects.filter(
                property=property_instance,
                status__in=["pending", "confirmed"],  
                start_date__lt=end,  
                end_date__gt=start   
            )

            if self.instance:
                overlapping = overlapping.exclude(booking_id=self.instance.booking_id)

            if overlapping.exists():
                raise serializers.ValidationError(
                    {"non_field_errors": "This property is already booked for the selected dates."}
                )

        return data

    def create(self, validated_data):
        listing = validated_data["property"]
        start = validated_data["start_date"]
        end = validated_data["end_date"]

        nights = (end - start).days
        validated_data["total_price"] = listing.price_per_night * nights

        return super().create(validated_data)

    def update(self, instance, validated_data):
        listing = validated_data.get("property", instance.property)
        start = validated_data.get("start_date", instance.start_date)
        end = validated_data.get("end_date", instance.end_date)

        nights = (end - start).days
        validated_data["total_price"] = listing.price_per_night * nights

        return super().update(instance, validated_data)


class ListingSerializer(serializers.ModelSerializer):
    bookings_count = serializers.IntegerField(
        source="bookings.count", read_only=True
    ) 

    bookings = BookingSerializer(
        many=True, read_only=True
    ) 

    class Meta:
        model = Listing
        fields = [
            "property_id",
            "name",
            "description",
            "location",
            "price_per_night",
            "created_at",
            "updated_at",
            "bookings_count",
            "bookings",
        ]
        read_only_fields = ["property_id", "created_at", "updated_at"]

    def validate_price_per_night(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price per night must be greater than zero."
            )
        return value