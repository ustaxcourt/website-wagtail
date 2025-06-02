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


export function checkA11y() {
  cy.injectAxe();

  cy.checkA11y(
    undefined,
    {
      includedImpacts: ['serious', 'critical'],
      retries: 3,
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
    const headerStyles = {
        h1: { fontFamily: 'Noto Serif JP', fontSize: '32px', lineHeight: '40px' },
        'h2:not(footer h2)': { fontFamily: 'Noto Serif JP', fontSize: '24px', lineHeight: '30px' },
        'footer h2': { fontFamily: 'Noto Serif JP', fontSize: '20px', lineHeight:'normal'},
        h3: { fontFamily: 'Source Sans Pro', fontSize: '20px', lineHeight: '25px' },
        h4: { fontFamily: 'Source Sans Pro', fontSize: '17px', lineHeight: '24px' },
    };
    Object.entries(headerStyles).forEach(([header, styles]) => {
        cy.get('body').then(($body) => {
            if ($body.find(header).length === 0) {
                cy.log(`⚠️ Skipping ${header} checks: No ${header} elements found.`);
                return;
            }
            cy.get(header).each(($el) => {
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

Cypress.Commands.add('fixStatusPageIframe', () => {
    cy.window().then((win) => {
        let attempts = 0;
        const maxAttempts = 10;
        const interval = setInterval(() => {
            const iframe = win.document.querySelector('iframe[src*="statuspage.io/embed/frame"]');
            if (iframe) {
                iframe.removeAttribute('tabindex');
                clearInterval(interval);
            }
            if (++attempts >= maxAttempts) {
                clearInterval(interval);
            }
        }, 500);
    });
});
