# Squashed migration: 0093 through 0098
# - Renames "Press Releases" collection and tag to "News and Announcements"
# - Creates "Home Page News Images" subcollection and moves images into it
# - Changes NewsItem.image on_delete to PROTECT

import django.db.models.deletion
import home.models.snippets.news_item
from django.db import migrations, models


# Updates the name of the tag with the name of [old_tag_name] to [new_tag_name]
def update_tag_name(apps, schema_editor, old_tag_name, new_tag_name):
    Tag = apps.get_model("taggit", "Tag")
    tag = Tag.objects.get(name=old_tag_name)
    tag.name = new_tag_name
    tag.save()


# Updates the "Press Releases" collection and tag to be named "News and Announcements"
def rename_collection_and_tag_to_new_name(apps, schema_editor):
    Collection = apps.get_model("wagtailcore", "Collection")

    old_collection_name = "Press Releases"
    new_collection_name = "News and Announcements"

    try:
        coll = Collection.objects.get(name=old_collection_name)
    except Collection.DoesNotExist:
        raise RuntimeError(
            f"Old collection '{old_collection_name}' does not exist. Migration aborted."
        )

    # Rename collection if it exists
    coll.name = new_collection_name
    coll.save(update_fields=["name"])

    try:
        update_tag_name(apps, schema_editor, old_collection_name, new_collection_name)
    except Exception as e:
        raise RuntimeError(
            f"Error while checking updating tag '{old_collection_name}' to '{new_collection_name}'. Migration aborted. Error: {e}"
        )


# Updates the "News and Announcements" collection and tag back to "Press Releases"
def rename_tag_and_collection_back_to_old_name(apps, schema_editor):
    Collection = apps.get_model("wagtailcore", "Collection")

    current_collection_name = "News and Announcements"
    previous_collection_name = "Press Releases"

    try:
        update_tag_name(
            apps, schema_editor, current_collection_name, previous_collection_name
        )
    except Exception as e:
        raise RuntimeError(
            f"Error while checking updating tag '{current_collection_name}' to '{previous_collection_name}'. Migration aborted. Error: {e}"
        )

    try:
        coll = Collection.objects.get(name=current_collection_name)
    except Collection.DoesNotExist:
        raise RuntimeError(
            f"Old collection '{current_collection_name}' does not exist. Migration aborted."
        )

    # Rename collection if it exists
    coll.name = previous_collection_name
    coll.save(update_fields=["name"])


# Creates the subcollection "Home Page News Images" if it doesn't exist, places
# it as a subcollection of the "News and Announcements" collection, and move any
# images that exist in the "News and Announcements" collection to the "Home Page
# News Images" subcollection.
def create_subcollection_under_parent(apps, schema_editor):
    Collection = apps.get_model("wagtailcore", "Collection")

    parent_name = "News and Announcements"
    subcollection_name = "Home Page News Images"
    parent_collection_real = None

    try:
        Collection.objects.get(name=parent_name)
    except Collection.DoesNotExist:
        raise RuntimeError(
            f"Parent collection '{parent_name}' does not exist. Migration aborted."
        )

    # Create subcollection if it doesn't already exist under this parent
    from wagtail.models import Collection as RealCollection

    try:
        # Use the real model to get the root and create the child
        parent_collection_real = RealCollection.objects.get(name=parent_name)
        if (
            not parent_collection_real.get_children()
            .filter(name=subcollection_name)
            .exists()
        ):
            parent_collection_real.add_child(name=subcollection_name)
    except Exception as e:
        raise RuntimeError(
            f"Could not create subcollection '{subcollection_name}' under collection '{parent_name}'. Migration aborted. Error: {e}"
        )

    from wagtail.images.models import Image as RealImage

    # Move images in "News and Announcements" collection to "Home Page News Images"
    # (These are images that were in the "Press Releases" collection before that collection was
    # renamed to "News and Announcements" in the previous migration script)
    try:
        subcollection_real = RealCollection.objects.get(name=subcollection_name)
        for newsImage in RealImage.objects.filter(collection=parent_collection_real):
            newsImage.collection = subcollection_real
            newsImage.save(update_fields=["collection"])
    except Exception as e:
        raise RuntimeError(
            f"Failed to move images from collection '{parent_name}' to collection '{subcollection_name}'. Migration aborted. Error: {e}"
        )


# Moves any images in the "Home Page News Images" subcollection to the "News and
# Announcements" collection and deletes the subcollection "Home Page News Images"
# under the "News and Announcements" collection if it exists.
def delete_subcollection_under_parent(apps, schema_editor):
    Collection = apps.get_model("wagtailcore", "Collection")

    parent_name = "News and Announcements"
    subcollection_name = "Home Page News Images"

    try:
        Collection.objects.get(name=subcollection_name)
    except Collection.DoesNotExist:
        return  # Subcollection missing, nothing to delete

    from wagtail.models import Collection as RealCollection
    from wagtail.images.models import Image as RealImage

    try:
        parent_collection_real = RealCollection.objects.get(name=parent_name)
        if (
            not parent_collection_real.get_children()
            .filter(name=subcollection_name)
            .exists()
        ):
            raise RuntimeError(
                f"Subcollection '{subcollection_name}' is not a child of collection '{parent_name}'. Migration aborted."
            )
    except Exception as e:
        raise RuntimeError(
            f"Error while checking if subcollection '{subcollection_name}' is a child of collection '{parent_name}'. Migration aborted. Error: {e}"
        )

    # Move images in "Home Page News Images" subcollection to "News and Announcements"
    try:
        subcollection_real = RealCollection.objects.get(name=subcollection_name)
        for newsImage in RealImage.objects.filter(collection=subcollection_real):
            newsImage.collection = parent_collection_real
            newsImage.save(update_fields=["collection"])
    except Exception as e:
        raise RuntimeError(
            f"Failed to move images from collection '{subcollection_name}' to collection '{parent_name}'. Migration aborted. Error: {e}"
        )

    try:
        subcollection_real.delete()

    except Exception as e:
        raise RuntimeError(
            f"Could not delete subcollection '{subcollection_name}' under collection '{parent_name}'. Migration aborted. Error: {e}"
        )


class Migration(migrations.Migration):
    replaces = [
        ("home", "0093_auto_20260127_1550"),
        ("home", "0094_auto_20260127_1604"),
        ("home", "0095_alter_newsitem_image"),
        ("home", "0096_alter_newsitem_image"),
        ("home", "0097_alter_newsitem_image"),
        ("home", "0098_alter_newsitem_image"),
    ]

    dependencies = [
        ("home", "0092_alter_enhancedstandardpage_body"),
        ("taggit", "__latest__"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.RunPython(
            rename_collection_and_tag_to_new_name,
            rename_tag_and_collection_back_to_old_name,
        ),
        migrations.RunPython(
            create_subcollection_under_parent, delete_subcollection_under_parent
        ),
        migrations.AlterField(
            model_name="newsitem",
            name="image",
            field=models.ForeignKey(
                default=home.models.snippets.news_item.get_random_news_item_image_pk,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]
