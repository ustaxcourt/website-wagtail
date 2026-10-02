describe('Process and Timeline Page - Detailed Timeline controls', () => {
  // Scoped to the page so it doesn't also match the print copy appended to <body>.
  const timeline = '#main-content .detailed-timeline-rectangle';
  const content = `${timeline} .detailed-timeline-accordion-content`;
  const accordionHeader = `${timeline} .detailed-timeline-accordion-header`;
  const accordionButton = `${timeline} .detailed-timeline-accordion-header-button`;
  const accordionIcon = `${timeline} .detailed-timeline-accordion-icon`;
  const expandButton = `${timeline} .detailed-timeline-expand-button`;
  const printHost = '.detailed-timeline-print-host';

  const openStates = ($contents: JQuery<HTMLElement>) =>
    [...$contents].map((el) => !el.classList.contains('hidden'));

  beforeEach(() => {
    cy.visit('/petitioners-timeline/');
    cy.get(content).should('have.length.greaterThan', 1);
  });

  it('expands and collapses every phase with Expand All / Collapse All', () => {
    cy.get(expandButton)
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

  it('keeps the control and accordion indicators synchronized with individual toggles', () => {
    cy.get(content).each(($el) => expect($el).to.have.class('hidden'));
    cy.get(accordionButton).each(($el) =>
      expect($el).to.have.attr('aria-expanded', 'false'),
    );
    cy.get(accordionIcon).each(($el) => expect($el).not.to.have.class('rotated'));

    cy.get(accordionHeader).first().click();
    cy.get(content).first().should('not.have.class', 'hidden');
    cy.get(accordionButton).first().should('have.attr', 'aria-expanded', 'true');
    cy.get(accordionIcon).first().should('have.class', 'rotated');
    cy.get(expandButton)
      .should('contain', 'Expand All')
      .and('have.attr', 'aria-expanded', 'false');

    cy.get(accordionHeader).then(($headers) => {
      for (let index = 1; index < $headers.length; index += 1) {
        cy.get(accordionHeader).eq(index).click();
      }
    });
    cy.get(content).each(($el) => expect($el).not.to.have.class('hidden'));
    cy.get(expandButton)
      .should('contain', 'Collapse All')
      .and('have.attr', 'aria-expanded', 'true');

    cy.get(accordionHeader).first().click();
    cy.get(content).first().should('have.class', 'hidden');
    cy.get(accordionButton).first().should('have.attr', 'aria-expanded', 'false');
    cy.get(accordionIcon).first().should('not.have.class', 'rotated');
    cy.get(expandButton)
      .should('contain', 'Expand All')
      .and('have.attr', 'aria-expanded', 'false');
  });

  it('restores expanded sections when returning with browser Back', () => {
    cy.get(accordionHeader).eq(1).click();
    cy.get(accordionHeader).eq(3).click();
    cy.get(content).then(($contents) => {
      const beforeNavigation = openStates($contents);

      cy.visit('/petitioners-guidance/');
      cy.go('back');

      cy.get(content).should(($restoredContents) => {
        expect(openStates($restoredContents)).to.deep.equal(beforeNavigation);
      });
      cy.get(accordionButton).eq(1).should('have.attr', 'aria-expanded', 'true');
      cy.get(accordionButton).eq(3).should('have.attr', 'aria-expanded', 'true');
      cy.get(expandButton)
        .should('contain', 'Expand All')
        .and('have.attr', 'aria-expanded', 'false');
    });
  });

  it('restores expanded sections when returning with browser Forward', () => {
    cy.visit('/petitioners-guidance/');
    cy.visit('/petitioners-timeline/');
    cy.get(accordionHeader).eq(2).click();
    cy.get(accordionHeader).eq(5).click();

    cy.go('back');
    cy.location('pathname').should('eq', '/petitioners-guidance/');
    cy.go('forward');

    cy.get(content).should(($contents) => {
      const open = openStates($contents);
      expect(open[2]).to.equal(true);
      expect(open[5]).to.equal(true);
      expect(open.filter(Boolean)).to.have.length(2);
    });
    cy.get(expandButton)
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
