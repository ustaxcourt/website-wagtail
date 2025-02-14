from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    NavigationRibbon,
    EnhancedStandardPage,
)


class ZoomgovProceedingPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "zoomgov_zoomgov_proceedings"
        title = "Zoomgov Proceedings"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            Page.objects.get(slug=slug).delete()

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Zoomgov Proceedings Ribbon"
        ).first()

        questions = [
            {
                "question": "What should I do the day of my Zoomgov proceeding?",
                "answer": """<ul>
            <li>Log on to your proceeding at least 30 minutes early to ensure that you are able to connect.</li>
            <li>If you have difficulty connecting by computer, smartphone, or tablet, call the telephone access number provided with your Meeting ID and Passcode.</li>
            <li>Make sure your device is fully charged, and, if you are using a phone, that it has plenty of minutes. It’s best to connect to a power source. If you cannot, have a power cord and outlet nearby, just in case.</li>
            <li>Have a pen and paper handy in case you need to write things down.</li>
            <li>Have copies of any document that you sent to the Court, or to the other party, ready to look at during the proceeding.</li>
            </ul>""",
                "anchortag": "START1",
            },
            {
                "question": "Who can be in the Zoomgov courtroom during a proceeding?",
                "answer": "The parties (IRS and petitioners), counsel (attorneys, practitioners admitted to practice before the Court, and pro bono representatives), testifying experts, witnesses (while testifying), and others with the Court’s permission will be permitted in the Zoomgov courtroom.",
                "anchortag": "START2",
            },
            {
                "question": "What happens when I join the proceeding?",
                "answer": """<ul>
            <li>When you first join the proceeding you will be placed into a waiting room. If you connected by computer, smartphone, or tablet, you will see a message that says “Please wait, the meeting host will let you in soon”.</li>
            <li>When the Court is ready for you, the Trial Clerk will admit you to the Zoomgov courtroom and provide further information.</li>
            </ul>""",
                "anchortag": "START3",
            },
            {
                "question": "Do I have to be on video?",
                "answer": """<ul>
            <li>All participants should be connected by video. You and the Judge and the other party will be able to see each other and it will be easier to follow what is happening.</li>
            <li>If you have technology limitations, inform the Judge as soon as possible.</li>
            <li>To see the other participants, choose “gallery view” if connected to Zoomgov on your computer, smartphone, or tablet.</li>
            <li>To see just the person speaking, choose “speaker view” if connected to Zoomgov on your computer, smartphone, or tablet.</li>
            </ul>""",
                "anchortag": "START4",
            },
            {
                "question": "Will my telephone number be visible if I call in?",
                "answer": "No, your telephone number will not be visible. The Trial Clerk will rename your participant screen according to standard protocols.",
                "anchortag": "START5",
            },
            {
                "question": "Does the Court have any tips for participating in a Zoomgov proceeding?",
                "answer": """<ul>
             <li>Yes. Mute your microphone when you are not speaking. Even background noise can be heard.</li>
             <li>Make sure the camera is at eye level. You may want to put your device on a stack of books so you can be hands-free and look directly at the camera while talking.</li>
             <li>Don’t leave the proceeding, even for a short time, unless you have been excused by the Judge or Trial Clerk.</li>
             <li>Avoid moving around with your device during the proceeding.</li>
             <li>Wait for the Judge to call on you. Raise your hand if you need to speak to the Judge or Trial Clerk.</li>
             <li>Avoid speaking to someone not in the proceeding.</li>
             <li>Do not speak over other participants.</li>
             </ul>""",
                "anchortag": "START6",
            },
            {
                "question": "What if I get disconnected?",
                "answer": """<ul>
             <li>If you get disconnected, call into the proceeding using the dial-in number provided in your notice.</li>
             <li>If you still have difficulty connecting, call the Clerk’s Office at (202) 521-0700 for assistance</li>
             </ul>""",
                "anchortag": "START7",
            },
            {
                "question": "Can I record the Zoomgov proceeding?",
                "answer": """<ul>
             <li>No. The Court’s standing rules prohibit your making video or audio recordings.</li>
             <li>All proceedings are being recorded by the Court, and transcripts may be ordered from the Court Reporter.</li>
             </ul>""",
                "anchortag": "START8",
            },
            {
                "question": "What if I want to speak with my representative (or client) privately?",
                "answer": "Tell the Judge that you would like to speak with your representative (or client) privately. The Judge may excuse you to a private breakout room on Zoomgov, or provide further direction as appropriate.",
                "anchortag": "START9",
            },
            {
                "question": "What is a breakout room?",
                "answer": """<ul>
             <li>Zoomgov breakout rooms are separate meeting spaces, apart from the main Zoomgov courtroom. They are private, and only the participants in the room can see or hear what is going on in them.</li>
             <li>Discussions in the breakout rooms are not recorded.</li>
             <li>Discussions in the breakout rooms are not considered part of the official proceeding.</li>
             </ul>""",
                "anchortag": "START10",
            },
            {
                "question": "Will the Court allow low income taxpayer clinics and calendar call programs to participate in Zoomgov proceedings?",
                "answer": """<ul>
             <li>Yes. Please arrive to the virtual proceeding at least 60 minutes early if you would like to speak with a volunteer attorney about your case.</li>
             <li>You can also reach out to a low income taxpayer clinic or calendar call pro bono program as soon as you are issued your notice setting the case for trial. A list of participating programs can be found on the Court’s website at
              <strong><a href="https://www.ustaxcourt.gov/" target="_blank" title="United States Tax Court">www.ustaxcourt.gov.</a></strong>.</li>
             </ul>""",
                "anchortag": "START11",
            },
            {
                "question": "How do I connect to a Zoomgov proceeding if I am a member of the general public or the press?",
                "answer": """<ul>
             <li>Prior to each trial session, a link to an audio stream of the Zoomgov courtroom will be available on the Court’s website,
             <strong><a href="https://www.ustaxcourt.gov/" target="_blank" title="United States Tax Court">www.ustaxcourt.gov.</a></strong>.</li>
             <li>Audio will be streamed only while the Court is in session.</li>
             <li>Audio recordings will not be archived.</li>
             <li>The Court’s standing rules prohibit you from recording the proceedings.</li>
             </ul>""",
                "anchortag": "START12",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Zoomgov Proceedings",
                body=[
                    {"type": "heading", "value": "Zoomgov FAQs: Zoomgov Proceedings"},
                    {"type": "questionanswers", "value": questions},
                ],
                show_in_menus=False,
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
