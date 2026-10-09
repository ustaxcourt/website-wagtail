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
    Array.from($contents).map((el) => !el.classList.contains('hidden'));

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

  it('renders the expand and print button icons', () => {
    [
      [`.detailed-timeline-expand-button-icon`, 'visibility.svg'],
      [`.detailed-timeline-print-button-icon`, 'print.svg'],
    ].forEach(([iconSelector, iconFile]) => {
      cy.get(`${timeline} ${iconSelector}`).should(($icon) => {
        const styles = window.getComputedStyle($icon[0]);
        const bounds = $icon[0].getBoundingClientRect();
        expect(bounds.width).to.be.greaterThan(0);
        expect(bounds.height).to.be.greaterThan(0);
        expect(styles.maskImage).to.contain(iconFile);
      });
    });
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
      cy.get(`${timeline} .detailed-timeline-accordion-header`).eq(1).then(($sourceHeader) => {
        const sourceStyles = window.getComputedStyle($sourceHeader[0]);
        cy.get(`${printHost} .detailed-timeline-accordion-header`).eq(1).then(($printHeader) => {
          const printStyles = window.getComputedStyle($printHeader[0]);
          expect(printStyles.backgroundColor).to.equal(sourceStyles.backgroundColor);
          expect(printStyles.borderRadius).to.equal(sourceStyles.borderRadius);
          expect(printStyles.borderTopWidth).to.equal(sourceStyles.borderTopWidth);
        });
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

/**
 * Try to fake-out sessionStorage / history.state with the following scenarios.
 * 1. Click sections 1 and 3, then Expand All, then Collapse All, then reload. Every section should stay collapsed.
 * 2. The same sequence, but go Back instead of reloading.
 * 3. Open and close section 2, click Expand All, then reload. Every section should stay expanded.
 * 4. Open every section by clicking it, click Collapse All, then reload. The Expand All / Collapse All label should match what's actually open.
 */
describe('Process and Timeline Page - Expand All / Collapse All state after reload or Back', () => {
  const timeline = '#main-content .detailed-timeline-rectangle';
  const content = `${timeline} .detailed-timeline-accordion-content`;
  const accordionHeader = `${timeline} .detailed-timeline-accordion-header`;
  const expandButton = `${timeline} .detailed-timeline-expand-button`;

  const openStates = ($contents: JQuery<HTMLElement>) =>
   Array.from($contents).map((el) => !el.classList.contains('hidden'));

  beforeEach(() => {
    cy.visit('/petitioners-timeline/');
    cy.get(content).should('have.length.greaterThan', 3);
  });

  it('keeps sections collapsed after Collapse All and a reload', () => {
    // Individual clicks write sessionStorage = "true" for sections 1 and 3.
    cy.get(accordionHeader).eq(1).click();
    cy.get(accordionHeader).eq(3).click();

    cy.get(expandButton).click(); // Expand All
    cy.get(expandButton).should('contain', 'Collapse All').click(); // Collapse All
    cy.get(content).each(($el) => expect($el).to.have.class('hidden'));

    cy.reload();

    cy.get(content).should(($contents) => {
      expect(openStates($contents).filter(Boolean)).to.have.length(0);
    });
  });

  it('keeps sections collapsed after Collapse All and returning with Back', () => {
    cy.get(accordionHeader).eq(1).click();
    cy.get(accordionHeader).eq(3).click();

    cy.get(expandButton).click();
    cy.get(expandButton).should('contain', 'Collapse All').click();
    cy.get(content).each(($el) => expect($el).to.have.class('hidden'));

    cy.visit('/petitioners-guidance/');
    cy.go('back');

    cy.get(content).should(($contents) => {
      expect(openStates($contents).filter(Boolean)).to.have.length(0);
    });
  });

  it('keeps every section expanded after Expand All and a reload', () => {
    // Open then close section 2 individually, so sessionStorage holds "false" for it.
    cy.get(accordionHeader).eq(2).click();
    cy.get(accordionHeader).eq(2).click();

    cy.get(expandButton).should('contain', 'Expand All').click();
    cy.get(content).each(($el) => expect($el).not.to.have.class('hidden'));

    cy.reload();

    cy.get(content).should(($contents) => {
      expect(openStates($contents).every(Boolean)).to.equal(true);
    });
  });

  it('shows a control label that matches the sections after a reload', () => {
    // Open every section individually so each one has sessionStorage = "true".
    cy.get(accordionHeader).then(($headers) => {
      for (let index = 0; index < $headers.length; index += 1) {
        cy.get(accordionHeader).eq(index).click();
      }
    });
    cy.get(expandButton).should('contain', 'Collapse All').click();
    cy.get(content).each(($el) => expect($el).to.have.class('hidden'));

    cy.reload();

    // Whichever state wins, the label must agree with it.
    cy.get(content).then(($contents) => {
      const allOpen = openStates($contents).every(Boolean);
      cy.get(expandButton)
        .should('contain', allOpen ? 'Collapse All' : 'Expand All')
        .and('have.attr', 'aria-expanded', String(allOpen));
    });
  });
});

describe('Process and Timeline Page - accordion state per history entry', () => {
  const timeline = '#main-content .detailed-timeline-rectangle';
  const content = `${timeline} .detailed-timeline-accordion-content`;
  const accordionHeader = `${timeline} .detailed-timeline-accordion-header`;

  const openStates = ($contents: JQuery<HTMLElement>) =>
    Array.from($contents).map((el) => !el.classList.contains('hidden'));

  it('restores the state of the visit being returned to, not a later visit to the same page', () => {
    // First visit: open phase 1.
    cy.visit('/petitioners-timeline/');
    cy.get(accordionHeader).eq(1).click();
    cy.get(content).eq(1).should('not.have.class', 'hidden');

    // Leave, then come back with a fresh visit (not Back) and open phase 3 instead.
    cy.visit('/petitioners-guidance/');
    cy.visit('/petitioners-timeline/');
    cy.get(content).each(($el) => expect($el).to.have.class('hidden'));
    cy.get(accordionHeader).eq(3).click();
    cy.get(content).eq(3).should('not.have.class', 'hidden');

    // Back twice lands on the first visit, which had only phase 1 open.
    cy.go('back');
    cy.location('pathname').should('eq', '/petitioners-guidance/');
    cy.go('back');
    cy.location('pathname').should('eq', '/petitioners-timeline/');

    cy.get(content).should(($contents) => {
      const open = openStates($contents);
      expect(open[1], 'phase 1 open').to.equal(true);
      expect(open[3], 'phase 3 open').to.equal(false);
      expect(open.filter(Boolean)).to.have.length(1);
    });

    // Forward twice lands on the second visit, which had only phase 3 open.
    cy.go('forward');
    cy.location('pathname').should('eq', '/petitioners-guidance/');
    cy.go('forward');
    cy.location('pathname').should('eq', '/petitioners-timeline/');

    cy.get(content).should(($contents) => {
      const open = openStates($contents);
      expect(open[1], 'phase 1 open').to.equal(false);
      expect(open[3], 'phase 3 open').to.equal(true);
      expect(open.filter(Boolean)).to.have.length(1);
    });
  });
});
