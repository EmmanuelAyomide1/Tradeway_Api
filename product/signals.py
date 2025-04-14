from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from .models import Product, ProductImage
from .utils import deleteImageInCloudinary


from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver


@receiver(pre_save, sender=Product)
@receiver(pre_save, sender=ProductImage)
def handle_media_update(sender, instance, **kwargs):
    """
    Deletes old image and video from Cloudinary when updated.
    """
    try:
        if instance.id:
            old_instance = sender.objects.get(pk=instance.pk)

            if hasattr(instance, 'image') and old_instance.image != instance.image:
                deleteImageInCloudinary(old_instance.image)
                print("deleted successfully", old_instance.image)

            if hasattr(instance, 'video') and old_instance.video and old_instance.video != instance.video:
                deleteImageInCloudinary(old_instance.video)

    except Exception as e:
        print(f"Error in pre_save signal: {e}")


@receiver(pre_delete, sender=Product)
@receiver(pre_delete, sender=ProductImage)
def handle_media_delete(sender, instance, **kwargs):
    """
    Deletes image and video from Cloudinary when a product is deleted.
    """
    try:
        deleteImageInCloudinary(instance.image)

        if hasattr(instance, 'video'):
            deleteImageInCloudinary(instance.video)

        print("deleted successfull", instance.image)

    except Exception as e:
        print(f"Error in pre_delete signal: {e}")
