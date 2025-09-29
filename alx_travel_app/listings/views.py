from rest_framework import viewsets
from rest_framework.permissions import AllowAny  
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().order_by("-created_at")
    serializer_class = ListingSerializer
    permission_classes = [AllowAny]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by("-created_at")
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        listing = serializer.validated_data["property"]
        nights = (serializer.validated_data["end_date"] - serializer.validated_data["start_date"]).days
        total_price = nights * listing.price_per_night
        serializer.save(total_price=total_price)
