describe('Admin access', () => {
  it('Admin is abel to login with username password!', () => {
    cy.visit('http://localhost:8000/admin')
    cy.get('input[name=username]').type('admin')
    cy.get('input[name=password]').type('ustcAdminPW!')
    cy.get('button[type=submit]').click()
    cy.url().should('include', '/admin/')
  })
})
