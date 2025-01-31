from wagtail.models import Page, Site
from home.models import HomePage, HomePageEntry
from home.management.commands.pages.page_initializer import PageInitializer


class HomePageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        root = Page.objects.filter(depth=1).first()
        title = "Home"

        if not root:
            self.logger.write("Error: No root page found. Cannot create Home page.")
            return

        if HomePage.objects.filter(title=title).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        homepage = HomePage(
            title=title,
            draft_title="Home",
            slug=None,
            search_description="Official Site of the United States Tax Court",
            seo_title="United States Tax Court",
        )

        root.add_child(instance=homepage)
        homepage.save_revision().publish()

        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = homepage
            site.save()
            self.logger.write("Updated default site root to the new Home page.")

        # delete the wagtail generated page (it doesn't have the mixin)
        wagtailHome = Page.objects.filter(
            title="Welcome to your new Wagtail site!"
        ).first()
        if wagtailHome:
            self.logger.write("Deleting the default wagtail home")
            wagtailHome.delete()

        # set the new home page slug as home now that the wagtail default page is deleted
        homepage.slug = "home"
        homepage.save_revision().publish()

        HomePageEntry.objects.create(
            homepage=homepage,
            title="Remote Proceedings Info",
            body=(
                'Guidance on remote (virtual) proceedings and example videos of various procedures in a virtual courtroom can be found <a target="_blank" href="https://ustaxcourt.gov/zoomgov.html">here.</a>'
            ),
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="Closed for Holidays",
            body=(
                "In addition to observing the Christmas Day holiday on Wednesday, December 25, 2024, the Court will be closed on Tuesday, December 24, 2024. DAWSON will remain available for electronic access and electronic filing."
            ),
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="Chief Judge Kathleen Kerrigan announced today that Cathy Fung was sworn in as Judge of the United States Tax Court.",
            body=(
                'See the <a href="https://ustaxcourt.gov/resources/press/12132024.pdf" target="_blank">Press Release</a>.'
            ),
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="In Memory of Victor Lundy",
            body=(
                'Victor Lundy, architect of the Tax Court courthouse in Washington, D.C., died peacefully in his sleep on November 4, 2024. He was 101. The Tax Court will continue to be good stewards of this special building, a prime example of Mr. Lundy’s artistry in architecture. Learn more by watching <a href="https://www.youtube.com/watch?v=s6umLipF7-E" target="_blank">Victor Lundy: Sculptor of Space</a> or by visiting the <a href="https://www.gsa.gov/real-estate/gsa-properties/visiting-public-buildings/united-states-tax-court" target="_blank">GSA website</a>.'
            ),
        )
        HomePageEntry.objects.create(
            homepage=homepage,
            title="U.S. Tax Court Warning about Tax Scams",
            body=(
                "<p>Some people may receive unsolicited phone calls, emails, or other communications from individuals fraudulently claiming to be from the Tax Court, the Internal Revenue Service (IRS), or Federal government agencies and demanding immediate payment by money order, gift card, debit card, or other means to settle a tax debt.</p>"
                "<p>The Tax Court does not want anyone to be victimized by a tax scam. It is important that you know that the Tax Court will never do any of the following:</p>"
                "<ul>"
                "<li>call or email demanding payment of immigration visa application fees or taxes;</li>"
                "<li>call or email threatening arrest;</li>"
                "<li>call or email insisting that a specific payment method be used to pay Court fees, a tax debt, or requesting credit or debit card numbers over the phone.</li>"
                "</ul>"
                "<p>The IRS posts current <a href='https://www.irs.gov/newsroom/tax-scams-consumer-alerts' target='_blank'>warnings and alerts</a> about all types of tax scams on its website (including information about how to report tax scams). In addition, you may file a consumer complaint about a tax scam with the <a href='https://www.ftc.gov' target='_blank'>Federal Trade Commission</a> (FTC) or the <a href='https://www.fbi.gov' target='_blank'>Federal Bureau of Investigation</a> (FBI). These websites are maintained by the FTC and FBI—government agencies that are unrelated to the Tax Court.</p>"
                "<p>If you would like to verify that the communication you received is really from the Tax Court, please call the Court at (202) 521-0700.</p>"
            ),
        )

        self.logger.write("Successfully created the new Home page.")
