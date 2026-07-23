from wagtail import blocks
from wagtail.images.blocks import ImageBlock

LIST_TYPE_CHOICES = [
    ("ordered", "Ordered List"),
    ("unordered", "Unordered List"),
    ("checkbox", "Checkbox List"),
    ("checkbox_with_subtext", "Checkbox with Subtext"),
]

LIST_TYPE_BLOCK = blocks.ChoiceBlock(
    choices=LIST_TYPE_CHOICES, required=False, default="ordered"
)


class NestedListBlock(blocks.StructBlock):
    def __init__(self, item_block, *args, **kwargs):
        super().__init__(
            [
                ("list_type", LIST_TYPE_BLOCK),
                ("items", blocks.ListBlock(item_block, default=[])),
            ],
            *args,
            **kwargs,
        )

    def clean(self, value):
        cleaned_data = super().clean(value)

        if cleaned_data.get("list_type") != "checkbox_with_subtext":
            subtext_block = self.child_blocks["items"].child_block.child_blocks[
                "subtext"
            ]
            empty_subtext = subtext_block.to_python("")
            for item in cleaned_data.get("items", []):
                if "subtext" in item:
                    item["subtext"] = empty_subtext

        if cleaned_data.get("list_type") not in ("checkbox", "checkbox_with_subtext"):
            for item in cleaned_data.get("items", []):
                if "disabled" in item:
                    item["disabled"] = False

        return cleaned_data


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
        ("subtext", blocks.RichTextBlock(required=False)),
        (
            "disabled",
            blocks.BooleanBlock(required=False, default=False),
        ),
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

    return NestedListBlock(
        blocks.StructBlock(list_item_blocks, required=False),
        required=False,
    )
