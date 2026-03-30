from wagtail import blocks


class ChatbotBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        required=False,
        default="Ask a Question",
        help_text="Heading displayed above the chat widget",
    )
    placeholder = blocks.CharBlock(
        required=False,
        default="e.g. How do I file a petition?",
        help_text="Placeholder text shown in the input field",
    )

    class Meta:
        label = "AI Chat Widget (Bedrock)"
        icon = "comment"
