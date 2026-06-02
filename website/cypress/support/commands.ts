// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
import { Result } from 'axe-core';

declare global {
  namespace Cypress {
    interface Chainable {
      adminLogin(username: string, password: string): Chainable<void>;
    }
  }
}

const isLocalhost = (): boolean => {
  const baseUrl = Cypress.config('baseUrl') || '';
  return baseUrl.includes('localhost') || baseUrl.includes('127.0.0.1');
};

// Note: in AWS deployments the app will default to SSO login, so to run tests
// against aws environments we specifically visit the "local-login" instead.
Cypress.Commands.add('adminLogin', (username: string, password: string) => {
    const loginPath = isLocalhost() ? '/admin/login/' : '/admin/local-login/';
  cy.visit(loginPath);
  cy.get('input[name="username"]').type(username);
  cy.get('input[name="password"]').type(password, { log: false });
  cy.get('button[type="submit"], input[type="submit"]').click();
cy.url({ timeout: 10000 }).should((url) => {
    expect(url).to.include('/admin/');
    expect(url).not.to.include('/admin/login');
    expect(url).not.to.include('/admin/local-login');
  });
});

export function terminalLog(violations: Result[]): void {
  const violationData = violations.map(
    ({ description, id, impact, nodes }) => ({
      description,
      id,
      impact,
      nodes: nodes.length,
    }),
  );

  cy.task('table', violationData);
}


export function checkA11y(context?: any, options: Record<string, unknown> = {}) {
  cy.injectAxe();
  // hack: tweak any statuspage.io message so it doesn't cause A11y test to fail
  fixStatusPageIframe();
    cy.checkA11y(
        context,
        {
            includedImpacts: ['serious', 'critical'],
            retries: 3,
            ...options,
        },
        terminalLog,
    );
}

export function checkHeaderOrder() {
    const headers = ['h1', 'h2', 'h3', 'h4'];
    cy.document().then((doc) => {
        const headerElements = Array.from(doc.querySelectorAll(headers.join(',')));
        if (headerElements.length === 0) {
            cy.log('No headers found, skipping order check.');
            return;
        }
        let lastLevel = 0;
        headerElements.forEach((header) => {
            const currentLevel = parseInt(header.tagName.replace('H', ''), 10);
            if (currentLevel < lastLevel) {
                throw new Error(
                    `Header order violation: ${header.tagName} appears after a higher-level header (${headers[lastLevel - 1].toUpperCase()})`
                );
            }
            lastLevel = currentLevel;
        });
    });
}

export function checkHeaderStyles() {
    cy.viewport('iphone-x'); // Check mobile first
    cy.wait(100); // Allow styles to recompute

    const pSelector = 'p:not(.usa-banner__header-action):not(.usa-banner__header-text)';

    const mobileStyles = {
        h1: { fontFamily: 'Source Sans 3', fontSize: '24px', lineHeight: '32px' },
        h2: { fontFamily: 'Source Sans 3', fontSize: '20px', lineHeight: '22px' },
        h3: { fontFamily: 'Source Sans 3', fontSize: '18px', lineHeight: '20px' },
        [pSelector]: { fontFamily: 'Source Sans 3', fontSize: '16px', lineHeight: '20px' },
    };

    Object.entries(mobileStyles).forEach(([selector, styles]) => {
        cy.get('body').then(($body) => {
            if ($body.find(selector).length === 0) {
                cy.log(`⚠️ Skipping ${selector} checks (mobile): No ${selector} elements found.`);
                return;
            }
            cy.get(selector).first().then(($el) => {
                cy.wrap($el).should('have.css', 'font-family').then((fontFamily) => {
                    const fontFamilyString = String(fontFamily);
                    expect(fontFamilyString.toLowerCase()).to.include(styles.fontFamily.toLowerCase());
                });
                cy.wrap($el).should('have.css', 'font-size').then((fontSize) => {
                    expect(fontSize).to.eq(styles.fontSize);
                });
                cy.wrap($el).should('have.css', 'line-height').then((lineHeight) => {
                    expect(lineHeight).to.eq(styles.lineHeight);
                });
            });
        });
    });

    // Check desktop/tablet
    cy.viewport(1280, 720);
    cy.wait(100); // Allow styles to recompute

    const desktopStyles = {
        h1: { fontFamily: 'Source Sans 3', fontSize: '32px', lineHeight: '38px' },
        h2: { fontFamily: 'Source Sans 3', fontSize: '24px', lineHeight: '30px' },
        h3: { fontFamily: 'Source Sans 3', fontSize: '20px', lineHeight: '25px' },
        [pSelector]: { fontFamily: 'Source Sans 3', fontSize: '17px', lineHeight: '20px' },
    };

    Object.entries(desktopStyles).forEach(([selector, styles]) => {
        cy.get('body').then(($body) => {
            if ($body.find(selector).length === 0) {
                cy.log(`⚠️ Skipping ${selector} checks (desktop): No ${selector} elements found.`);
                return;
            }
            cy.get(selector).first().then(($el) => {
                cy.wrap($el).should('have.css', 'font-family').then((fontFamily) => {
                    const fontFamilyString = String(fontFamily);
                    expect(fontFamilyString.toLowerCase()).to.include(styles.fontFamily.toLowerCase());
                });
                cy.wrap($el).should('have.css', 'font-size').then((fontSize) => {
                    expect(fontSize).to.eq(styles.fontSize);
                });
                cy.wrap($el).should('have.css', 'line-height').then((lineHeight) => {
                    expect(lineHeight).to.eq(styles.lineHeight);
                });
            });
        });
    });
}

export function fixStatusPageIframe(): void {
    cy.window().then((win) => {
        let attempts = 0;
        const maxAttempts = 10;
        const interval = setInterval(() => {
            const iframe = win.document.querySelector('iframe[src*="statuspage.io/embed/frame"]');
            if (iframe) {
                iframe.removeAttribute('tabindex');
                clearInterval(interval);
                return;
            }
            if (++attempts >= maxAttempts) {
                clearInterval(interval);
            }
        }, 500);
    });
}
