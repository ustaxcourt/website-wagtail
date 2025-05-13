module.exports = {
  content: [
    'app/templates/**/*.html',
    'home/templates/**/*.html'
  ],
  css: ['app/static/uswds/css/styles.css'],
  safelist: {
    greedy: [/^usa-table/]
  },
  output: 'app/static/uswds/css/styles.css'
}
