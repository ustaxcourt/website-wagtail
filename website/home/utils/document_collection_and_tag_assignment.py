from home.data.document_tags_map import DOCUMENT_TAGS_MAP
from home.data.collection_sorting_order import COLLECTION_SORTING_ORDER
from home.data.role_tag_tags_map import ROLE_TAGS_TAG_MAP


def get_tags_for_document(doc_name):
    """
    Returns a list of tag names for the given document name.
    """
    initial_tags = DOCUMENT_TAGS_MAP.get(doc_name, {}).get("tags", [])

    for role_tag, associated_tags in ROLE_TAGS_TAG_MAP.items():
        if set(associated_tags) & set(initial_tags):
            initial_tags.append(role_tag)

    return initial_tags


def get_collection_for_document(doc_name, tags):
    """
    Returns the collection name for the given document name, based on tag priority.
    """
    for cname in COLLECTION_SORTING_ORDER:
        if cname in tags:
            return cname
    print(f"No collection exist for document '{doc_name}'")
    return None
