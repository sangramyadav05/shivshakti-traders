from rest_framework import serializers
from products.models import Product
from enquiries.models import ProductEnquiry


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'category',
            'category_slug',
            'short_description',
            'full_description',
            'uses',
            'image_url',
            'is_active',
            'created_at',
            'updated_at',
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ProductEnquirySerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Product.objects.filter(is_active=True),
    )

    class Meta:
        model = ProductEnquiry
        fields = ['id', 'product', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
            'message': {'required': True},
        }

    def validate_name(self, value):
        name = value.strip()
        if len(name) < 2:
            raise serializers.ValidationError('Name should be at least 2 characters long.')
        return name

    def validate_phone(self, value):
        phone = value.strip()
        if phone and len(phone) < 7:
            raise serializers.ValidationError('Enter a valid phone number.')
        return phone

    def validate_message(self, value):
        message = value.strip()
        if len(message) < 10:
            raise serializers.ValidationError('Message should be at least 10 characters long.')
        return message
