describe('Process and Timeline Page - Detailed Timeline controls', () => {
  // Scoped to the page so it doesn't also match the print copy appended to <body>.
  const timeline = '#main-content .detailed-timeline-rectangle';
  const content = `${timeline} .detailed-timeline-accordion-content`;
  const printHost = '.detailed-timeline-print-host';

  const openStates = ($contents: JQuery<HTMLElement>) =>
    [...$contents].map((el) => !el.classList.contains('hidden'));

  beforeEach(() => {
    cy.visit('/petitioners-timeline/');
    cy.get(content).should('have.length.greaterThan', 1);
  });

  it('expands and collapses every phase with Expand All / Collapse All', () => {
    cy.get('.detailed-timeline-expand-button')
      .as('expandButton')
      .should('contain', 'Expand All')
      .and('have.attr', 'aria-expanded', 'false');

    cy.get('@expandButton').click();
    cy.get(content).each(($el) => expect($el).not.to.have.class('hidden'));
    cy.get('@expandButton')
      .should('contain', 'Collapse All')
      .and('have.attr', 'aria-expanded', 'true');

    cy.get('@expandButton').click();
    cy.get(content).each(($el) => expect($el).to.have.class('hidden'));
    cy.get('@expandButton')
      .should('contain', 'Expand All')
      .and('have.attr', 'aria-expanded', 'false');
  });

  it('prints a fully expanded copy without changing the on-page timeline', () => {
    // Open the second phase and tick its first task so we can check state is preserved.
    cy.get(`${timeline} .detailed-timeline-accordion-header`).eq(1).click();
    cy.get(content).eq(1).find('input[type="checkbox"]').first().check({ force: true });

    cy.get(content).then(($contents) => {
      const before = openStates($contents);

      cy.window().then((win) => {
        cy.stub(win, 'print').as('print');
      });
      cy.get('.detailed-timeline-print-button')
        .should('contain', 'Print Detailed Timeline')
        .click();
      cy.get('@print').should('have.been.calledOnce');

      cy.get(printHost).within(() => {
        cy.get('.detailed-timeline-accordion-content').each(($el) =>
          expect($el).not.to.have.class('hidden'),
        );
        cy.get('.detailed-timeline-accordion-content')
          .eq(1)
          .find('input[type="checkbox"]')
          .first()
          .should('be.checked');
        cy.get('[id]').should('not.exist');
      });
      cy.get('body').should('have.class', 'printing-detailed-timeline');

      cy.get(content).then(($after) => {
        expect(openStates($after)).to.deep.equal(before);
      });
      cy.get(content).eq(1).find('input[type="checkbox"]').first().should('be.checked');
    });

    cy.window().then((win) => win.dispatchEvent(new Event('afterprint')));
    cy.get(printHost).should('not.exist');
    cy.get('body').should('not.have.class', 'printing-detailed-timeline');
  });
});
