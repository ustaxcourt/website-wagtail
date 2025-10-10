from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.apps import apps


# Shared patching flag for all storage classes
_wagtail_patched = False


def patch_wagtail():
    """
    Patch Wagtail's BaseImageForm to work with overwrite behavior.
    Shared across all storage backends.
    """
    global _wagtail_patched

    if _wagtail_patched:
        return

    try:
        from wagtail.images.forms import BaseImageForm
        from wagtail.search import index as search_index

        def patched_save(self, commit=True):
            if "file" in self.changed_data:
                self.instance._set_image_file_metadata()

            old_file_name = self.original_file.name if self.original_file else None
            super(BaseImageForm, self).save(commit=commit)

            if commit:
                if "file" in self.changed_data and self.original_file:
                    new_file_name = self.instance.file.name

                    # Only delete old file if filename changed
                    if old_file_name != new_file_name:
                        self.original_file.storage.delete(self.original_file.name)

                    # Always delete renditions when file changes
                    self.instance.renditions.all().delete()

                search_index.insert_or_update_object(self.instance)

            return self.instance

        BaseImageForm.save = patched_save
        _wagtail_patched = True
        print("✓ Wagtail patched for overwrite storage behavior")

    except ImportError:
        # Wagtail not installed, skip patching
        pass


@deconstructible
class OverwriteFileSystemStorage(FileSystemStorage):
    """
    Custom FileSystemStorage that overwrites files with the same name.
    Automatically patches Wagtail on first use.
    """

    def get_available_name(self, name, max_length=None):
        """
        Return the filename as-is, deleting any existing file first.
        Patches Wagtail on first call (when apps are ready).
        """
        # Patch Wagtail the first time this method is called (apps are ready by then)
        if not _wagtail_patched and apps.apps_ready:
            patch_wagtail()

        if self.exists(name):
            self.delete(name)
        return name


@deconstructible
class OverwriteS3Storage:
    """
    Custom S3 storage that overwrites files with the same name.
    Automatically patches Wagtail on first use.

    This is a mixin-style class that adds overwrite behavior to S3Boto3Storage.
    """

    def get_available_name(self, name, max_length=None):
        """
        Return the filename as-is, deleting any existing file first.
        Patches Wagtail on first call (when apps are ready).
        """
        # Patch Wagtail the first time this method is called (apps are ready by then)
        if not _wagtail_patched and apps.apps_ready:
            patch_wagtail()

        # For S3, we simply return the name and let S3 overwrite
        # This is more efficient than explicitly deleting first
        if self.exists(name):
            self.delete(name)
        return name


# Import S3Boto3Storage and create a combined class
try:
    from storages.backends.s3boto3 import S3Boto3Storage

    @deconstructible
    class OverwriteS3Boto3Storage(OverwriteS3Storage, S3Boto3Storage):
        """
        S3 storage backend that overwrites files with the same name.
        Combines OverwriteS3Storage behavior with S3Boto3Storage.
        """

        pass

except ImportError:
    # storages library not installed, create a placeholder
    class OverwriteS3Boto3Storage:
        """Placeholder for when django-storages is not installed."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "django-storages is required for S3 storage. "
                "Install it with: pip install django-storages boto3"
            )
