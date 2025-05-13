module.exports = {
  content: [
    'app/templates/**/*.html',
    'home/templates/**/*.html'
  ],
  css: ['app/static/uswds/css/styles.css'],
  safelist: {
    greedy: [/^usa-table/, /^tablet:/, /^mobile-lg:/, /^desktop:/ ]
  },
  output: 'app/static/uswds/css/styles.css'
}
