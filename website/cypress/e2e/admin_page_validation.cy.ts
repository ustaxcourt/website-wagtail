/**
 * Admin Page Edit Validation
 *
 * This test logs into the Wagtail admin, navigates to the pages listing,
 * expands the Home page children, and tests each page for editability.
 */

describe('Admin Page Edit Validation', () => {
  const ADMIN_USERNAME = 'admin';
  const ADMIN_PASSWORD = 'ustcAdminPW!';

  let allPages: any[] = [];
  let testResults: Array<{
    pageId: string;
    title: string;
    slug?: string;
    status: 'success' | 'failed';
    error?: string;
  }> = [];

  it('logs in and collects all page IDs from admin interface', () => {
    // Login to admin first
    cy.visit('/admin/login/');
    cy.get('input[name="username"]').type(ADMIN_USERNAME);
    cy.get('input[name="password"]').type(ADMIN_PASSWORD);
    cy.get('button[type="submit"], input[type="submit"]').click();
    cy.url({ timeout: 10000 }).should('include', '/admin/');

    // Now collect pages
    // Function to collect pages with pagination
    const collectAllPages = (url: string, allPages: any[] = []): Cypress.Chainable<any[]> => {
      return cy.request({
        url: url,
        headers: {
          'Accept': 'application/json'
        }
      }).then((response) => {
        expect(response.status).to.eq(200);

        const pages = response.body.items || response.body.results || [];
        const updatedPages = [...allPages, ...pages];


        // Check if we have more pages to collect
        const totalCount = response.body.meta?.total_count || response.body.count || pages.length;
        const hasMore = updatedPages.length < totalCount;

        if (hasMore) {
          // Calculate next page parameters
          const currentOffset = updatedPages.length;
          const limit = pages.length || 20;
          const nextUrl = `/admin/api/main/pages/?offset=${currentOffset}&limit=${limit}`;

          return collectAllPages(nextUrl, updatedPages);
        } else {
          return cy.wrap(updatedPages);
        }
      });
    };

    // Start collecting from all pages (no child_of filter to get all pages)
    collectAllPages(`/admin/api/main/pages/`).then((pages) => {
      allPages = pages.filter((page: any) => page.id > 1); // Exclude root page
      expect(allPages.length).to.be.greaterThan(0, 'Should find pages to test');

      // Test each page sequentially using cy.wrap and .each()
      cy.wrap(allPages).each((page: any) => {
      const pageId = page.id.toString();

      // Extract slug and title from the page data we already have
      const slug = page.meta?.slug || page.slug || page.url_path?.split('/').filter(Boolean).pop() || `page-${pageId}`;
      const title = page.title || page.meta?.seo_title || `Page ${pageId}`;

      // Visit the edit page directly with retry logic
      cy.visit(`/admin/pages/${pageId}/edit/`, {
        timeout: 15000,
        failOnStatusCode: false
      });

      // Wait for page to stabilize
      cy.wait(500);

      // Check response status and content
      cy.url().then((currentUrl) => {
        let status: 'success' | 'failed' = 'success';
        let error: string | undefined;

        if (!currentUrl.includes('/edit/')) {
          status = 'failed';
          error = 'Page redirected or failed to load edit interface';
        } else {
          // Check page content for errors
          cy.get('body').then(($body) => {
            // Check if redirected to login (indicates auth failure)
            if ($body.find('input[name="username"], input[name="password"]').length > 0) {
              status = 'failed';
              error = 'Redirected to login - authentication issue';
            } else {
              // Check for actual error pages by looking at more specific indicators
              const hasErrorPage = $body.find('h1').text().includes('Server Error') ||
                                   $body.find('h1').text().includes('Not Found') ||
                                   $body.find('.error-page, .server-error').length > 0;

              const hasWagtailEditForm = $body.find('form[action*="/edit/"], .page-editor, .tab-nav, input[name="title"], input[name="slug"]').length > 0;
              const hasSubmitButton = $body.find('button[type="submit"], input[type="submit"]').length > 0;

              if (hasErrorPage) {
                status = 'failed';
                error = 'Error page detected';
              } else if (!hasWagtailEditForm) {
                status = 'failed';
                error = 'No Wagtail edit form found on page';
              } else if (!hasSubmitButton) {
                status = 'failed';
                error = 'Edit form missing submit button';
              }
              // If we reach here with no errors, status remains 'success'
            }

            // Print result to STDOUT immediately with color formatting
            const statusText = status === 'success' ? 'Editable' : `Not Editable (${error})`;
            const coloredOutput = status === 'success'
              ? `Page ID: ${pageId}, Slug: ${slug}. ${statusText}.`
              : `\x1b[31mPage ID: ${pageId}, Slug: ${slug}. ${statusText}\x1b[0m`;
            cy.task('log', coloredOutput);

            // Record result
            testResults.push({
              pageId,
              title,
              slug,
              status,
              error
            });
          });
        }
      });
      }).then(() => {
        // After all pages are tested, check if any failed and fail the test
        const failedPages = testResults.filter(r => r.status === 'failed');
        if (failedPages.length > 0) {
          const failedList = failedPages.map(p => `${p.pageId} (${p.slug}): ${p.error}`).join(', ');
          throw new Error(`${failedPages.length} pages are not editable: ${failedList}`);
        }
      });
    });
  });

  after(() => {
    // Generate comprehensive report
    const total = testResults.length;
    const successful = testResults.filter(r => r.status === 'success').length;
    const failed = testResults.filter(r => r.status === 'failed').length;
    const successRate = total > 0 ? Math.round((successful / total) * 100) : 0;

    // Group failures by error type
    const errorGroups: Record<string, typeof testResults> = {};
    testResults.filter(r => r.status === 'failed').forEach(result => {
      const errorType = result.error?.split(' - ')[0] || 'Unknown error';
      if (!errorGroups[errorType]) {
        errorGroups[errorType] = [];
      }
      errorGroups[errorType].push(result);
    });

    // Console output
    console.log('\n' + '='.repeat(80));
    console.log('ADMIN PAGE EDIT VALIDATION RESULTS');
    console.log('='.repeat(80));
    console.log(`Total pages tested: ${total}`);
    console.log(`Successfully editable: ${successful}`);
    console.log(`Failed to edit: ${failed}`);
    console.log(`Success rate: ${successRate}%`);
    console.log('='.repeat(80));

    if (failed > 0) {
      console.log('\nFAILED PAGES:');
      console.log('-'.repeat(40));

      Object.entries(errorGroups).forEach(([errorType, results]) => {
        console.log(`\n${errorType} (${results.length} pages):`);
        results.slice(0, 10).forEach(result => {
          console.log(`  - ${result.title} (ID: ${result.pageId}, Slug: ${result.slug || 'unknown'})`);
        });
        if (results.length > 10) {
          console.log(`  ... and ${results.length - 10} more`);
        }
      });
    }

    // Log final results
    console.log(`\n✅ Admin edit validation completed! ${successRate}% success rate.`);

    // Only fail if no pages were found at all
    if (total === 0) {
      console.log('\n❌ No pages were found to test.');
      throw new Error('No pages found to test');
    }
  });
});
