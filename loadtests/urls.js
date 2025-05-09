const urls = [
  '/',
  '/redirect/',
  '/mission/',
  '/history/',
  '/reports-and-statistics/',
  '/judges/',
  '/employment/',
  '/employment/vacancy-announcements/',
  '/employment/law-clerk-program/',
  '/holidays/',
  '/zoomgov/',
  '/administrative-orders/',
  '/rules/',
  '/petitioners/',
  '/clinics/',
  '/practitioners/',
  '/petitioners-start/',
  '/petitioners-about/',
  '/petitioners-during/',
  '/petitioners-before/',
  '/petitioners-after/',
  '/petitioners-glossary/',
  '/zoomgov-the-basics/',
  '/zoomgov-zoomgov-proceedings/',
  '/zoomgov-getting-ready/',
  '/jcdp/',
  '/clinics-academic/',
  '/clinics-academic-non-law-school/',
  '/clinics-nonacademic/',
  '/clinics-calendar-call/',
  '/clinics-chief-counsel/',
  '/notices-of-rule-amendments/',
  '/case-procedure/',
  '/jcdp-orders-issued/',
  '/rules-comments/',
  '/citation-and-style-manual/',
  '/transcripts-and-copies/',
  '/pamphlets/',
  '/dawson/',
  '/efile-a-petition/',
  '/pay-filing-fee/',
  '/merging-files/',
  '/dashboard/',
  '/update-contact-information/',
  '/find-a-case/',
  '/find-an-order/',
  '/find-an-opinion/',
  '/dawson-faqs-basics/',
  '/dawson-tou/',
  '/definitions/',
  '/documents-eligible-for-efiling/',
  '/notice-regarding-privacy/',
  '/release-notes/',
  '/dawson-user-guides/',
  '/dawson-petitioner-registration/',
  '/dawson-account-practitioner/',
  '/case-related-forms/',
  '/forms-instructions/',
  '/dawson-faqs-searches-public-access/',
  '/dawson-faqs-account-management/',
  '/dawson-faqs-training-and-support/'
];

// Initialize failedUrls array
let failedUrls = [];

module.exports = {
  getRandomUrl: function(context, events, done) {
    const randomIndex = Math.floor(Math.random() * urls.length);
    context.vars.url = urls[randomIndex];
    return done();
  },

  afterResponse: function(requestParams, response, context, ee, next) {
    if (response.statusCode !== 200) {
      const failedUrl = requestParams.url;
      console.error(`500 error for URL: ${failedUrl}`);
      failedUrls.push(failedUrl);

      // Log unique failed URLs at the end of the test
      if (context.vars.__phase === 'done') {
        console.log('\n=== Failed URLs Summary ===');
        console.log([...new Set(failedUrls)]);
      }
    }
    return next();
  }
};
