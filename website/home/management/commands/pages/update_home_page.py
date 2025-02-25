from home.models import HomePage, HomePageEntry
from home.management.commands.pages.page_initializer import PageInitializer


class HomePageUpdate(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        pass

    def update(self):
        title = "Home"

        if HomePage.objects.filter(title=title).exists():
            self.logger.write(
                f"- {title} page already exists. Updating the existing page."
            )
            homepage = HomePage.objects.get(title=title)
        else:
            self.logger.write("Page does not exist. Nothing to update. STOPPING.")
            return

        remote_proceeding_entry = HomePageEntry.objects.filter(
            homepage=homepage, title="Remote Proceedings Info"
        )

        if remote_proceeding_entry.exists():
            remote_proceeding_entry.update(
                body=(
                    'Guidance on remote (virtual) proceedings and example videos of various procedures in a virtual courtroom can be found <a href="/zoomgov">here.</a>'
                )
            )
        else:
            self.logger.write(
                "Remote Proceedings Info entry does not exist. Nothing to update."
            )

        self.logger.write("Successfully updated the new Home page.")
