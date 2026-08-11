from rest_framework import serializers
from .models import Offer
from datetime import date
from django.db.models import Q

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_package_lpa(self, value):
        if value <= 0:
            raise serializers.ValidationError("package_lpa must be greater than 0")
        return value

    def validate(self, data):
        # joining_date cannot be before offer_date
        joining_date = data.get('joining_date')
        offer_date = data.get('offer_date')
        
        # In partial updates, we might only have one of them in data, so fetch the other from instance
        if self.instance:
            joining_date = joining_date or self.instance.joining_date
            offer_date = offer_date or self.instance.offer_date
            
        if joining_date and offer_date and joining_date < offer_date:
            raise serializers.ValidationError({"joining_date": "joining_date cannot be before offer_date"})

        # valid offer_type and status are handled by Django's choices validation natively via ModelSerializer, 
        # but we can explicitly enforce it if needed. The default ModelSerializer handles choice validation.
        
        # check duplicate active offers
        application = data.get('application')
        status = data.get('status')
        
        if self.instance:
            application = application or self.instance.application
            status = status or self.instance.status

        # If it's a new offer or changing status to active, check for existing active offers
        if status in ['PENDING', 'ACCEPTED']:
            active_offers = Offer.objects.filter(
                application=application,
                status__in=['PENDING', 'ACCEPTED']
            )
            if self.instance:
                active_offers = active_offers.exclude(id=self.instance.id)
                
            if active_offers.exists():
                raise serializers.ValidationError("This application already has an active offer.")

        return data

class RespondOfferSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')])

    def validate(self, data):
        offer = self.context.get('offer')
        if not offer:
            raise serializers.ValidationError("Offer instance is required in context.")
            
        if offer.status in ['ACCEPTED', 'REJECTED', 'WITHDRAWN']:
            raise serializers.ValidationError("Cannot respond to an offer that is already ACCEPTED, REJECTED, or WITHDRAWN.")
            
        return data
