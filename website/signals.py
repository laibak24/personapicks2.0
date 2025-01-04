from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User  # Import your User model

@receiver(post_save, sender=User)
def assign_avatar_on_creation(sender, instance, created, **kwargs):
    if created and instance.mbti_type:  # Check if the user was just created
        # Generate the avatar path based on MBTI type
        avatar_filename = f"{instance.mbti_type}.jpg"  # e.g., intj.jpg
        instance.avatar = f"avatars/{avatar_filename}"
        instance.save()
