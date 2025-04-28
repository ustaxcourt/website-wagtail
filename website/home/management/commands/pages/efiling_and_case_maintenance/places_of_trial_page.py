from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import PlacesOfTrialPage

all_dpt_cities = [
    {
        "state": "Alabama",
        "cities": [
            {
                "name": "Birmingham",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Mobile",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Alaska",
        "cities": [
            {
                "name": "Anchorage",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Arizona",
        "cities": [
            {
                "name": "Phoenix",
                "note": "",
                "address": "Sandra Day O'Connor U.S. Courthouse 401 West Washington Street (85003)",
            },
        ],
    },
    {
        "state": "Arkansas",
        "cities": [
            {
                "name": "Little Rock",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "California",
        "cities": [
            {
                "name": "Fresno",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Los Angeles",
                "note": "",
                "address": "Edward R. Roybal Center & Federal Building 255 E. Temple Street (90012) Rooms 1167, 1174",
            },
            {
                "name": "San Diego",
                "note": "",
                "address": "Edward J. Schwartz Federal Building  880 Front Street, San Diego, CA 92101 Room 4228",
            },
            {
                "name": "San Francisco",
                "note": "",
                "address": "Phillip Burton Federal Building and U.S. Courthouse 450 Golden Gate Ave, San Francisco, CA 94102 Rooms 2-1408",
            },
        ],
    },
    {
        "state": "Colorado",
        "cities": [
            {
                "name": "Denver",
                "note": "",
                "address": "Byron Rogers Federal Building 1961 Stout St, Denver, CO 80294 Room C502",
            },
        ],
    },
    {
        "state": "Connecticut",
        "cities": [
            {
                "name": "Hartford",
                "note": "",
                "address": "Abraham A. Ribicoff Federal Building and U.S. Courthouse 450 Main Street Hartford, CT 06103 Room 619",
            },
        ],
    },
    {
        "state": "District of Columbia",
        "cities": [
            {
                "name": "Washington",
                "note": "",
                "address": "US Tax Court 400 2nd St NW, Washington, DC 20217",
            },
        ],
    },
    {
        "state": "Florida",
        "cities": [
            {
                "name": "Jacksonville",
                "note": "",
                "address": "US District Court Clerk 300 N Hogan St, Jacksonville, FL 32202 Room 6A",
            },
            {
                "name": "Miami",
                "note": "",
                "address": "Claude Pepper Federal Building 51 SW 1st Ave, Miami, FL 33130 Room 1524",
            },
            {
                "name": "Tallahassee",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Tampa",
                "note": "",
                "address": "Timberlake Federal Annex Building 501 E Polk St, Tampa, FL 33602 Room 1201",
            },
        ],
    },
    {
        "state": "Georgia",
        "cities": [
            {
                "name": "Atlanta",
                "note": "",
                "address": "Richard B. Russell Federal Building 75 Ted Turner Dr SW, Atlanta, GA 30303 Room 1136",
            },
        ],
    },
    {
        "state": "Hawaii",
        "cities": [
            {
                "name": "Honolulu",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Idaho",
        "cities": [
            {
                "name": "Boise",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Pocatello",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Illinois",
        "cities": [
            {
                "name": "Chicago",
                "note": "",
                "address": "John C. Kluczynski Federal Building 230 S Dearborn St, Chicago, IL 60604 Room 3908",
            },
            {
                "name": "Peoria",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Indiana",
        "cities": [
            {
                "name": "Indianapolis",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Iowa",
        "cities": [
            {
                "name": "Des Moines",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Kansas",
        "cities": [
            {
                "name": "Wichita",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Kentucky",
        "cities": [
            {
                "name": "Louisville",
                "note": "",
                "address": "Gene Snyder Federal Building 601 W Broadway # 630, Louisville, KY 40202 Room 440",
            },
        ],
    },
    {
        "state": "Louisiana",
        "cities": [
            {
                "name": "New Orleans",
                "note": "",
                "address": "U.S. Custom House 423 Canal St, New Orleans, LA 70130 Room 212",
            },
            {
                "name": "Shreveport",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Maine",
        "cities": [
            {
                "name": "Portland",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Maryland",
        "cities": [
            {
                "name": "Baltimore",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Massachusetts",
        "cities": [
            {
                "name": "Boston",
                "note": "",
                "address": "John W. McCormack Post Office and Courthouse 5 Post Office Square, Boston, MA 02109 Room 5",
            },
        ],
    },
    {
        "state": "Michigan",
        "cities": [
            {
                "name": "Detroit",
                "note": "",
                "address": "Theodore Levin United States Courthouse 231 W Lafayette Blvd, Detroit, MI 48226 Room 1069",
            },
        ],
    },
    {
        "state": "Minnesota",
        "cities": [
            {
                "name": "St Paul",
                "note": "",
                "address": "Warren E. Burger Federal Building 316 Robert St, St Paul, MN 55101 Room 444",
            },
        ],
    },
    {
        "state": "Mississippi",
        "cities": [
            {
                "name": "Jackson",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Missouri",
        "cities": [
            {
                "name": "Kansas City",
                "note": "",
                "address": "Charles E. Whittaker U.S. Courthouse 400 E 9th St, Kansas City, MO 64106 Room 1010",
            },
            {
                "name": "St Louis",
                "note": "",
                "address": "Thomas F. Eagleton United States Courthouse 111 S 10th St, St. Louis, MO 63102 Room 9.170",
            },
        ],
    },
    {
        "state": "Montana",
        "cities": [
            {
                "name": "Billings",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Helena",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Nebraska",
        "cities": [
            {
                "name": "Omaha",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Nevada",
        "cities": [
            {
                "name": "Las Vegas",
                "note": "",
                "address": "Foley Federal Building and U.S. Courthouse 300 S Las Vegas Blvd, Las Vegas, NV 89101 Room 4-400",
            },
            {
                "name": "Reno",
                "note": "",
                "address": "C. Clifton Young Federal Building 300 Booth St, Reno, NV 89509 Room 1161",
            },
        ],
    },
    {
        "state": "New Mexico",
        "cities": [
            {
                "name": "Albuquerque",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "New York",
        "cities": [
            {
                "name": "Albany",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Buffalo",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "New York City",
                "note": "",
                "address": "Jacob K. Javits Federal Building 26 Federal Plaza, New York, NY 10278 Rooms 206",
            },
            {
                "name": "Syracuse",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "North Carolina",
        "cities": [
            {
                "name": "Winston-Salem",
                "note": "",
                "address": "Hiram H. Ward Federal Building 229237 N Main St, Winston-Salem, NC 27101 Room 847",
            },
        ],
    },
    {
        "state": "North Dakota",
        "cities": [
            {
                "name": "Bismark",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Ohio",
        "cities": [
            {
                "name": "Cincinnati",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Cleveland",
                "note": "",
                "address": "Anthony J. Celebrezze Federal Building 1240 E 9th St, Cleveland, OH 44199 Room 3013",
            },
            {
                "name": "Columbus",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Oklahoma",
        "cities": [
            {
                "name": "Oklahoma City",
                "note": "",
                "address": "William J. Holloway Jr. U.S. Courthouse 200 NW 4th St, Oklahoma City, OK 73102 Room 402",
            },
        ],
    },
    {
        "state": "Oregon",
        "cities": [
            {
                "name": "Portland",
                "note": " No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Pennsylvania",
        "cities": [
            {
                "name": "Philadelphia",
                "note": "",
                "address": "The United States Custom House 200 Chestnut St, Philadelphia, PA 19106 Room 300",
            },
            {
                "name": "Pittsburgh",
                "note": "",
                "address": "William S. Moorhead Federal Building 1000 Liberty Ave, Pittsburgh, PA 15222 Room 1108",
            },
        ],
    },
    {
        "state": "South Carolina",
        "cities": [
            {
                "name": "Columbia",
                "note": "",
                "address": "Strom Thurmond Federal Building 1835 Assembly St, Columbia, SC 29201 Room 250",
            },
        ],
    },
    {
        "state": "South Dakota",
        "cities": [
            {
                "name": "Aberdeen",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Tennessee",
        "cities": [
            {
                "name": "Knoxville",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Memphis",
                "note": "",
                "address": "Odell Horton Federal Building 167 N Main St, Memphis, TN 38103 Room 1006",
            },
            {
                "name": "Nashville",
                "note": "",
                "address": "Estes Kefauver Federal Building 801 Broadway, Nashville, TN 37203 Room C650",
            },
        ],
    },
    {
        "state": "Texas",
        "cities": [
            {
                "name": "Dallas",
                "note": "",
                "address": "Earle Cabell Fed. Bldg. & U.S. Cthse. 1100 Commerce Street, 75242 Room 726",
            },
            {
                "name": "El Paso",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Houston",
                "note": "",
                "address": "Casey U.S. Courthouse 515 Rusk Street, 77002 Room 7006",
            },
            {
                "name": "Lubbock",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "San Antonio",
                "note": "",
                "address": "Hipolito F. Garcia Federal Building & Courthouse 615 E. Houston Street, 78206 Room 371",
            },
        ],
    },
    {
        "state": "Utah",
        "cities": [
            {
                "name": "Salt Lake City",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Vermont",
        "cities": [
            {
                "name": "Burlington",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Virginia",
        "cities": [
            {
                "name": "Richmond",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
            {
                "name": "Roanoke",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Washington",
        "cities": [
            {
                "name": "Seattle",
                "note": "",
                "address": "Nakamura U.S. Courthouse 1010 5th Avenue, 98104 Room 4",
            },
            {
                "name": "Spokane",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "West Virginia",
        "cities": [
            {
                "name": "Charleston",
                "note": "No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
    {
        "state": "Wisconsin",
        "cities": [
            {
                "name": "Milwaukee",
                "note": "",
                "address": "Federal Building & U.S. Courthouse 517 E. Wisconsin Avenue 53202 Room 498",
            },
        ],
    },
    {
        "state": "Wyoming",
        "cities": [
            {
                "name": "Cheyenne",
                "note": "Trials of small tax cases only. No permanent courtroom. See notice of trial for address.",
                "address": "",
            },
        ],
    },
]


class PlacesOfTrialPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dpt-cities"
        title = "Places Of Trial"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        places_of_trial_data = [
            {
                "type": "state",
                "value": {
                    "state": state_data["state"],
                    "cities": state_data["cities"],
                },
            }
            for state_data in all_dpt_cities
        ]

        places_of_trial_page = PlacesOfTrialPage(
            title=title,
            slug=slug,
            seo_title=title,
            search_description="Press Releases",
            places_of_trial=places_of_trial_data,
            body=[
                {
                    "type": "alert_message",
                    "value": {
                        "message": "<strong>Addresses are trial locations only</strong> <br>Always address mail to: United States Tax Court, 400 Second Street NW, Washington, DC 20217-0002.",
                    },
                }
            ],
            show_in_menus=True,
        )

        home_page.add_child(instance=places_of_trial_page)
        places_of_trial_page.save_revision().publish()
        self.logger.write(f"'{title}' page created and published.")
