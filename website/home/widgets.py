from wagtail.documents.widgets import AdminDocumentChooser


class AdminSVGChooser(AdminDocumentChooser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chooser_modal_url_name = "svg_chooser:choose"
