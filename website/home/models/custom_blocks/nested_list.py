from wagtail import blocks
from wagtail.images.blocks import ImageBlock

LIST_TYPE_CHOICES = [
    ("ordered", "Ordered List"),
    ("unordered", "Unordered List"),
]

LIST_TYPE_BLOCK = blocks.ChoiceBlock(
    choices=LIST_TYPE_CHOICES, required=False, default="ordered"
)


def create_nested_list_block(max_depth=5, current_depth=1):
    """
    Creates a nested list block structure with configurable depth.

    Args:
        max_depth (int): Maximum nesting depth allowed (default: 4)
        current_depth (int): Current depth in the recursion (used internally)

    Returns:
        blocks.StructBlock: A Wagtail block structure for nested lists
    """
    # Base structure that's common at all levels
    list_item_blocks = [
        ("text", blocks.RichTextBlock(required=False)),
        ("image", ImageBlock(required=False)),
    ]

    # Add nested_list field if we haven't reached max depth
    if current_depth < max_depth:
        list_item_blocks.append(
            (
                "nested_list",
                blocks.ListBlock(
                    create_nested_list_block(max_depth, current_depth + 1),
                    default=[],
                ),
            )
        )

    return blocks.StructBlock(
        [
            ("list_type", LIST_TYPE_BLOCK),
            (
                "items",
                blocks.ListBlock(
                    blocks.StructBlock(list_item_blocks, required=False),
                    default=[],
                ),
            ),
        ],
        required=False,
    )
