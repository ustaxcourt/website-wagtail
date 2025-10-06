from wagtail.documents.views.chooser import DocumentChooserViewSet


class SVGChooseView(DocumentChooserViewSet.choose_view_class):
    def get_object_list(self):
        queryset = super().get_object_list()

        return queryset.filter(file__iendswith=".svg")


class SVGChooserViewSet(DocumentChooserViewSet):
    choose_view_class = SVGChooseView


svg_chooser_viewset = SVGChooserViewSet("svg_chooser")
