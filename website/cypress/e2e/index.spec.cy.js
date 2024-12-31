describe('index page', () => {
  beforeEach(() => {
    cy.visit('http://127.0.0.1:8000/')
  })
  
  it('has required us govt banner', () => {
    cy.get('section').should('have.class', 'usa-banner')
  })

  it('unhides/hides banner content when button is clicked', () => {
    // state when loaded
    cy.get('div').should('have.class', 'usa-banner__content').should('have.class', 'usa-accordion__content wide-container').should('be.hidden') 
    
    // open banner content
    cy.get('button').should('have.class', 'usa-accordion__button').should('have.class', 'usa-accordion__button').click()
    cy.get('div').should('have.class', 'usa-banner__content').should('have.class', 'usa-accordion__content wide-container').should('be.visible') 
    
    // click again to close content
    cy.get('button').should('have.class', 'usa-accordion__button').should('have.class', 'usa-accordion__button').click()
    cy.get('div').should('have.class', 'usa-banner__content').should('have.class', 'usa-accordion__content wide-container').should('be.hidden') 
  })
})