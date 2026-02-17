from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']


def validate_image_size(image):
    if not image:
        return
    if image.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError('Image size must be 5 MB or less.')


image_extension_validator = FileExtensionValidator(
    allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
    message='Only JPG, JPEG, PNG, and WEBP images are allowed.',
)
