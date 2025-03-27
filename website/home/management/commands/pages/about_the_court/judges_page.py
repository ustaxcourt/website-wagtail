from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    JudgeIndex,
    JudgeProfile,
    JudgeCollection,
    JudgeRole,
)

all_judges = [
    {
        "first_name": "Kathleen",
        "middle_initial": "",
        "last_name": "Kerrigan",
        "suffix": "",
        "display_name": "Kathleen Kerrigan",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0777",
        "bio": "Chief Judge. B.S., Boston College 1985; J.D., University of Notre Dame Law School, 1990. Admitted to Massachusetts Bar, 1991 and District Columbia Bar, 1992. Legislative Director for Congressman Richard E. Neal, Member of the Ways and Means Committee, 1990 to 1998. Associate and partner at Baker & Hostetler LLP, Washington, D.C. 1998-2005. Tax Counsel for Senator John F. Kerry, Member of Senate Finance Committee, 2005-2012. Appointed by President Obama as Judge of the United States Tax Court; sworn in on May 4, 2012, for a term ending on May 3, 2027. Elected as Chief Judge for a two-year term effective June 1, 2022. Re-elected as Chief Judge for a two-year term effective June 1, 2024.",
    },
    {
        "first_name": "Jeffrey",
        "middle_initial": "S.",
        "last_name": "Arbeit",
        "suffix": "",
        "display_name": "Jeffrey S. Arbeit",
        "title": "Judge",
        "chambers_telephone": "(202) 521-4718",
        "bio": "Judge. Born in Massachusetts. Served for nine years on the nonpartisan staff of the Joint Committee on Taxation of the United States Congress. Before that, worked for four years at Sullivan & Cromwell LLP. Clerked for two years for the Honorable James S. Halpern of the United States Tax Court. Holds a B.A. from Brown University, a J.D. from Boston University School of Law, and an LL.M. from New York University School of Law.  Appointed by President Biden as Judge of the United States Tax Court and sworn in on October 3, 2024, for a term ending October 2, 2039.",
    },
    {
        "first_name": "Tamara",
        "middle_initial": "W.",
        "last_name": "Ashford",
        "suffix": "",
        "display_name": "Tamara W. Ashford",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0822",
        "bio": "Judge. Born in Massachusetts. B.A., in public policy studies, Duke University (1991); J.D., Vanderbilt University Law School (1994); LL.M., Master of Laws in Taxation, with an honors certificate of specialization in international tax, University of Miami School of Law (1997). Admitted to the Bars of North Carolina; District of Columbia; United States Tax Court; United States Courts of Appeals for the District of Columbia, First, Second, Fourth, Fifth, Sixth, Ninth and Tenth Circuits; United States Supreme Court. Served as Law Clerk to the Honorable John C. Martin, North Carolina Court of Appeals (1994-1996). Practiced law as a Trial Attorney in the Appellate Section, Tax Division, United States Department of Justice (1997-2001). Practiced law as a Senior Associate, Miller & Chevalier, Chartered (2001-2004). Served as Assistant to the Commissioner (2004-2007) and U.S. Director for the Joint International Tax Shelter Information Centre/Senior Advisor to the Commissioner, Large and Mid-Size Business Division (2007-2008) in the Internal Revenue Service. Recipient of the Sheldon S. Cohen National Outstanding Support to the Office of Chief Counsel Award (2006). Practiced law as Counsel, Dewey & LeBoeuf, LLP (2008-2011). Recognized for Tax Controversy by the 2010 edition of The Legal 500. Served as Deputy Assistant Attorney General for Appellate and Review (2011-2014), Principal Deputy Assistant Attorney General and Acting Deputy Assistant Attorney General for Policy and Planning (2013-2014), and Acting Assistant Attorney General (June 2014-December 2014) in the Tax Division, United States Department of Justice. Named a 2012 Person of the Year by Tax Analysts. Appointed by President Obama as Judge of the United States Tax Court; sworn in on December 19, 2014 for a term ending December 18, 2029.",
    },
    {
        "first_name": "Ronald",
        "middle_initial": "L.",
        "last_name": "Buch",
        "suffix": "",
        "display_name": "Ronald L. Buch",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0810",
        "bio": "Judge. Born in Michigan. Northwood Institute, B.B.A., 1987. Detroit College of Law, J.D. with Taxation Concentration, 1993. Capital University Law School, LL.M. in Taxation, 1994. Research Editor of the Detroit College of Law Review, 1992-1993. Ohio Tax Review Fellow, 1993-1994. Admitted to the bars of Michigan, inactive (1993), Ohio, inactive (1994), Florida (1994), and the District of Columbia (1995). Consultant at KPMG Washington National Tax (1995-1997). Attorney-Advisor (1997-2000) and Senior Legal Counsel (2000-2001) at the IRS Office of Chief Counsel. Associate (2001-2005) and Partner (2005-2009) at McKee Nelson LLP. Partner at Bingham McCutchen LLP (2009-2013). James E. Markham Attorney of the Year Award, 1999. Chair of the DC Bar Tax Audits and Litigation Committee, 2006-2008. Chair of the ABA Tax Section’s Administrative Practice Committee, 2008-2009. Appointed by President Obama as Judge of the United States Tax Court; sworn in on January 14, 2013, for a term ending January 13, 2028. <p><strong>Additional Information or Requirements for Law Clerk Applicants:</strong></p><p>LL.M. preferred, writing sample not to exceed 10 pages.</p>",
    },
    {
        "first_name": "Elizabeth",
        "middle_initial": "A.",
        "last_name": "Copeland",
        "suffix": "",
        "display_name": "Elizabeth A. Copeland",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0670",
        "bio": "Judge. Born in Colorado. Bachelor of Business Administration from the University of Texas at Austin, cum laude, and Juris Doctor from the University of Texas School of Law. Certified Public Accountant (Texas, 1988); admitted to the State Bar of Texas (1992). Ernst & Whinney (1986-89); Law Clerk to Justice Cook of the Texas Supreme Court; Attorney-Adviser to Judge Mary Ann Cohen of the US Tax Court (1992-93); Adjunct Professor at Our Lady of the Lake University (1997-99); Partner with Clark Hill PLC. Recipient of the American Bar Association Section of Taxation's Janet Spragens Pro Bono Award (2009); Tax Person of the Year by Tax Analysts (2012); San Antonio Tax Lawyer of the Year (2011, 2017, 2018). Chair, State Bar of Texas Tax Section for the 2013-14 term. Appointed by President Trump as Judge of the United States Tax Court; sworn in on October 12, 2018 for a term ending October 11, 2033.",
    },
    {
        "first_name": "Maurice",
        "middle_initial": "B.",
        "last_name": "Foley",
        "suffix": "",
        "display_name": "Maurice B. Foley",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0681",
        "bio": "Judge. Received a Bachelor of Arts degree from Swarthmore College; a Juris Doctor from University of California, Berkeley School of Law; and a Masters of Law in Taxation from Georgetown University Law Center. Prior to the appointment to the Court, was an attorney for the Legislation and Regulations Division of the Internal Revenue Service, Tax Counsel for the United States Senate Committee on Finance, and Deputy Tax Legislative Counsel in the U.S. Treasury's Office of Tax Policy. Appointed by President Clinton as Judge, United States Tax Court, and sworn in on April 10, 1995, for a term ending April 9, 2010. Reappointed by President Obama and sworn in on November 25, 2011, for a term ending November 24, 2026. Served as Chief Judge of the Court June 1, 2018, through May 31, 2022. <p><strong>Additional Information or Requirements for Law Clerk Applicants:</strong></p><p><ul><li>LL.M.</li><li>Member of Bar</li><li>Experienced attorney in tax (must have 2-3 years experience)</li><li>Excellent writing skills</li><li>Cover Letter</li><li>Resume</li><li>Transcripts (J.D. and LL.M)</li><li>Writing Sample</li><li>References (3)</li></ul></p>",
    },
    {
        "first_name": "Cathy",
        "middle_initial": "",
        "last_name": "Fung",
        "suffix": "",
        "display_name": "Cathy Fung",
        "title": "Judge",
        "chambers_telephone": "(202) 657-0100",
        "bio": "Judge. B.A., University of California, Los Angeles; J.D., University of North Carolina at Chapel Hill; LL.M. in Taxation, New York University; and an LL.M. in Securities and Financial Regulation, Georgetown University Law Center. Served as a Law Clerk to the Honorable Robert A. Wherry of the United States Tax Court (2004-2006). Associate at Dewey Ballantine (later Dewey & LeBoeuf) (2006-2009); Attorney in the IRS Office of Chief Counsel, Financial Institutions and Products Division (2009-2015); Director, Headquarters Operations in the IRS Office of Chief Counsel, Large Business & International Division (2015-2019); Associate Area Counsel in the IRS Office of Chief Counsel, Large Business & International Division (2019-2022); and Deputy Area Counsel in the IRS Office of Chief Counsel, Litigation & Advisory Division (formerly Large Business & International) (2022-2024). Appointed by President Biden as Judge of the United States Tax Court and sworn in on December 13, 2024, for a term ending December 12, 2039.",
    },
    {
        "first_name": "Travis",
        "middle_initial": "A.",
        "last_name": "Greaves",
        "suffix": "",
        "display_name": "Travis A. Greaves",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0736",
        "bio": "Judge. Born in Texas.  Received a Bachelor of Arts degree from the University of Tennessee; a Juris Doctor, cum laude, from South Texas College of Law; and a Masters of Law in Taxation, with distinction, from Georgetown University Law Center. Immediately before appointment served as Deputy Assistant Attorney General for Appellate and Review in the U.S. Department of Justice’s Tax Division. Before joining the Department of Justice, was an attorney with Greaves Wu LLP; Caplin & Drysdale, Chartered; and Reed Smith, LLP.  Previously served as Tax & Economic Policy Advisor for the Office of Governor Bobby Jindal of the State of Louisiana. Appointed by President Trump as Judge of the United States Tax Court and sworn in on March 9, 2020 for a term ending March 8, 2035.",
    },
    {
        "first_name": "Benjamin",
        "middle_initial": "A.",
        "last_name": "Guider",
        "suffix": "III",
        "display_name": "Benjamin A. Guider III",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0885",
        "bio": "Judge. Has over 15 years of experience as a lawyer advising clients with respect to federal low-income housing tax credits, federal and state historic rehabilitation tax credits, tax-exempt bonds, and a variety of other private and public financing sources. Prior to joining the Court, he was an affordable housing attorney at Longwell Riess, L.L.C. From 2008 to 2023 he was an attorney at Coats Rose, P.C.  Holds a B.A. from the University of Virginia in 2001 and a J.D. from Tulane University in 2004. Member of the American Bar Association’s Forum on Affordable Housing and Community Development Law, as well as a member of the Louisiana State Bar Association and the State Bar of California. Appointed by President Biden as Judge of the United States Tax Court and sworn in on October 3, 2024, for a term ending October 2, 2039.",
    },
    {
        "first_name": "Rose",
        "middle_initial": "E.",
        "last_name": "Jenkins",
        "suffix": "",
        "display_name": "Rose E. Jenkins",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0878",
        "bio": "Judge. B.A. and M.A., Stanford University (2005); J.D., University of Texas School of Law (2008); E.LL.M. in Taxation, New York University School of Law (2012). Admitted to the New York State Bar (2009). Served as: Associate, Skadden, Arps, Slate, Meagher & Flom LLP, New York, NY (2008-2013); Attorney (2013-2017), Senior Counsel (2017-2019), and Special Counsel (2019-2020) in International office of IRS Office of Chief Counsel; Managing Director at KPMG Washington National Tax (2020-2021); Senior Attorney Advisor at The Tax Law Center at NYU Law (2021-2023); and Attorney in Procedure & Administration office of IRS Office of Chief Counsel (2023-2024). Member of New York State Bar Association Tax Section Executive Committee (2022). Appointed by President Biden as Judge of the United States Tax Court; sworn in on October 15, 2024, for a term ending October 14, 2039.",
    },
    {
        "first_name": "Courtney",
        "middle_initial": "D.",
        "last_name": "Jones",
        "suffix": "",
        "display_name": "Courtney D. Jones",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0795",
        "bio": "Judge.  B.S., Hampton University, magna cum laude (2000), recipient of the President’s Award for Exceptional Achievement; J.D., Harvard Law School (2004).  Editor-in-Chief of the Harvard BlackLetter Law Journal.  Admitted to the District of Columbia Bar.  Practiced law as a Senior Attorney, Tax-Exempt and Government Entities Division, Office of Chief Counsel of the Internal Revenue Service (2011-2019); as an Associate with Caplin & Drysdale, Chartered, Washington, D.C. (2008-2011); and as an Associate with Bird, Loechl, Brittain & McCants, Atlanta, Georgia (2004-2008).  Served on the Board of Trustees of Hampton University (2015-2018).  Appointed by President Trump as Judge of the United States Tax Court; sworn in on August 9, 2019 for a term ending in 2034.",
    },
    {
        "first_name": "Adam",
        "middle_initial": "B.",
        "last_name": "Landy",
        "suffix": "",
        "display_name": "Adam B. Landy",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0835",
        "bio": "Judge. Judge Landy holds a Bachelor of Science in Chemistry and a Master of Science in Sport and Entertainment Management from the University of South Carolina, a Juris Doctor from the University of South Carolina School of Law, and a Master of Laws in Taxation from the Northwestern University Pritzker School of Law. From 2010 to 2016, Judge Landy was an Associate Attorney with McNair Law Firm, P.A. (now Burr & Forman, LLP). From August 2016 until he joined the Court, Judge Landy was a Senior Attorney with the Internal Revenue Service Office of Chief Counsel. Appointed Special Trial Judge of the United States Tax Court, on December 6, 2021. Appointed by President Biden as Judge of the United States Tax Court; sworn in on August 8, 2024, for a term ending August 7, 2039.",
    },
    {
        "first_name": "Alina",
        "middle_initial": "I.",
        "last_name": "Marshall",
        "suffix": "",
        "display_name": "Alina I. Marshall",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0738",
        "bio": "Judge. Born in Romania. Received a Bachelor of Arts degree, cum laude, from Yale University and a Juris Doctor, cum laude, from the University of Pennsylvania Law School (Order of the Coif). Prior to appointment served as Counsel to the Chief Judge at the United States Tax Court and practiced law with Milbank, Tweed, Hadley & McCloy LLP; Freshfields Bruckhaus Deringer US LLP; and West & Feinberg, P.C.  Adjunct Professor of Law at Georgetown University Law Center.  Appointed by President Trump as Judge of the United States Tax Court; sworn in on August 24, 2020 for a term ending August 23, 2035.",
    },
    {
        "first_name": "Joseph",
        "middle_initial": "W.",
        "last_name": "Nega",
        "suffix": "",
        "display_name": "Joseph W. Nega",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0640",
        "bio": "Judge. Born in Illinois. DePaul University, B.S.C. in Accounting, 1981; DePaul University School of Law, J.D., 1984; Georgetown University School of Law, M.L.T., 1986. Admitted to the Illinois Bar 1984. On staff of the Joint Committee on Taxation of the United States Congress: Legislation Attorney, 1985-1989; Legislation Counsel, 1989-2009; and Senior Legislation Counsel, 2009-2013. Appointed by President Obama as Judge of the United States Tax Court; sworn in on September 4, 2013 for a term ending September 3, 2028.<p><strong>Additional Information or Requirements for Law Clerk Applicants:</strong></p><p><ul><li>J.D. with multiple tax courses or LL.M. in taxation in process or complete</li><li>Writing sample</li></ul></p>",
    },
    {
        "first_name": "Cary",
        "middle_initial": "Douglas",
        "last_name": "Pugh",
        "suffix": "",
        "display_name": "Cary Douglas Pugh",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0824",
        "bio": "Judge. Born in Virginia. B.A., in Political Science and Russian, magna cum laude, Duke University, 1987; M.A., in Russian and East European Studies, Stanford University, 1988; J.D., University of Virginia School of Law, 1994; Order of the Coif, Virginia Law Review Executive Editor. Admitted to Virginia State Bar, 1994, District of Columbia Bar, 1995, United States Supreme Court Bar, 1997. Served as Law Clerk to the Honorable Jackson L. Kiser, Chief Judge, U.S. District Court, Western District of Virginia, 1994-1995. Practiced law as an Associate, Vinson & Elkins LLP, Washington, DC, 1995-1999. Served as Minority Tax Counsel and Majority Tax Counsel, Committee on Finance, United States Senate, 1999-2002. Served as Special Counsel to the Chief Counsel, 2002-2005. Recipient of the Chief Counsel’s Award 2003. Practiced law as Counsel, Skadden, Arps, Slate, Meagher & Flom LLP, 2005-2014. Member of American Bar Association, Section of Taxation; named John S. Nolan Tax Law Fellow, 2001-2002; served as Chair, Tax Shelter Committee and Government Relations Committee and as Council Director. Fellow, American College of Tax Counsel. Former Adjunct Professor, Georgetown University Law Center, LL.M. Taxation Program. Appointed by President Obama as Judge of the United States Tax Court; sworn in on December 16, 2014 for a term ending December 15, 2029.<p><strong>Additional Information or Requirements for Law Clerk Applicants:</strong></p><p>Candidate must possess excellent writing and research skills; ability to work in a small team environment; ability to work carefully through facts and law. Candidate should not fear tax and will be exposed to Duke basketball but need not love Duke basketball.</p><p><strong>Application material required:</strong> Cover letter, resume, unofficial transcripts, three recommendations, and writing sample</p>",
    },
    {
        "first_name": "Emin",
        "middle_initial": "",
        "last_name": "Toro",
        "suffix": "",
        "display_name": "Emin Toro",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0760",
        "bio": "Judge. Born in Albania. Received a Bachelor of Arts degree from Palm Beach Atlantic College, summa cum laude, and a Juris Doctor with highest honors from the University of North Carolina School of Law (Order of the Coif). Prior to appointment to the Court served as a Law Clerk to Judge Karen LeCraft Henderson of the U.S. Court of Appeals for the District of Columbia Circuit and as a Law Clerk to Associate Justice Clarence Thomas of the Supreme Court of the United States; was a Partner at Covington & Burling LLP. Appointed by President Trump as Judge of the United States Tax Court; sworn in on October 18, 2019 for a term ending October 17, 2034.",
    },
    {
        "first_name": "Patrick",
        "middle_initial": "J.",
        "last_name": "Urda",
        "suffix": "",
        "display_name": "Patrick J. Urda",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0800",
        "bio": "Judge. Born in Indiana. Received a Bachelor of Arts degree, summa cum laude, from the University of Notre Dame and a Juris Doctor from Harvard Law School. Prior to appointment to the Court practiced law with McDermott Will & Emery and with Maciorowski, Sackmann & Ulrich; served as a Law Clerk to Judge Daniel A. Manion of the U.S. Court of Appeals for the Seventh Circuit; and held several positions with the U.S. Department of Justice’s Tax Division, including details as Counsel to the Deputy Assistant Attorney General for Appellate and Review and to the Criminal Division’s Office of Overseas Prosecutorial Development Assistance and Training. Former Adjunct Professor of Law at American University Washington College of Law. Appointed by President Trump as Judge of the United States Tax Court; sworn in on September 27, 2018 for a term ending September 26, 2033.<p><strong>Additional Information or Requirements for Law Clerk Applicants:</strong></p><ul><li>LL.M. preferred</li><li>Writing sample no longer than 10 pages</li><li>Transcripts (College/J.D./LL.M)</li></ul></p>",
    },
    {
        "first_name": "Kashi",
        "middle_initial": "",
        "last_name": "Way",
        "suffix": "",
        "display_name": "Kashi Way",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0871",
        "bio": "Judge. Born in Pennsylvania. B.A., University of Southern California, 1993; M.A., Columbia University, 1995; J.D., University of Virginia, 1999; Editor-in-Chief, Virginia Tax Review. Admitted to the Bars of California (1999) and the District of Columbia (2002). Served as Law Clerk to the Honorable Joseph H. Gale, United States Tax Court, 1999-2001. Practiced law as an Associate, Covington & Burling, LLP, Washington, DC, 2001-2005. Served on the staff of the Joint Committee on Taxation of the United States Congress: Legislation Counsel, 2005-2015; Senior Legislation Counsel, 2015-2024. Appointed by President Biden as Judge of the United States Tax Court; sworn in on August 7, 2024, for a term ending August 6, 2039.",
    },
    {
        "first_name": "Christian",
        "middle_initial": "N.",
        "last_name": "Weiler",
        "suffix": "",
        "display_name": "Christian N. Weiler",
        "title": "Judge",
        "chambers_telephone": "(202) 521-0649",
        "bio": "Judge.  Born in Louisiana. Received a Bachelor of Science degree in accounting from Louisiana State University, a Juris Doctor from Loyola University New Orleans College of Law, and a Master of Laws in Taxation from the Dedman School of Law at Southern Methodist University.  Prior to appointment to the Court practiced law as a partner at Weiler & Rees in New Orleans, Louisiana and was a board-certified tax law specialist, as recognized by the Louisiana Board of Legal Specialization.  Appointed by President Trump as Judge of the United States Tax Court; sworn in on September 9, 2020 for a term ending September 8, 2035.",
    },
    {
        "first_name": "Mary Ann",
        "middle_initial": "",
        "last_name": "Cohen",
        "suffix": "",
        "display_name": "Mary Ann Cohen",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0655",
        "bio": "Senior Judge. Born in New Mexico. Attended public schools in Los Angeles, CA; B.S., University of California, at Los Angeles, 1964; J.D., University of Southern California School of Law, 1967. Practiced law in Los Angeles, member in law firm of Abbott & Cohen. American Bar Association, Section of Taxation, and Continuing Legal Education activities. Received Dana Latham Memorial Award from Los Angeles County Bar Association Taxation Section, May 30, 1997; Jules Ritholz Memorial Merit Award from ABA Tax Section Committee on Civil and Criminal Tax Penalties, 1999; and Joanne M. Garvey Award from California Bar Taxation Section on November 7, 2008. Appointed by President Reagan as Judge of the United States Tax Court; sworn in on September 24, 1982 for a term ending September 23, 1997.  Reappointed by President Clinton on November 7, 1997 for a term ending November 6, 2012.  Served as Chief Judge from June 1, 1996 to September 23, 1997 and from November 7, 1997 to May 31, 2000.  Assumed senior status on October 1, 2012 and continues to perform judicial duties as Senior Judge on recall.",
    },
    {
        "first_name": "Joseph Robert",
        "middle_initial": "",
        "last_name": "Goeke",
        "suffix": "",
        "display_name": "Joseph Robert Goeke",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0690",
        "bio": "Senior Judge. Born in Kentucky. B.S., cum laude, Xavier University, 1972; J.D., University of Kentucky, College of Law, 1975, Order of the Coif. Admitted to Illinois and Kentucky Bar, U.S. District Court for the Northern District of Illinois (Trial Bar), U.S. Court of Federal Claims. Trial Attorney, Chief Counsel's Office, Internal Revenue Service, New Orleans, LA, 1975-1980. Senior Trial Attorney, Chief Counsel's Office, Internal Revenue Service, Cincinnati, OH, 1980-85. Special International Trial Attorney, Chief Counsel's Office, Internal Revenue Service, Cincinnati, OH, 1985-1988. Partner, Law Firm of Mayer, Brown, Rowe & Maw, Chicago, IL, 1988 to 2003. Appointed by President Bush as Judge of the United States Tax Court; sworn in on April 22, 2003 for a term ending April 21, 2018. Assumed senior status on April 21, 2018 and continues to perform judicial duties as Senior Judge on recall.",
    },
    {
        "first_name": "David",
        "middle_initial": "",
        "last_name": "Gustafson",
        "suffix": "",
        "display_name": "David Gustafson",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0850",
        "bio": "Senior Judge. Born in South Carolina. Bob Jones University, B.A. summa cum laude, 1978. Duke University School of Law, J.D. with distinction, 1981. Order of the Coif (1981). Executive Editor of the Duke Law Journal (1980-1981). Admitted to the District of Columbia Bar, 1981. Associate at the law firm of Sutherland, Asbill and Brennan, in Washington, D.C., 1981-1983. Trial Attorney (1983-1989), Assistant Chief (1989-2005), and Chief (2005-2008) in the Court of Federal Claims Section of the Tax Division in the U.S. Department of Justice; and Coordinator of Tax Shelter Litigation for the entire Tax Division (2002-2006). Appointed by President George W. Bush as Judge of the United States Tax Court; sworn in on July 29, 2008, for a term ending July 29, 2023. Assumed senior status on November 1, 2022, and continues to perform judicial duties as Senior Judge on recall.<p><strong>Additional Information or Requirements for Law Clerk Applicants:</strong></p><p>LL.M. preferred</p>",
    },
    {
        "first_name": "James",
        "middle_initial": "S.",
        "last_name": "Halpern",
        "suffix": "",
        "display_name": "James S. Halpern",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0707",
        "bio": "Senior Judge. Born in New York. Hackley School, Tarrytown, NY, 1963; Wharton School, B.S., University of Pennsylvania, 1967; J.D., University of Pennsylvania Law School, 1972; LL.M., Taxation, New York University Law School, 1975; Associate Attorney, Mudge, Rose, Guthrie and Alexander, New York City, 1972-74; assistant professor of law, Washington and Lee University, 1975-76; assistant professor of law, St. John's University, New York City, 1976-78, visiting professor, Law School, New York University, 1978-79; associate attorney, Roberts and Holland, New York City, 1979-80; Principal Technical Advisor, Assistant Commissioner (Technical) and Associate Chief Counsel (Technical), Internal Revenue Service, Washington, DC, 1980-83; partner, Baker and Hostetler, Washington, DC, 1983-90; Adjunct Professor, Law School, George Washington University, Washington, DC, 1984-present; Colonel, U.S. Army Reserve (retired). Appointed by President Bush as Judge of the United States Tax Court; sworn in on July 3, 1990 for a term ending July 2, 2005. Reappointed by President Bush; sworn in on November 2, 2005 for a term ending November 1, 2020. Assumed senior status on October 16, 2015 and continues to perform judicial duties as Senior Judge on recall.",
    },
    {
        "first_name": "Mark",
        "middle_initial": "V.",
        "last_name": "Holmes",
        "suffix": "",
        "display_name": "Mark V. Holmes",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0714",
        "bio": "Senior Judge. Born in New York. B.A. Harvard College, 1979; J.D. University of Chicago Law School, 1983. Admitted to New York and District of Columbia Bars; U.S. Supreme Court; DC, Second, Fifth and Ninth Circuits; Southern and Eastern Districts of New York, Court of Federal Claims. Practiced in New York as an Associate, Cahill Gordon & Reindel, 1983-85; Sullivan & Cromwell, 1987-1991; served as Clerk to the Hon. Alex Kozinski, Ninth Circuit, 1985-87; and in Washington as Counsel to Commissioners, United States International Trade Commission, 1991-96; Counsel, Miller & Chevalier, 1996-2001; Deputy Assistant Attorney General, Tax Division, 2001-03. Member, American Bar Association (Litigation and Tax Sections). Appointed by President Bush as Judge of the United States Tax Court; sworn in on June 30, 2003 for a term ending June 29, 2018.  Assumed senior status on June 30, 2018 and continues to perform judicial duties as Senior Judge on recall.",
    },
    {
        "first_name": "Albert",
        "middle_initial": "G.",
        "last_name": "Lauber",
        "suffix": "",
        "display_name": "Albert G. Lauber",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0785",
        "bio": "Senior Judge. Born in New York. Received a Bachelor of Arts degree, summa cum laude, from Yale College, a Master of Arts in Classics from Clare College, Cambridge University, and a Juris Doctor from Yale Law School. Prior to appointment to the Court served as a Law Clerk to Judge Malcolm R. Wilkey of the U.S. Court of Appeals for the D.C. Circuit, and as a Law Clerk to Justice Harry A. Blackmun of the U.S. Supreme Court; worked for the Department of Justice as Tax Assistant to the Solicitor General and as Deputy Solicitor General; was a Partner with Caplin & Drysdale, Chartered; and was the Director, Graduate Tax & Securities Programs, at Georgetown University Law Center. Former professor at Georgetown University Law Center, George Washington University Law School, and the University of Virginia Law School. Appointed by President Obama as Judge of the United States Tax Court; sworn in on January 31, 2013, for a term ending January 30, 2028. Assumed senior status on January 1, 2020, and continues to perform judicial duties as Senior Judge on recall.<p><strong>Additional Information or Requirements for Law Clerk Applicants:</strong></p><p>Must submit resume, J.D. and LL.M. transcripts, two letters of recommendation, and at least one writing sample.</p>",
    },
    {
        "first_name": "L. Paige",
        "middle_initial": "",
        "last_name": "Marvel",
        "suffix": "",
        "display_name": "L. Paige Marvel",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0740",
        "bio": "Senior Judge. Born in Maryland. Education: B.A., magna cum laude, 1971, College of Notre Dame, Baltimore, MD; J.D. with honors, University of Maryland School of Law, Baltimore, MD, 1974 (awarded Order of the Coif).  Garbis & Schwait, P.A., associate 1974-76, and shareholder 1976-85; Garbis, Marvel & Junghans, P.A., shareholder 1985-86; Melnicove, Kaufman, Weiner, Smouse & Garbis, P.A., shareholder 1986-88; Venable, Baetjer & Howard L.L.P., partner, 1988-98. Member, American Bar Association, Section of Taxation, Vice-Chair, Committee Operations, 1993-95; Council Director, 1989-92; Chair, Court Procedure Committee, 1985-87; Maryland State Bar Association, Board of Governors, 1988-90, and 1996-98; Chair, Taxation Section, 1982-83. Fellow, American Bar Foundation; Fellow, Maryland Bar Foundation; Fellow and former Regent, 1996-98, American College of Tax Counsel; Member, American Law Institute; Advisor, ALI Restatement of Law Third-The Law Governing Lawyers 1988-1998; University of Maryland Law School Board of Visitors, 1995-2001; Loyola/Notre Dame Library, Inc. Board of Trustees, 1996-2003; Co-editor, Procedure Department, The Journal of Taxation 1990-98. Member, Commissioner’s Review Panel on IRS Integrity, 1989-91; Member and Chair, Procedure Subcommittee, Commission to Revise the Annotated Code of Maryland, (Tax Provisions), 1981-87; Member, Advisory Commission to the Maryland State Department of Economic and Community Development, 1978-81. Appointed by President Clinton as Judge of the United States Tax Court; sworn in on April 6, 1998 for a term ending April 5, 2013. Reappointed by President Obama; sworn in on December 3, 2014 for a term ending December 2, 2029. Served as Chief Judge from June 1, 2016 to May 31, 2018.  Assumed senior status on December 6, 2019, and continues to perform judicial duties as Senior Judge on recall.",
    },
    {
        "first_name": "Richard",
        "middle_initial": "T.",
        "last_name": "Morrison",
        "suffix": "",
        "display_name": "Richard T. Morrison",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0853",
        "bio": "Senior Judge. Born in Kansas. Received Bachelor of Arts and Bachelor of Science degrees from the University of Kansas, and Juris Doctor and Master of Arts degrees from the University of Chicago. Prior to appointment to the Court served as a Clerk to Judge Jerry E. Smith of the U.S. Court of Appeals for the Fifth Circuit; practiced law with Baker & McKenzie and with Mayer Brown & Platt; and was the Deputy Assistant Attorney General for Appellate and Review for the U.S. Department of Justice’s Tax Division. Appointed by President Bush as Judge of the United States Tax Court; sworn in on August 29, 2008 for a term ending August 28, 2023. Assumed senior status on August 29, 2023, and continues to perform judicial duties as Senior Judge on recall.<p><strong>Application material required:</strong></p><p>Cover letter; resume; at least one writing sample; list of references or reference letters; and unofficial transcripts of (1) undergraduate courses, (2) JD courses, and (3) LLM courses (if applicable).</p>",
    },
    {
        "first_name": "Elizabeth",
        "middle_initial": "Crewson",
        "last_name": "Paris",
        "suffix": "",
        "display_name": "Elizabeth Crewson Paris",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0839",
        "bio": "Senior Judge. Born in Oklahoma. B.S., University of Tulsa, 1980; J.D., University of Tulsa College of Law, 1987; LL.M., Taxation, University of Denver College of Law, 1993. Admitted to the Supreme Court of Oklahoma and U.S. District Court for the District of Oklahoma, 1988; U.S. Tax Court, U.S. Court of Federal Claims, U.S. Court of Appeals for the Tenth Circuit, 1993; Supreme Court of Colorado, 1994. Former partner, Brumley Bishop and Paris, 1992; Senior Associate, McKenna and Cueno, 1994; Tax Partner, Reinhart, Boerner, Van Deuren, Norris and Rieselbach, 1998. Tax Counsel to the United States Senate Finance Committee, 2000-2008. Member of the American Bar Association, Section of Taxation and Real Property and Probate Sections, formerly served as Vice Chair to both Agriculture and Entity Selection Committees. Member of Colorado and Oklahoma Bar Associations. Recognized as Distinguished Alumnus by the University of Tulsa School of law. Author of numerous tax, estate planning, real property, agriculture articles and chapters. Former Adjunct Professor, Georgetown University Law Center, LL.M. Taxation Program, and University of Tulsa College of Law. Appointed by President Bush as Judge of the United States Tax Court; sworn in on July 30, 2008 for a term ending July 29, 2023. Assumed senior status on July 30, 2023, and continues to perform judicial duties as Senior Judge on recall.",
    },
    {
        "first_name": "Michael",
        "middle_initial": "B.",
        "last_name": "Thornton",
        "suffix": "",
        "display_name": "Michael B. Thornton",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0766",
        "bio": "Senior Judge. Born in Mississippi. University of Southern Mississippi, B.S., in Accounting, summa cum laude, 1976; M.S., in Accounting, 1977; M.A., in English Literature, University of Tennessee, 1979; J.D., with distinction, Duke University School of Law, 1982; Order of the Coif, Duke Law Journal Editorial Board. Admitted to District of Columbia Bar, 1982. Served as Law Clerk to the Honorable Charles Clark, Chief Judge, U.S. Court of Appeals for the Fifth Circuit, 1983-84. Practiced law as an Associate Attorney, Sutherland, Asbill and Brennan, Washington, DC, 1982-83, and summer 1981; Miller and Chevalier, Chartered, Washington, DC, 1985-88. Served as Tax Counsel, U.S. House Committee on Ways and Means, 1988-94; Chief Minority Tax Counsel, U.S. House Committee on Ways and Means, January 1995; Attorney-Adviser, U.S. Treasury Department, February-April 1995; Deputy Tax Legislative Counsel in the Office of Tax Policy, United States Treasury Department, April 1995-February 1998. Recipient of Treasury Secretary's Annual Award, U.S. Department of the Treasury, 1997; Meritorious Service Award, U.S. Department of the Treasury, 1998. Appointed by President Clinton as Judge of the United States Tax Court; sworn in on March 8, 1998 for a term ending March 7, 2013. Served as Chief Judge from June 1, 2012, to March 7, 2013 and August 7, 2013 to May 31, 2016. Reappointed by President Obama on August 7, 2013, for a term ending August 6, 2028. Assumed senior status on January 1, 2021, and continues to perform judicial duties as Senior Judge on recall.",
    },
    {
        "first_name": "Juan",
        "middle_initial": "F.",
        "last_name": "Vasquez",
        "suffix": "",
        "display_name": "Juan F. Vasquez",
        "title": "Senior Judge",
        "chambers_telephone": "(202) 521-0778",
        "bio": "Senior Judge. Born in Texas. Attended Fox Tech High School and San Antonio Junior College, A.D. (Data Processing); received B.B.A. (Accounting), University of Texas, Austin, 1972; attended State University of New York, Buffalo in 1st year law school, 1975; J.D., University of Houston Law Center, 1977; LL.M., Taxation, New York University Law School, 1978. Admitted to Texas Bar, 1977. Certified in Tax Law by Texas Board of Legal Specialization, 1984; Certified Public Accountant Certificate from Texas, 1976, and California, 1974. Admitted to United States District Court, Southern District of Texas, 1982, and Western District of Texas, 1985, U.S. Court of Appeals for the Fifth Circuit, 1982; private practice of tax law, in San Antonio, TX, 1987-April 1995; partner, Leighton, Hood and Vasquez, 1982-87, San Antonio, TX; Trial Attorney, Office of Chief Counsel, Internal Revenue Service, Houston, TX, 1978-82; accountant, Coopers and Lybrand, Los Angeles, CA., 1972-74. Member of American Bar Association, Tax Section; Texas State Bar, Tax and Probate Section; Fellow of Texas and San Antonio Bar Foundations, Mexican American Bar Association (MABA) of San Antonio (Treasurer); Houston MABA; Texas MABA (Treasurer); National Association of Hispanic CPA's; San Antonio Chapter (founding member); College of State Bar of Texas, National Hispanic Bar Association; member of Greater Austin Tax Litigation Association; served on Austin Internal Revenue Service District Director's Practitioner Liaison Committee, 1990-91, chairman, 1991. Appointed by President Clinton as Judge of the United States Tax Court; sworn in on May 1, 1995 for a term ending April 30, 2010. Reappointed by President Obama on October 13, 2011 for a term ending October 12, 2026. Assumed senior status on June 24, 2018 and continues to perform judicial duties as Senior Judge on recall.",
    },
    {
        "first_name": "Lewis",
        "middle_initial": "R.",
        "last_name": "Carluzzo",
        "suffix": "",
        "display_name": "Lewis R. Carluzzo",
        "title": "Special Trial Judge",
        "chambers_telephone": "(202) 521-3339",
        "bio": "Special Trial Judge. Born in New Jersey. Received undergraduate and law degrees, Villanova University, 1971 and 1974. Admitted to New Jersey Bar, 1974. Served as law clerk, New Jersey Superior Court Judge. Associated with law firm in Bridgeton, NJ, 1975, also serving as city prosecutor. From 1977 until appointment as Special Trial Judge, employed by the Office of Chief Counsel, Internal Revenue Service, as attorney, Washington, DC, District Counsel's Office. In 1983, appointed Special Trial Attorney on staff of the Associate Chief Counsel, Litigation. From 1992 to 1994, assigned to the Office of Special Counsel, Large Case. Appointed Special Trial Judge of the United States Tax Court, on August 7, 1994. Appointed Chief Special Trial Judge effective September 1, 2017.",
    },
    {
        "first_name": "Zachary",
        "middle_initial": "S.",
        "last_name": "Fried",
        "suffix": "",
        "display_name": "Zachary S. Fried",
        "title": "Special Trial Judge",
        "chambers_telephone": "(202) 521-0867",
        "bio": "Special Trial Judge Fried holds a B.A. from the University of Virginia, a J.D. from George Washington University Law School, and an LL.M in Taxation from Georgetown University Law Center. Before his appointment, he served as Attorney-Adviser to Chief Special Trial Judge Lewis R. Carluzzo and as Deputy Counsel to the Chief Judge. Prior professional experience included working as an Attorney with the Apartment and Office Building Association of Metropolitan Washington.<p>He is a member of the District of Columbia Bar, United States Tax Court Bar, and American Bar Association.</p><p>Appointed Special Trial Judge of the United States Tax Court on October 10, 2023.</p>",
    },
    {
        "first_name": "Diana",
        "middle_initial": "L.",
        "last_name": "Leyden",
        "suffix": "",
        "display_name": "Diana L. Leyden",
        "title": "Special Trial Judge",
        "chambers_telephone": "(202) 521-0823",
        "bio": "Special Trial Judge. Born in New York; Sachem High School, 1972; Union College, Schenectady, NY, B.A. magna cum laude,1978; UConn Law School, Hartford, CT, J.D. 1982; Georgetown University Law Center, LL.M. Taxation 1984. Admitted to Connecticut Bar (1982), District of Columbia Bar (1982, inactive) and Massachusetts Bar (1985, inactive); Admitted to U.S. Court of Federal Claims (1983); United States District Court for the District of Connecticut, 2001; United States Court of Appeals for the Second Circuit, 2003; Member of the American Bar Association, Tax Section; Recipient of the American Bar Association Tax Section Janet Spragens Pro Bono Award (2005); former chair of the ABA Tax Section Low Income Taxpayer Committee; United States Tax Court (law clerk to Judge Herbert Chabot) (1982-1984); Steptoe & Johnson (1984-1985); Powers and Hall (1985-1987); Day, Berry & Howard (1987-1988); Massachusetts Department of Revenue (1988-1995); Connecticut Department of Revenue Services (1995-1997); UConn Law School Tax Clinic (1999-2015); New York City Department of Finance Taxpayer Advocate (2015-2016). Appointed Special Trial Judge of the United States Tax Court on June 20, 2016.",
    },
    {
        "first_name": "Peter",
        "middle_initial": "J.",
        "last_name": "Panuthos",
        "suffix": "",
        "display_name": "Peter J. Panuthos",
        "title": "Special Trial Judge",
        "chambers_telephone": "(202) 521-4707",
        "bio": "Special Trial Judge. Born in New York. Attended public schools in New York City; graduated from Erasmus Hall High School, 1961; attended Bernard Baruch School of Business of CUNY, B.S., Bryant College, Providence, RI, 1966; J.D., Suffolk University Law School, Boston, MA, 1969; LL.M., Taxation, Boston University School of Law, 1972; member of the Law Review. Admitted to Supreme Judicial Court of Massachusetts, District of Columbia Bar and United States Supreme Court; member of American Bar Association, Federal Bar Association, Inns of Court. Trial Attorney and Assistant District Counsel, Boston Office of Chief Counsel, Internal Revenue Service, 1970-83. Appointed Special Trial Judge, United States Tax Court, on June 12, 1983. Works with clinical and pro bono programs throughout the country. Works with the American Bar Association and appropriate committees to assist low income litigants. Participant and speaker at conferences relating to procedural matters, clinical and pro bono programs. Taught Tax Procedure and substantive tax courses as an adjunct professor, at Bentley College in Boston and the Catholic University of America, Columbus School of Law. Currently teaches at David A. Clarke School of Law, University of District of Columbia and Georgetown University Law School. Received the J. Edgar Murdock Award for distinguished service to the United States Tax Court, 2012. Recipient of the 2014 Janet R. Spragens Pro Bono Award from the American Bar Association, Section of Taxation for outstanding sustained achievement and commitment in pro bono activities. Served as Chief Special Trial Judge from June 1, 1992, to August 31, 2017.",
    },
    {
        "first_name": "Jennifer",
        "middle_initial": "E.",
        "last_name": "Siegel",
        "suffix": "",
        "display_name": "Jennifer E. Siegel",
        "title": "Special Trial Judge",
        "chambers_telephone": "(202) 521-0720",
        "bio": "Special Trial Judge Siegel holds a B.A. from Barnard College, an M.B.A. from the Drucker School of Management at Claremont Graduate University, a J.D. from the University of San Francisco School of Law, and an LL.M. in Taxation from New York University School of Law.<p>Prior to her appointment, she served the Court as Attorney-Adviser to Special Trial Judge Robert N. Armen, Jr. (2006-2009), an Assistant Deputy Counsel to the Chief Judge (2009-2017), Deputy Clerk of the Court (2017-2019), and Public Affairs Counsel (2019-2023). Prior professional experience included work in private practice and as a certified mediator.</p><p>Appointed Special Trial Judge of the United States Tax Court on September 11, 2023.</p>",
    },
]


class JudgesPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)
        self.slug = "judges"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            self.logger.write("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Judges"

        if Page.objects.filter(slug=self.slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        judge_collection = JudgeCollection.objects.create(name="Judges")
        senior_judge_collection = JudgeCollection.objects.create(name="Senior Judges")
        special_trial_judge_collection = JudgeCollection.objects.create(
            name="Special Trial Judges"
        )

        for judge in all_judges:
            JudgeProfile.objects.update_or_create(
                first_name=judge["first_name"],
                middle_initial=judge["middle_initial"],
                last_name=judge["last_name"],
                suffix=judge["suffix"],
                defaults={
                    "display_name": judge["display_name"],
                    "title": judge["title"],
                    "chambers_telephone": judge["chambers_telephone"],
                    "bio": judge["bio"],
                },
            )

        # Create judge role
        JudgeRole.objects.update_or_create(
            role_name="Chief Judge",
            defaults={
                "judge": JudgeProfile.objects.filter(
                    last_name__iexact="Kerrigan"
                ).first()
            },
        )

        JudgeRole.objects.update_or_create(
            role_name="Chief Special Trial Judge",
            defaults={
                "judge": JudgeProfile.objects.filter(
                    last_name__iexact="Carluzzo"
                ).first()
            },
        )

        # Create the page first
        _ = home_page.add_child(
            instance=JudgeIndex(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description=title,
                body=[
                    {
                        "type": "columns",
                        "value": {
                            "column": [
                                [  # First column
                                    {
                                        "type": "h2WithAnchorTag",
                                        "value": {
                                            "text": "Judges",
                                            "anchortag": "JUDGES",
                                        },
                                    },
                                    {
                                        "type": "judgeCollection",
                                        "value": judge_collection.id,
                                    },
                                ],
                                [  # Second column
                                    {
                                        "type": "h2WithAnchorTag",
                                        "value": {
                                            "text": "Senior Judges",
                                            "anchortag": "SENIOR",
                                        },
                                    },
                                    {
                                        "type": "judgeCollection",
                                        "value": senior_judge_collection.id,
                                    },
                                ],
                                [  # Third column
                                    {
                                        "type": "h2WithAnchorTag",
                                        "value": {
                                            "text": "Special Trial Judges",
                                            "anchortag": "SPECIAL",
                                        },
                                    },
                                    {
                                        "type": "judgeCollection",
                                        "value": special_trial_judge_collection.id,
                                    },
                                ],
                            ]
                        },
                    }
                ],
            )
        )

        self.logger.write(f"Created the '{title}' page with judge collections.")
