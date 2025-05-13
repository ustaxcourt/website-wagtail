module.exports = {
  content: [
    'app/templates/**/*.html',
    'home/templates/**/*.html'
  ],
  css: ['app/static/uswds/css/styles.css'],
  safelist: {
    greedy: [
        /^usa-table/,
        /^tablet:grid-col/,
        /^tablet:display-none/,
        /^tablet:display-block/,
        /^mobile-lg:grid-col/,
        /^mobile-lg:display-table-cell/,
        /^desktop:grid-col/
    ]
  },
  output: 'app/static/uswds/css/styles.css'
}
