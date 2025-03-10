/* gulpfile.js */

/**
* Import uswds-compile
*/
const uswds = require("@uswds/compile");

/**
* USWDS version
* Set the major version of USWDS you're using
* (Current options are the numbers 2 or 3)
*/
uswds.settings.version = 3;

/**
* Path settings
* Set as many as you need
*/
uswds.paths.dist.css = './app/static/uswds/css';
uswds.paths.dist.fonts = './app/static/uswds/fonts';
uswds.paths.dist.img = './app/static/uswds/img';
uswds.paths.dist.js = './app/static/uswds/js';
uswds.paths.dist.theme = './app/static/uswds/sass';

/**
* Exports
* Add as many as you need
*/
exports.init = uswds.init;
exports.compile = uswds.compile;
exports.watch = uswds.watch;
exports.copyAssets = uswds.copyAssets
