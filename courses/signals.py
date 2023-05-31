import os
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from courses.models import Content, File, Image


# delete file function
def _delete_file(path):
    """ Deletes file from filesystem. """
    if os.path.isfile(path):
        os.remove(path)


@receiver(post_delete, sender=File)
def post_delete_file_sys(sender, instance, *args, **kwargs):
    if instance.file:
        _delete_file(instance.file.path)


@receiver(post_delete, sender=Image)
def post_delete_image_sys(sender, instance, *args, **kwargs):
    if instance.image:
        _delete_file(instance.image.path)
