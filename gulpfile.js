var gulp = require("gulp");
var jsmin = require("gulp-uglify");
var cssmin = require("gulp-minify-css");

gulp.task("minUnminifiedJS", function(){
    return gulp.src(["./templates/assets/**/*.js", "!./templates/assets/**/*.min.js", "!./templates/assets/js/angularjs/**/*.js", "!./templates/assets/js/libs/ng-maps.js"])
        .pipe(jsmin())
        .pipe(gulp.dest("./templates/assets/"));
});

gulp.task("minUnminifiedCSS", function(){
    return gulp.src(["./templates/assets/**/*.css", "!./templates/**/*.min.css"])
        .pipe(cssmin())
        .pipe(gulp.dest("./templates/assets/"));
});

gulp.task("default", ["minUnminifiedCSS", "minUnminifiedJS"]);
