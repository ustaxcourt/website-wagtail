from home.management.commands.pages.page_initializer import PageInitializer

ropp_tc_reports_docs = [
    "vol-060.pdf",
    "vol-064.pdf",
    "vol-068.pdf",
    "vol-071.pdf",
    "vol-077.pdf",
    "vol-079.pdf",
    "vol-081.pdf",
    "vol-082.pdf",
    "vol-085.pdf",
    "vol-087.pdf",
    "vol-090.pdf",
    "vol-093.pdf",
    "vol-109.pdf",
    "vol-120.pdf",
    "vol-125.pdf",
    "vol-128.pdf",
    "vol-130.pdf",
    "vol-134.pdf",
    "vol-135.pdf",
    "vol-136.pdf",
    "vol-139.pdf",
    "vol-153.pdf",
    "vol-154.pdf",
    "vol-155.pdf",
]


class UnlistedFiles(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        for doc in ropp_tc_reports_docs:
            _ = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc,
                title=doc,
                collection="Unlisted Documents",
            )
