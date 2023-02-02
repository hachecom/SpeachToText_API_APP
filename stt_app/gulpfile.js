// requirements
var gulp = require('gulp');
var gulpBrowser = require("gulp-browser");
var reactify = require('reactify');
var del = require('del');
var size = require('gulp-size');


// tasks transform: translate from jsx -React scripts- to plain JS
gulp.task('transform', function () {
  var stream = gulp.src('./app/static/scripts/jsx/*.js')
    .pipe(gulpBrowser.browserify({transform: ['reactify']}))
    .pipe(gulp.dest('./app/static/scripts/js/'))
    .pipe(size());
  return stream;
});

// clean the plain js script's directory for start from the scratch every time
gulp.task('del', function () {
  return del(['./project/static/scripts/js']);
});

// default main task which is executed by the command $ gulp
gulp.task('default', ['del'], function() {
  gulp.start('transform')
  gulp.watch('./project/static/scripts/jsx/*.js', ['transform']); //this task is watching for change in files. if any,
                                                                  //then re-runs the transform task
});