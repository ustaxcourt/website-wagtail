from wagtail import blocks


class PageSelectorBlock(blocks.StreamBlock):
    """
    Link target chooser (WAG-1440): pick an internal page or enter an
    external URL. Use with max_num=1 when a single target is expected.
    """

    internal_page = blocks.PageChooserBlock(label="Internal page")
    external_url = blocks.URLBlock(label="External page URL")
