from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    NavigationRibbon,
    EnhancedStandardPage,
)


class GettingReadyPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "zoomgov-getting-ready"
        title = "Zoomgov Proceedings"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Zoomgov Proceedings Ribbon"
        ).first()

        questions = [
            {
                "question": "I just got my notice. Should I do anything ahead of time to get ready?",
                "answer": """<ul>
            <li>Make sure you have the Zoom “client” installed on your computer. It’s a small, free application file to run the program. You can download it here: <strong><a href="https://zoom.us/download" title="Zoom Download">https://zoom.us/download</a></strong>.</li>
            <li>If you plan to use a smartphone or tablet, you will need to install the latest version of the Zoom Cloud Meetings app. The app is available for free on both the iTunes and Google Play stores.</li>
            <li>You can test the Zoomgov audio and video on your device before your trial or hearing date. Visit <strong><a href="https://zoom.us/test" title="Zoom Test">https://zoom.us/test</a></strong> for more information.</li>
            </ul>""",
                "anchortag": "START1",
            },
            {
                "question": "Is there a way to do a test before my actual hearing?",
                "answer": """<ul>
            <li>Yes. We strongly encourage you to test the Zoomgov audio and video on your computer, smartphone, or tablet before your trial or hearing date. Visit <strong><a href="https://zoom.us/test" title="Zoom Test">https://zoom.us/test</a></strong> for more information.</li>
            <li>Please join your proceeding at least 30 minutes prior to its scheduled start time so you can address any last-minute technical issues.</li>
            </ul>""",
                "anchortag": "START2",
            },
            {
                "question": "Do I need a computer to participate in a Zoomgov proceeding?",
                "answer": """<ul>
            <li>No. You can connect to a Zoomgov proceeding by smartphone or tablet, or by a regular telephone.</li>
            <li>Your computer will need a video camera, speakers, and a microphone to if you plan to participate by computer.</li>
            <li>For more information on how to connect to a Zoomgov proceeding, visit <strong><a href="https://zoom.us" title="Zoom">www.zoom.us</a></strong>.</li>
            </ul>""",
                "anchortag": "START3",
            },
            {
                "question": "Do I need special software to participate in a Zoomgov proceeding?",
                "answer": """<ul>
            <li>The first time you use Zoomgov from a computer, you will be asked to download a small, free application file to run the program. You can download it here: <strong><a href="https://zoom.us/download" title="Zoom Download">https://zoom.us/download</a></strong>.</li>
            <li>If you are using a smartphone or tablet, you will need the latest version of the Zoom Cloud Meetings app. The app is available for free on both the iTunes and Google Play stores.</li>
            </ul>""",
                "anchortag": "START4",
            },
            {
                "question": "Do I need special technology to participate in a Zoomgov proceeding?",
                "answer": """<ul>
             <li>No, but it’s helpful if you make the most of the technology you do have.</li>
             <li>If you use WiFi, make sure you’re in close range and that you are not sharing bandwidth with too many other devices.</li>
             <li>If you can, use a good quality headset (headphones with mic) to help ensure you can be heard, and that you can hear others as clearly as possible.</li>
             <li>Know how to manage the volume so you can hear all of the participants.</li>
             <li>Know how to adjust the brightness of your screen so you can see well.</li>
             </ul>""",
                "anchortag": "START5",
            },
            {
                "question": "Does it matter where I am when I participate in a Zoomgov proceeding?",
                "answer": """<ul>
             <li>Yes. Be somewhere with minimal distractions where you are able to talk and to listen.</li>
             <li>Your picture quality will be best if you are inside, with good lighting.</li>
             <li>Avoid messy areas.</li>
             <li>Try to have a plain background.</li>
             <li>Avoid windows, plants, lamps, or anything directly behind your head.</li>
             <li>We do not recommend the use of a virtual background without a green screen.</li>
             </ul>""",
                "anchortag": "START6",
            },
            {
                "question": "How do I connect to a Zoomgov proceeding if I am a participant?",
                "answer": """<ul>
             <li>You can connect by computer, by smartphone or tablet, or by regular telephone.</li>
             <li>On a computer, go to <strong><a href="https://zoomgov.com/" title="Zoomgov">https://zoomgov.com/</a></strong> and click “Join a Meeting”, and enter the Meeting ID and Passcode.</li>
             <li>On a smartphone or tablet, use the Zoom Cloud Meetings app and click “Join”, and enter the Meeting ID and Passcode.</li>
             <li>If you do not have access to a computer or smartphone, use a telephone to dial the number provided and enter the Meeting ID and Passcode when prompted.</li>
             <li>For more information on how Zoomgov and Zoom work, visit www.zoom.us and the quickstart guide at <strong><a href="https://support.zoom.us/hc/en-us/articles/360034967471- Quick-start-guide-for-new-users" title="Zoom Quick Start">https://support.zoom.us/hc/en-us/articles/360034967471- Quick-start-guide-for-new-users</a></strong>.</li>
             </ul>""",
                "anchortag": "START7",
            },
            {
                "question": "Where is my meeting ID and Passcode?",
                "answer": "The Meeting ID and Passcode are on your notice setting the case for trial or setting the matter for hearing.",
                "anchortag": "START8",
            },
            {
                "question": "What if I lost my notice setting the case for trial?",
                "answer": "If you cannot find your Zoomgov information, please contact the Clerk’s Office at (202) 521-0700.",
                "anchortag": "START9",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Getting Ready",
                body=[
                    {"type": "h2", "value": "Zoomgov FAQs: Getting Ready"},
                    {"type": "questionanswers", "value": questions},
                ],
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
