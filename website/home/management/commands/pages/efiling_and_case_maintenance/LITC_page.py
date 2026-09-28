from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import LITCPage
from home.models.utils.execute_script import ExecuteScript
import logging

logger = logging.getLogger(__name__)


all_litc_clinics = [
    {
        "state": "Alabama",
        "cities": [
            {
                "name": "Birmingham",
                "clinics": [
                    {
                        "name": "Legal Services Alabama LITC",
                        "address": "P.O. Box 20728, Montgomery, AL 36120",
                        "phone": "866-456-4995",
                        "website": "https://www.legalservicesalabama.org",
                        "small_case_procedures_only": False,
                    }
                ],
            },
            {
                "name": "Mobile",
                "clinics": [
                    {
                        "name": "Legal Services Alabama LITC",
                        "address": "P.O. Box 20728, Montgomery, AL 36120",
                        "phone": "866-456-4995",
                        "website": "https://www.legalservicesalabama.org",
                        "small_case_procedures_only": False,
                    }
                ],
            },
        ],
    },
    {
        "state": "Alaska",
        "cities": [
            {
                "name": "Anchorage",
                "clinics": [
                    {
                        "name": "Alaska Business Development Center, Inc.",
                        "address": "840 K Street, Suite 202, Anchorage, AL 99501",
                        "email": "info@abdc.org",
                        "phone": "907-562-0335",
                        "website": "https://www.abdc.org",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Arizona",
        "cities": [
            {
                "name": "Phoenix",
                "clinics": [
                    {
                        "name": "Community Legal Services",
                        "address": "305 S 2nd Abe, Phoenix, AZ 85003",
                        "email": "info@clsaz.org",
                        "phone": "602-258-3434",
                        "website": "https://www.clsaz.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Catholic Community Services of Southern AZ",
                        "address": "975 N. Alvernon Way, Tucson, AZ 85712",
                        "phone": "520-416-4763",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Arkansas",
        "cities": [
            {
                "name": "Little Rock",
                "clinics": [
                    {
                        "name": "Legal Aid of Arkansas, Inc.",
                        "address": "1200 Henryetta Street, Springdale, AR 72762",
                        "phone": "870-732-6373",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "University of Arkansas at Little Rock Bowen School of Law",
                        "address": "1201 McMath Avenue, Little Rock, AR 72202",
                        "phone": "501-916-5492",
                        "website": "",
                        "small_case_procedures_only": True,
                    },
                ],
            }
        ],
    },
    {
        "state": "California",
        "cities": [
            {
                "name": "Fresno",
                "clinics": [
                    {
                        "name": "Cal Poly Orfalea School of Business",
                        "address": "1 Grand Avenue, Building 3, Room 107, San Luis Obispo, CA 93406",
                        "email": "litc@calpoly.edu",
                        "phone": "805-756-2951",
                        "website": "",
                        "small_case_procedures_only": True,
                    }
                ],
            },
            {
                "name": "Los Angeles",
                "clinics": [
                    {
                        "name": "Bet Tzedek Legal Services Tax Clinic",
                        "address": "3250 Wilshire Blvd., 13th Fl., Los Angeles, CA 90010",
                        "phone": "323-939-0506",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Bookstein Tax Clinic, California State University, Northridge Nazarian College of Business &Econ.",
                        "address": "18111 Nordhoff Street, Northridge, CA 91330",
                        "phone": "818-677-3688",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Chapman University Fowler School of Law",
                        "address": "One University Drive, Orange, CA 92886",
                        "phone": "714-628-2535",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Koreatown Youth & Community Center",
                        "address": "3727 West 6th Street, Suite 410, Los Angeles, CA 90020",
                        "phone": "213-232-2700",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Inland Counties Legal Services",
                        "address": "1040 Iowa Ave., Suite 109, Riverside, CA 92507",
                        "phone": "888-245-4257",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Los Angeles County Bar Tax Court Pro Se Program",
                        "address": "",
                        "phone": "",
                        "website": "https://www.taxcourtprose.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Pepperdine University Legal Aid Clinic",
                        "address": "545 S. San Pedro Street, Los Angeles, CA 90013",
                        "phone": "213-673-4831",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Public Law Center Federal Tax Clinic",
                        "address": "601 W. Civic Center Dr., Santa Ana, CA 92701",
                        "email": "taxclinic@publiclawcenter.org",
                        "phone": "714-541-1010, ext. 340",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Taxpayers Help Center, Inc.",
                        "address": "9029 Reseda Blvd., Suite 209, Northridge, CA 91344",
                        "phone": "818-366-0111",
                        "website": "https://www.taxpayershelpcenter.com",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "San Diego",
                "clinics": [
                    {
                        "name": "University of San Diego School of Law Tax Clinic",
                        "address": "5998 Alcalá Park, BA 303, San Diego, CA 92110",
                        "phone": "619-260-7470",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Aid Society of San Diego, Inc.",
                        "address": "1764 San Diego Avenue, Suite 100, San Diego, CA 92110",
                        "phone": "877-534-2524",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Inland Counties Legal Services",
                        "address": "1040 Iowa Ave., Suite 109, Riverside, CA 92507",
                        "phone": "888-245-4257",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "San Francisco",
                "clinics": [
                    {
                        "name": "Justice and Diversity Center",
                        "address": "201 Mission Street, Suite 400, San Francisco, CA 94105",
                        "phone": "415-782-8977",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Chinese Newcomers Service Center",
                        "address": "777 Stockton Street, #104, San Francisco, CA 94108",
                        "phone": "415-421-2111",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "UC Law Low-Income Taxpayer Clinic",
                        "address": "200 McAllister Street, San Francisco, CA 94102",
                        "email": "litc@uclawsf.edu",
                        "phone": "415-703-8287",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
        ],
    },
    {
        "state": "Colorado",
        "cities": [
            {
                "name": "Denver",
                "clinics": [
                    {
                        "name": "University of Denver Graduate Tax Program",
                        "address": "2255 East Evans Avenue, #390, Denver, CO 80208",
                        "email": "litc@law.du.edu",
                        "phone": "303-871-6331",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Colorado Legal Services",
                        "address": "1905 Sherman St. #400, Denver, CO 80203",
                        "phone": "303-837-1313",
                        "website": "https://www.applyonlinecls.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Denver Asset Building Coalition",
                        "address": "2475 W. 26th Ave., Denver, CO 80211",
                        "email": "intake@denverabc.org",
                        "phone": "",
                        "website": "",
                        "small_case_procedures_only": True,
                    },
                ],
            }
        ],
    },
    {
        "state": "Connecticut",
        "cities": [
            {
                "name": "Hartford",
                "clinics": [
                    {
                        "name": "University of Connecticut School of Law",
                        "address": "65 Elizabeth Street, Hartford, CT 06105",
                        "phone": "860-570-5165",
                        "website": "https://www.law.uconn.edu/academics/clinical-education/tax-clinic",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Quinnipiac University School of Law",
                        "address": "275 Mt. Carmel Avenue, Hamden, CT 06518",
                        "phone": "203-582-3238",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Rhode Island Legal Services, Inc.",
                        "address": "56 Pine Street, 4th Floor, Providence, RI 02903",
                        "phone": "401-274-2652",
                        "website": "https://www.lowincometaxclinic.org",
                        "small_case_procedures_only": True,
                    },
                ],
            }
        ],
    },
    {
        "state": "Delaware",
        "cities": [
            {
                "name": "Philadelphia",
                "clinics": [
                    {
                        "name": "Delaware Community Reinvestment Action Council, Inc.",
                        "address": "One East Laurel Street Georgetown, Delaware 19947 and 600 South Harrison Street Wilmington, DE 19805",
                        "phone": "302-690-5000 / 302-393-1607 (Spanish line)",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "District of Columbia",
        "cities": [
            {
                "name": "Washington",
                "clinics": [
                    {
                        "name": "The American University-WCL Janet R. Spragens Federal Tax Clinic",
                        "address": "4300 Nebraska Avenue, N.W., Suite Y265, Washington, D.C. 20016",
                        "phone": "202-274-4144",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Services of Northern Virginia",
                        "address": "10700 Page Avenue, Suite 100, Fairfax, VA 22030",
                        "phone": "703-778-6800",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Washington D.C. Center for Public Interest Tax Law",
                        "address": "1111 Pennsylvania Ave, NW, Washington, D.C. 20004",
                        "phone": "202-739-3272",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "University of the District of Columbia David A. Clarke School of Law",
                        "address": "4340 Connecticut Ave, NW, Suite 342, Washington, D.C. 20008",
                        "phone": "202-274-6683",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Florida",
        "cities": [
            {
                "name": "Jacksonville",
                "clinics": [
                    {
                        "name": "University of Florida Low-Income Taxpayer Clinic",
                        "address": "309 Village Drive, PO Box 117626, Gainesville, FL 32611-7626",
                        "phone": "352-273-0810",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
            {
                "name": "Tallahassee",
                "clinics": [
                    {
                        "name": "Legal Services of North Florida",
                        "address": "2119 Delta Blvd., Tallahassee, FL 32309",
                        "phone": "850-385-9007",
                        "website": "https://www.LSNF.org",
                        "small_case_procedures_only": False,
                    }
                ],
            },
            {
                "name": "Tampa",
                "clinics": [
                    {
                        "name": "Bay Area Legal Services, Inc.",
                        "address": "1302 N 19th St., Suite 400, Tampa, FL 33605",
                        "phone": "813-232-1343 / 800-625-2257 / 800-955-8771/TTY",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "GulfCoast Legal Services",
                        "address": "501 First Ave N, Suite 420, St. Petersburg, FL 33701",
                        "phone": "727-821-0726 / 800-230-5920",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Miami",
                "clinics": [
                    {
                        "name": "Legal Aid Service of Broward County",
                        "address": "491 North State Road 7, Plantation, FL 33317",
                        "phone": "954-736-2477",
                        "website": "https://www.browardlegalaid.org",
                        "small_case_procedures_only": True,
                    },
                    {
                        "name": "Legal Aid Society of Palm Beach County",
                        "address": "423 Fern Street, Suite 200, West Palm Beach, FL 33401",
                        "phone": "561-655-8944",
                        "website": "https://www.legalaiedpbc.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Services of Greater Miami, Inc. Low Income Taxpayer Clinic",
                        "address": "4343 West Flagler Street, Suite #100, Miami, FL 33134",
                        "phone": "305-576-0080",
                        "website": "https://www.Legalservicesmiami.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "St. Thomas University School of Law",
                        "address": "16401 NW 37th Avenue, Miami Gardens, FL 33054",
                        "phone": "305-474-2453",
                        "website": "https://www.stu.edu/law/index.html",
                        "small_case_procedures_only": True,
                    },
                ],
            },
        ],
    },
    {
        "state": "Georgia",
        "cities": [
            {
                "name": "Atlanta",
                "clinics": [
                    {
                        "name": "Georgia State University College of Law Philip C. Cook Low Income Taxpayer Clinic",
                        "address": "85 Park Place NE, Atlanta, GA 30303",
                        "email": "taxclinic@gsu.edu",
                        "phone": "404-413-9230",
                        "website": "https://www.law.gsu.edu/tax",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Georgia Tax Clinic",
                        "address": "234 Luckie Street, Lawrenceville, GA 30046",
                        "phone": "678-646-5661",
                        "website": "https://www.gataxclinic.com",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Hawaii",
        "cities": [
            {
                "name": "Honolulu",
                "clinics": [
                    {
                        "name": "Hawaii Federal Tax Clinic",
                        "address": "1001 Bishop Street, Honolulu, Hawaii 96813",
                        "phone": "808-202-2274",
                        "website": "https://www.hawaiifedtax.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "University of Washington School of Law Clinic",
                        "address": "William H. Gates Hall, Suite 265, Seattle, WA 98145",
                        "phone": "206-685-6805 / 866-866-0158 (toll-free)",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Idaho",
        "cities": [
            {
                "name": "Boise",
                "clinics": [
                    {
                        "name": "University of Idaho",
                        "address": "501 W. Front Street, Boise, Idaho 83702",
                        "phone": "208-364-6166",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Illinois",
        "cities": [
            {
                "name": "Chicago",
                "clinics": [
                    {
                        "name": "Legal Aid Chicago",
                        "address": "120 S. La Salle St., #900, Chicago, IL 60603",
                        "phone": "312-341-1070",
                        "website": "https://www.legalaidchicago.org/get-help/legal-aid-chicago-clinics/",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Loyola University Chicago School of Law",
                        "address": "25 E. Pearson, Suite 1005, Chicago, IL 60611",
                        "phone": "312-915-7176",
                        "website": "https://www.luc.edu/law/taxclinic",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Ladder Up Tax Clinic",
                        "address": "350 N. Orleans Street Suite C2-100, Chicago, IL 60654",
                        "phone": "312-630-0267",
                        "website": "https://www.goladderup.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Prairie State Legal Services",
                        "address": "31W001W. North Avenue, Suite 200, West Chicago, IL 60185",
                        "phone": "855-829-7757",
                        "website": "https://www.pslegal.org/litc",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Peoria",
                "clinics": [
                    {
                        "name": "Prairie State Legal Services",
                        "address": "31W001W. North Avenue, Suite 200, West Chicago, IL 60185",
                        "phone": "855-829-7757",
                        "website": "https://www.pslegal.org/litc",
                        "small_case_procedures_only": False,
                    }
                ],
            },
        ],
    },
    {
        "state": "Indiana",
        "cities": [
            {
                "name": "Indianapolis",
                "clinics": [
                    {
                        "name": "Indiana Legal Services, Inc.",
                        "address": "214 S. College Avenue, Bloomington, IN 47404",
                        "phone": "812-961-0011",
                        "website": "https://www.indianalegalservices.org/litc",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Neighborhood Christian Legal Clinic",
                        "address": "3333 North Meridian Street, Suite 201, Indianapolis, IN 46208",
                        "phone": "317-429-4151",
                        "website": "https://www.nclegalclinic.org",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Iowa",
        "cities": [
            {
                "name": "Des Moines",
                "clinics": [
                    {
                        "name": "Iowa Legal Aid LITC",
                        "address": "666 Walnut St. 25th Floor, Des Moines, IA 50309",
                        "phone": "800-532-1275",
                        "website": "https://www.iowalegalaid.org",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Kansas",
        "cities": [
            {
                "name": "Wichita",
                "clinics": [
                    {
                        "name": "Kansas City Tax Clinic, UMKC School of Law",
                        "address": "500 East 52nd Street, Kansas City, MO 64110",
                        "phone": "816-235-6201",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Aid of Western Missouri",
                        "address": "4001 Dr. Martin Luther King, Jr. Blvd, Ste 300, Kansas City, MO 64130",
                        "phone": "806-474-6750 (KC Metro) / 800-990-2907 (Outside KC)",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Kentucky",
        "cities": [
            {
                "name": "Louisville",
                "clinics": [
                    {
                        "name": "Legal Aid Society, Inc.",
                        "address": "416 W. Muhammad Ali Blvd., Ste.300, Louisville, KY 40202",
                        "phone": "502-584-1254 / 800-292-1862",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "AppalReD Legal Aid",
                        "address": "114 North Third Street, Richmond, KY 40475",
                        "phone": "859-624-1394 / 800-477-1394",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Aid of the Bluegrass",
                        "address": "300 East Main Street, Suite 210, Lexington, KY 40507",
                        "phone": "859-431-8200",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Louisiana",
        "cities": [
            {
                "name": "New Orleans",
                "clinics": [
                    {
                        "name": "Southeast Louisiana Legal Services",
                        "address": "1340 Poydras Street, Suite 600, New Orleans, LA 70112",
                        "email": "application@slls.org",
                        "phone": "504-529-1000, ext. 225 / 877-521-6242, ext. 225",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "LSU Law Low Income Tax Clinic",
                        "address": "1 East Stadum Drive, Rm W109, Baton Rouge, LA 70898",
                        "email": "taxclinic@lsu.edu",
                        "phone": "225-578-7819",
                        "website": "https://www.law.lsu.edu/forms/litc",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Shreveport",
                "clinics": [
                    {
                        "name": "Southeast Louisiana Legal Services",
                        "address": "1340 Poydras Street, Suite 600, New Orleans, LA 70112",
                        "email": "application@slls.org",
                        "phone": "504-529-1000, ext. 225 / 877-521-6242, ext. 225",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "LSU Law Low Income Tax Clinic",
                        "address": "1 East Stadum Drive, Rm W109, Baton Rouge, LA 70898",
                        "email": "taxclinic@lsu.edu",
                        "phone": "225-578-7819",
                        "website": "https://www.law.lsu.edu/forms/litc",
                        "small_case_procedures_only": False,
                    },
                ],
            },
        ],
    },
    {
        "state": "Maine",
        "cities": [
            {
                "name": "Portland",
                "clinics": [
                    {
                        "name": "Pine Tree Legal Assistance, Inc.",
                        "address": "39 Green Street, PO Box 2429, Augusta, ME 04338",
                        "phone": "207-552-3108",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Maryland",
        "cities": [
            {
                "name": "Baltimore",
                "clinics": [
                    {
                        "name": "Maryland Volunteer Lawyers Service",
                        "address": "201 North Charles Street, Suite 1400, Baltimore, MD 21201",
                        "phone": "410-547-6537 / 800-510-0050",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "University of Baltimore School of Law",
                        "address": "1420 North Charles Street, Baltimore, MD 21201",
                        "phone": "410-837-5706",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "University of Maryland Francis King Carey School of Law",
                        "address": "500 West Baltimore Street, Baltimore, MD 21201",
                        "phone": "410-706-3295",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Massachusetts",
        "cities": [
            {
                "name": "Boston",
                "clinics": [
                    {
                        "name": "Greater Boston Legal Services",
                        "address": "197 Friend Street, Boston, MA 02114",
                        "email": "Taxbenefits-help@gbls.org",
                        "phone": "617-371-1234 / 617-603-1569",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Services of Harvard Law School",
                        "address": "122 Boylston Street, Jamaica Plain, MA 02130",
                        "email": "apatten@law.harvard.edu",
                        "phone": "617-390-1729",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "603 Legal Aid Low-Income Taxpayer Project",
                        "address": "93 N. State Street, Suite 200, Concord, NH 03301",
                        "email": "lgoldberg@603legalaid.org",
                        "phone": "603-224-3333",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Rhode Island Legal Services, Inc.",
                        "address": "56 Pine Street, 4th Floor, Providence, RI 02903",
                        "email": "breiss@rils.org",
                        "phone": "401-274-2652",
                        "website": "",
                        "small_case_procedures_only": True,
                    },
                    {
                        "name": "Vermont Legal Aid, Inc.",
                        "address": "264 North Winooski Avenue, Burlington, VT 05402",
                        "email": "zlees@vtlegalaid.org",
                        "phone": "800-889-2047",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Northeast Legal Aid",
                        "address": "50 Island Street, Suite 203A, Lawrence, MA 01840",
                        "email": "mjiganti@nla-ma.org",
                        "phone": "978-458-1465",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Michigan",
        "cities": [
            {
                "name": "Detroit",
                "clinics": [
                    {
                        "name": "Accounting Aid Society LITC",
                        "address": "3031 West Grand Boulevard, Suite 470, Detroit, Michigan 48202",
                        "phone": "313-556-1920, ext. 1219 / 866-673-0873, ext. 1219 (toll free)",
                        "website": "https://www.accountingaidsociety.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Michigan State University College of Law",
                        "address": "648 N. Shaw Lane, East Lansing, MI 48824",
                        "phone": "517-432-6880",
                        "website": "https://www.taxclinic.law.msu.edu",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "University of Michigan Law School",
                        "address": "701 South State Street, Ann Arbor, MI 48109",
                        "phone": "734-936-3535",
                        "website": "https://www.law.umich.edu/clinical/litc",
                        "small_case_procedures_only": True,
                    },
                    {
                        "name": "West Michigan Clinic, Legal Aid of Western Michigan",
                        "address": "25 Division Ave. South, Suite 300, Grand Rapids, MI 49503",
                        "phone": "616-774-0672, ext. 132 / 800-442-2777, ext. 132",
                        "website": "https://www.lawestmi.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Toledo Tax Controversy Clinic, University of Toledo College of Law",
                        "address": "1825 W. Rocket Drive, Toledo, OH 43606",
                        "phone": "419-684-8822",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Minnesota",
        "cities": [
            {
                "name": "St. Paul",
                "clinics": [
                    {
                        "name": "University of Minnesota Tax Clinic",
                        "address": "229 19th Avenue South/190 Walter Mondale Hall, Minneapolis, MN 55455",
                        "phone": "612-625-5515",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Mid-Minnesota Legal Aid Tax Law Project",
                        "address": "111 North 5th Street, Suite 100, Minneapolis, MN 55403",
                        "phone": "612-334-5970",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Mississippi",
        "cities": [
            {
                "name": "Jackson",
                "clinics": [
                    {
                        "name": "North Mississippi Rural Legal Services Mississippi Taxpayer Assistance Project",
                        "address": "5 County Road 1014-PO Box 928, Oxford, MS 38655",
                        "phone": "662-234-2918 ext. 2126 / 888-808-8049",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Missouri",
        "cities": [
            {
                "name": "Kansas City",
                "clinics": [
                    {
                        "name": "Kansas City Tax Clinic, UMKC School of Law",
                        "address": "500 East 52nd Street, Kansas City, MO 64110",
                        "phone": "816-235-6201",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Aid of Western Missouri",
                        "address": "4001 Dr. Martin Luther King, Jr. Blvd, Ste. 300, Kansas City, MO 64130",
                        "phone": "816-474-6750 (KC Metro) / 800-990-2907 (Outside KC)",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "St. Louis",
                "clinics": [
                    {
                        "name": "Washington University School of Law",
                        "address": "Anheuser Busch Hall, Room 105, Forest Park Parkway and Throop Drive, St. Louis, MO 63130",
                        "phone": "314-935-7238",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
        ],
    },
    {
        "state": "Montana",
        "cities": [
            {
                "name": "Billings",
                "clinics": [
                    {
                        "name": "University of Wyoming",
                        "address": "1000 E. University Ave. Dept 3275, Laramie, WY 82071",
                        "email": "litc@uwyo.edu",
                        "phone": "307-766-6114",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
            {
                "name": "Helena",
                "clinics": [
                    {
                        "name": "Gonzaga Law School",
                        "address": "721 N. Cincinnati Street, Spokane, WA 99202",
                        "phone": "509-313-5791",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
        ],
    },
    {
        "state": "Nebraska",
        "cities": [
            {
                "name": "Omaha",
                "clinics": [
                    {
                        "name": "Legal Aid of Nebraska",
                        "address": "1241 N. Street, Suite 200, Lincoln, NE 68508",
                        "phone": "877-250-2016",
                        "website": "https://www.legalaidofnebraska.org",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Nevada",
        "cities": [
            {
                "name": "Las Vegas",
                "clinics": [
                    {
                        "name": "Texas A&M University School of Law Tax Dispute Resolution Clinic",
                        "address": "307 W. 7th St., Suite LL 50, Fort Worth, Texas 76102",
                        "email": "tdrc@law.tamu.edu",
                        "phone": "817-212-4123",
                        "website": "https://www.law.tamu.edu/tax-clinic",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Inland Counties Legal Services Low Income Taxpayer Clinic",
                        "address": "1040 Iowa Ave., Suite 109, Riverside, California 92507",
                        "phone": "888-245-4257",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Reno",
                "clinics": [
                    {
                        "name": "Texas A&M University School of Law Tax Dispute Resolution Clinic",
                        "address": "307 W. 7th St., Suite LL 50, Fort Worth, Texas 76102",
                        "email": "tdrc@law.tamu.edu",
                        "phone": "817-212-4123",
                        "website": "https://www.law.tamu.edu/tax-clinic",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Inland Counties Legal Services Low Income Taxpayer Clinic",
                        "address": "1040 Iowa Ave., Suite 109, Riverside, California 92507",
                        "phone": "888-245-4257",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
        ],
    },
    {
        "state": "New Hampshire",
        "cities": [
            {
                "name": "Boston",
                "clinics": [
                    {
                        "name": "603 Legal Aid",
                        "address": "93 N. State Street, Suite 200, Concord, NH 03301",
                        "phone": "603-224-3333",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "New Jersey",
        "cities": [
            {
                "name": "New York City",
                "clinics": [
                    {
                        "name": "Legal Services of New Jersey",
                        "address": "100 Metroplex Drive, Edison, NJ 08817",
                        "phone": "888-576-5529",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Northeast New Jersey Legal Services",
                        "address": "574 Summit Avenue, 2nd Floor, Jersey City, NJ 07306",
                        "phone": "201-792-6363",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Rutgers School of Law Federal Tax Clinic",
                        "address": "123 Washington Street, Newark, N.J. 08816",
                        "phone": "973-353-1685",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "New Mexico",
        "cities": [
            {
                "name": "Albuquerque",
                "clinics": [
                    {
                        "name": "New Mexico Legal Aid",
                        "address": "P.O. Box 25486, Albuquerque, NM 87125 / 505 Marquette Ave. NW, 700, Albuquerque, NM 87102",
                        "phone": "833-545-4357 (intake) / 505-814-6593 (clinic)",
                        "website": "https://www.newmexicolegalaid.org",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "New York",
        "cities": [
            {
                "name": "Albany",
                "clinics": [
                    {
                        "name": "Legal Aid Society of Northeastern New York",
                        "address": "95 Central Avenue, Albany, NY 12206",
                        "phone": "833-628-0087",
                        "website": "",
                        "small_case_procedures_only": True,
                    },
                    {
                        "name": "Vermont Legal Aid, Inc.",
                        "address": "264 North Winooski Avenue, Burlington, VT 05402",
                        "phone": "800-889-2047",
                        "website": "https://www.vtlawhelp.org",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Buffalo",
                "clinics": [
                    {
                        "name": "Central Library of Rochester",
                        "address": "115 South Avenue, Rochester, NY 14604",
                        "phone": "585-900-1024",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Syracuse University College of Law LITC",
                        "address": "Office of Clinical Legal Education, Box 6543, Syracuse, New York 13217-6543",
                        "phone": "315-443-4582 / 888-797-5291 (Toll-free)",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Cornell University Law School",
                        "address": "241 Campus Road, Ithaca, NY 14853",
                        "phone": "607-255-4196",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Syracuse",
                "clinics": [
                    {
                        "name": "Syracuse University College of Law LITC",
                        "address": "Office of Clinical Legal Education, Box 6543, Syracuse, New York 13217-6543",
                        "phone": "315-443-4582 / 888-797-5291 (Toll-free)",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Cornell University Law School",
                        "address": "241 Campus Road, Ithaca, NY 14853",
                        "phone": "607-255-4196",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "New York City",
                "clinics": [
                    {
                        "name": "Brooklyn Legal Services Corporation A",
                        "address": "260 Broadway, Suite 2, Brooklyn, NY 11211",
                        "phone": "718-487-2300",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Mobilization for Justice",
                        "address": "100 William Street, 6th Fl, New York, NY 10038",
                        "phone": "212-417-3839",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Brooklyn LITC, Brooklyn Legal Services NYC",
                        "address": "105 Court Street, Brooklyn, N.Y. 11201",
                        "phone": "917-661-4500",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Fordham University School of Law Lincoln Square Legal Services, Inc.",
                        "address": "150 West 62nd Street, 9th Floor, New York, N.Y. 10023",
                        "phone": "212-636-7353",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Bronx Legal Services",
                        "address": "349 149th Street, 10th Floor, Bronx, N.Y. 10451",
                        "phone": "917-661-4500",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Queens Legal Services",
                        "address": "8900 Sutphin Blvd., 5th Floor, Jamaica, N.Y. 11435",
                        "phone": "917-661-4500",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "The Legal Aid Society LITC",
                        "address": "2090 Adam Clayton Powell, Jr. Blvd, 3rd Fl., New York, N.Y. 10027",
                        "phone": "888-663-6880",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
        ],
    },
    {
        "state": "North Carolina",
        "cities": [
            {
                "name": "Winston-Salem",
                "clinics": [
                    {
                        "name": "Charlotte Center for Legal Advocacy North Carolina LITC",
                        "address": "5535 Albemarle Rd., Charlotte, NC 28212",
                        "phone": "980-353-3530 / 800-438-1254 (Toll-free) / 800-247-1931 (Spanish line)",
                        "website": "https://www.charlottelegaladvocacy.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Pisgah Legal Services LITC",
                        "address": "62A Charlotte St., Asheville, NC 28801",
                        "phone": "828-253-0406 / 800-489-6144 (Toll-free)",
                        "website": "https://www.pisgahlegal.org",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "North Dakota",
        "cities": [
            {
                "name": "Bismarck",
                "clinics": [
                    {
                        "name": "No local clinic, remote assistance: Texas A&M University School of Law Tax Dispute Resolution Clinic",
                        "address": "307 W. 7th Street, Suite LL 50, Fort Worth, Texas 76102",
                        "email": "tdrc@law.tamu.edu",
                        "phone": "817-212-4123",
                        "website": "https://www.law.tamu.edu/tax-clinic",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Ohio",
        "cities": [
            {
                "name": "Cincinnati",
                "clinics": [
                    {
                        "name": "Legal Aid Society of Cincinnati",
                        "address": "215 E. Ninth Street, Suite 200, Cincinnati, OH 45202",
                        "phone": "513-241-9400",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Aid of the Bluegrass",
                        "address": "300 East Main Street, Suite 210, Lexington, KY 40507",
                        "phone": "859-431-8200",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Cleveland",
                "clinics": [
                    {
                        "name": "The Legal Aid Society of Cleveland",
                        "address": "1223 W. 6th Street, Cleveland, OH 44113",
                        "phone": "888-817-3777",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Community Legal Aid Services",
                        "address": "50 South Main Street, Suite 800, Akron, OH 44308",
                        "phone": "800-998-9454",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Toledo Tax Controversy Clinic, University of Toledo College of Law",
                        "address": "1825 W. Rocket Drive, Toledo, OH 43606",
                        "phone": "419-684-8822",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Columbus",
                "clinics": [
                    {
                        "name": "Legal Aid of Southeast and Central Ohio",
                        "address": "1108 City Park Avenue., Suite 100, Columbus, OH 43206",
                        "phone": "888-246-4420",
                        "website": "https://www.lasco.org/apply",
                        "small_case_procedures_only": False,
                    }
                ],
            },
        ],
    },
    {
        "state": "Oklahoma",
        "cities": [
            {
                "name": "Oklahoma City",
                "clinics": [
                    {
                        "name": "Legal Aid Services of Oklahoma",
                        "address": "907 South Detroit Ave., Suite 725, Tulsa, Oklahoma 74120",
                        "phone": "918-236-9572",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Oregon",
        "cities": [
            {
                "name": "Portland",
                "clinics": [
                    {
                        "name": "Lewis & Clark Law School Tax Clinic",
                        "address": "333 SW 5th Ave, Ste. 400, Portland, OR 97204",
                        "email": "litc@lcark.edu",
                        "phone": "503-768-6500",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Aid Services of Oregon",
                        "address": "621 SW Morrison St., Ste. 900, Portland, OR 97205",
                        "phone": "",
                        "website": "https://www.ortaxhelp.com",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Oregon Law Center Tax Clinic",
                        "address": "621 SW Morrison St., Ste. 1450, Portland, OR 97205",
                        "email": "LITC@oregonlawcenter.org",
                        "phone": "800-672-4919",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Pennsylvania",
        "cities": [
            {
                "name": "Philadelphia",
                "clinics": [
                    {
                        "name": "Delaware Community Reinvestment Action Council, Inc.",
                        "address": "One East Laurel Street Georgetown, Delaware 19947 and 600 South Harrison Street Wilmington, DE 19805",
                        "phone": "302-690-5000 / 302-393-1607 (Spanish line)",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "MidPenn Legal Services",
                        "address": "29 North Queen, York, PA 17403",
                        "phone": "844-675-7829",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Philadelphia Legal Assistance",
                        "address": "718 Arch Street, Suite 300N, Philadelphia, PA 19106",
                        "phone": "215-981-3800",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Villanova University School of Law Tax Clinic",
                        "address": "299 North Spring Mill Road, Villanova, PA 19085",
                        "phone": "610-519-4123 / 888-829-2546 / 866-655-4419 (Spanish line)",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Temple Law School",
                        "address": "1719 N. Broad Street, Philadelphia, PA 19122",
                        "email": "taxclinic@temple.edu",
                        "phone": "215-204-8948",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Susquehanna Legal Aid for Adults and Youth (SLAAY)",
                        "address": "1307 Park Ave., Box #10, Williamsport, PA 17701",
                        "phone": "570-392-3025",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Misericordia University LITC",
                        "address": "301 Lake Street, Dallas, PA 18612",
                        "email": "taxclinic@misericordia.edu",
                        "phone": "(570) 674-1472",
                        "website": "",
                        "small_case_procedures_only": True,
                    },
                ],
            },
            {
                "name": "Pittsburgh",
                "clinics": [
                    {
                        "name": "University of Pittsburgh School of Law Tax Clinic",
                        "address": "P.O. Box 7226, Pittsburgh, PA 15213",
                        "email": "lawclin@pitt.edu",
                        "phone": "412-648-1300",
                        "website": "https://www.law.pitt.edu/academics/experiential-learning-opportunities/clinics/taxpayer-clinic",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Summit Legal Aid Low Income Taxpayer Clinic",
                        "address": "10 West Cherry Ave., Washington, PA 15301",
                        "phone": "800-846-0871",
                        "website": "https://www.pataxhelp.org/contact-us",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Temple Law School",
                        "address": "1719 N. Broad Street, Philadelphia, PA 19122",
                        "email": "taxclinic@temple.edu",
                        "phone": "215-204-8948",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
        ],
    },
    {
        "state": "Rhode Island",
        "cities": [
            {
                "name": "Boston",
                "clinics": [
                    {
                        "name": "Rhode Island Legal Services, Inc.",
                        "address": "56 Pine Street, 4th Floor, Providence, RI 02903",
                        "phone": "401-274-2652",
                        "website": "",
                        "small_case_procedures_only": True,
                    }
                ],
            }
        ],
    },
    {
        "state": "South Carolina",
        "cities": [
            {
                "name": "Columbia",
                "clinics": [
                    {
                        "name": "South Carolina Legal Services",
                        "address": "701 S. Main Street, Greenville, S.C. 29601",
                        "phone": "888-346-5592",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "University of South Carolina School of Law Clinic",
                        "address": "1525 Senate Street, Columbia, SC 29208",
                        "phone": "803-777-8614",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "South Dakota",
        "cities": [
            {
                "name": "Aberdeen",
                "clinics": [
                    {
                        "name": "No local clinic, remote assistance: Texas A&M University School of Law Tax Dispute Resolution Clinic",
                        "address": "307 W. 7th Street, Suite LL 50, Fort Worth, Texas 76102",
                        "email": "tdrc@law.tamu.edu",
                        "phone": "817-212-4123",
                        "website": "https://www.law.tamu.edu/tax-clinic",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Tennessee",
        "cities": [
            {
                "name": "Knoxville",
                "clinics": [
                    {
                        "name": "The Legal Aid Society of Middle Tennessee and the Cumberlands Tennessee Taxpayer Project",
                        "address": "575 Oak Ridge Turnpike, Suite 201, Oak Ridge, TN 37830 and 1321 Murfreesboro Pike, Suite 400, Nashville, TN 37217",
                        "phone": "866-481-3669",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
            {
                "name": "Nashville",
                "clinics": [
                    {
                        "name": "The Legal Aid Society of Middle Tennessee and the Cumberlands Tennessee Taxpayer Project",
                        "address": "575 Oak Ridge Turnpike, Suite 201, Oak Ridge, TN 37830 and 1321 Murfreesboro Pike, Suite 400, Nashville, TN 37217",
                        "phone": "866-481-3669",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
            {
                "name": "Memphis",
                "clinics": [
                    {
                        "name": "Memphis Area Legal Services, Inc.",
                        "address": "200 Jefferson, Suire 1075, Memphis, TN 38103",
                        "phone": "901-523-8822, ext. 419",
                        "website": "https://www.malsi.org",
                        "small_case_procedures_only": False,
                    }
                ],
            },
        ],
    },
    {
        "state": "Texas",
        "cities": [
            {
                "name": "Dallas",
                "clinics": [
                    {
                        "name": "Legal Aid of North West Texas",
                        "address": "600 E. Weatherford Street, Fort Worth, TX 76102",
                        "phone": "817-336-3943 / 800-955-3959",
                        "website": "https://www.lanwt.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Southern Methodist University Dedman School of Law Tax Clinic",
                        "address": "3315 Daniel Avenue, Dallas, TX 75205",
                        "phone": "214-768-8299",
                        "website": "https://www.law.smu.edu/clinics/federal-taxpayers-clinic",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Lone Star Legal Aid, Inc.",
                        "address": "1415 Fannin Street, Houston, TX 77002",
                        "phone": "713-652-0077 / 800-733-8394",
                        "website": "https://www.lonestarlegal.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Texas A&M University School of Law",
                        "address": "307 W. 7th Street, Suite LL50, Fort Worth, TX 76102",
                        "email": "LITC@law.tamu.edu",
                        "phone": "817-212-4062",
                        "website": "https://www.law.tamu.edu/tax-clinic",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Houston",
                "clinics": [
                    {
                        "name": "Lone Star Legal Aid, Inc.",
                        "address": "1415 Fannin Street, Houston, TX 77002",
                        "phone": "713-652-0077 / 800-733-8394",
                        "website": "https://www.lonestarlegal.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Houston Volunteer Lawyers",
                        "address": "1111 Bagby, Ste FLB300, Houston, TX 77002",
                        "phone": "713-228-0735",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "South Texas College of Law",
                        "address": "1303 San Jacinto St., Houston, TX 77002",
                        "phone": "800-646-1253 / 713-646-2922",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "El Paso",
                "clinics": [
                    {
                        "name": "Texas A&M University School of Law",
                        "address": "307 W. 7th Street, Suite LL50, Fort Worth, TX 76102",
                        "email": "LITC@law.tamu.edu",
                        "phone": "817-212-4062",
                        "website": "https://www.law.tamu.edu/tax-clinic",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Texas Tech University School of Law",
                        "address": "3311 18th Street, Lubbock, TX 79409",
                        "email": "clinics.law@ttu.edu",
                        "phone": "806-742-4312 / 800-420-8037 (toll-free)",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Texas Taxpayer Assistance Project, Texas RioGrande Legal Aid, Inc.",
                        "address": "1111 N. Main Avenue, San Antonio, TX 78212",
                        "phone": "210-212-3747 / 833-329-8752",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Lubbock",
                "clinics": [
                    {
                        "name": "Texas Tech University School of Law",
                        "address": "3311 18th Street, Lubbock, TX 79409",
                        "email": "clinics.law@ttu.edu",
                        "phone": "806-742-4312 / 800-420-8037 (toll-free)",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
            {
                "name": "San Antonio",
                "clinics": [
                    {
                        "name": "Texas Taxpayer Assistance Project, Texas RioGrande Legal Aid, Inc.",
                        "address": "1111 N. Main Avenue, San Antonio, TX 78212",
                        "phone": "210-212-3747 / 833-329-8752",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
        ],
    },
    {
        "state": "Utah",
        "cities": [
            {
                "name": "Salt Lake City",
                "clinics": [
                    {
                        "name": "Utah Tax Help Services",
                        "address": "815 W 1250 S, Orem, UT 84058",
                        "phone": "801-210-8001",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Westminster Tax",
                        "address": "1840 S 1300 E Gore 118, Salt Lake City, UT 84105",
                        "phone": "801-210-8291",
                        "website": "",
                        "small_case_procedures_only": False,
                    },
                ],
            }
        ],
    },
    {
        "state": "Vermont",
        "cities": [
            {
                "name": "Burlington",
                "clinics": [
                    {
                        "name": "Vermont Legal Aid, Inc.",
                        "address": "264 North Winooski Avenue, Burlington, VT 05402",
                        "phone": "800-889-2047",
                        "website": "https://www.vtlawhelp.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Legal Aid Society of Northeastern New York",
                        "address": "95 Central Avenue, Albany, NY 12206",
                        "phone": "833-628-0087",
                        "website": "",
                        "small_case_procedures_only": True,
                    },
                ],
            }
        ],
    },
    {
        "state": "Virginia",
        "cities": [
            {
                "name": "Richmond",
                "clinics": [
                    {
                        "name": "The Community Tax Law Project",
                        "address": "5206 Markel Road, Suite 100-B, Richmond, VA 23230",
                        "email": "info@ctlp.org",
                        "phone": "804-358-5855",
                        "website": "https://www.ctlp.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Washington & Lee University School of Law",
                        "address": "Lewis Hall Suite 249, Lexington, VA 24450",
                        "email": "taxclinic@wlu.edu",
                        "phone": "540-458-8918",
                        "website": "https://www.law.wlu.edu/clinics/tax-clinic",
                        "small_case_procedures_only": False,
                    },
                ],
            },
            {
                "name": "Roanoke",
                "clinics": [
                    {
                        "name": "The Community Tax Law Project",
                        "address": "5206 Markel Road, Suite 100-B, Richmond, VA 23230",
                        "email": "info@ctlp.org",
                        "phone": "804-358-5855",
                        "website": "https://www.ctlp.org",
                        "small_case_procedures_only": False,
                    },
                    {
                        "name": "Washington & Lee University School of Law",
                        "address": "Lewis Hall Suite 249, Lexington, VA 24450",
                        "email": "taxclinic@wlu.edu",
                        "phone": "540-458-8918",
                        "website": "https://www.law.wlu.edu/clinics/tax-clinic",
                        "small_case_procedures_only": False,
                    },
                ],
            },
        ],
    },
    {
        "state": "Washington",
        "cities": [
            {
                "name": "Seattle",
                "clinics": [
                    {
                        "name": "University of Washington School of Law Federal Tax Clinic",
                        "address": "William H. Gates Hall, Suite 265, P.O. Box 85110, Seattle, WA 98145",
                        "phone": "206-685-6805",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
            {
                "name": "Spokane",
                "clinics": [
                    {
                        "name": "Gonzaga University School of Law Tax Clinic",
                        "address": "721 North Cincinnati Street, Spokane, WA 99202",
                        "phone": "509-313-5791",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            },
        ],
    },
    {
        "state": "West Virginia",
        "cities": [
            {
                "name": "Charleston",
                "clinics": [
                    {
                        "name": "AppalRed Legal Aid",
                        "address": "114 N. Third Street, Richmond, KY 40475",
                        "phone": "859-624-1394 / 800-477-1394",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Wisconsin",
        "cities": [
            {
                "name": "Milwaukee",
                "clinics": [
                    {
                        "name": "Legal Action of Wisconsin, Inc.",
                        "address": "633 W. Wisconsin Ave., Ste. 2000, Milwaukee, WI 53203",
                        "phone": "855-947-2529 / 608-473-3820",
                        "website": "https://www.legalaction.org",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
    {
        "state": "Wyoming",
        "cities": [
            {
                "name": "Cheyenne",
                "clinics": [
                    {
                        "name": "University of Wyoming LITC",
                        "address": "1000 E. University Ave. Dept 3275, Laramie, WY 82071",
                        "email": "litc@uwyo.edu",
                        "phone": "307-766-6114",
                        "website": "",
                        "small_case_procedures_only": False,
                    }
                ],
            }
        ],
    },
]


class LITCPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def update(self):
        if Page.objects.filter(slug="clinics-and-pro-bono-programs").exists():
            logger.info(
                "- Clinics and Pro Bono Programs page already exists, skipping."
            )
            return
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def run(self):
        command_name = "Create Clinics and Pro Bono Programs page"

        if ExecuteScript.command_exists(command_name):
            logger.info(f"Script '{command_name}' already ran. Update not necessary.")
            return

        script_entry = ExecuteScript.create_script(command_name)

        try:
            self.update()
            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = "LITC Cities page created successfully."
            script_entry.save()

        except Exception as e:
            error_msg = f"Unexpected error during LITC Cities page creation: {type(e).__name__} - {str(e)}"
            logger.error(error_msg)
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"<strong>Error:</strong> {error_msg}"
            script_entry.save()
            raise

    def create_page_info(self, home_page):
        slug = "clinics-and-pro-bono-programs"
        title = "Clinics and Pro Bono Programs"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        for state in all_litc_clinics:
            for city in state["cities"]:
                city["clinics"] = sorted(city["clinics"], key=lambda x: x["name"])

        for state in all_litc_clinics:
            state["cities"] = sorted(state["cities"], key=lambda x: x["name"])

        sorted_clinics = sorted(all_litc_clinics, key=lambda x: x["state"])

        low_income_taxpayer_clinic_data = [
            {
                "type": "state",
                "value": {
                    "state": state_data["state"],
                    "cities": state_data["cities"],
                },
            }
            for state_data in sorted_clinics
        ]

        litc_page = LITCPage(
            title=title,
            slug=slug,
            seo_title=title,
            search_description="Clinics and pro bono programs that provide free or low-cost legal assistance to low-income taxpayers with tax disputes.",
            low_income_taxpayer_clinics=low_income_taxpayer_clinic_data,
            show_in_menus=True,
        )

        home_page.add_child(instance=litc_page)
        litc_page.save_revision().publish()
        logger.info(f"'{title}' page created and published.")
