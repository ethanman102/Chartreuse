import "https://unpkg.com/commonmark@0.29.3/dist/commonmark.js";

'use strict'

// waiting for the page to load before 
window.addEventListener('load', main);

function main() {
    const commonmark = window.commonmark;

    // variable to track the html element for displaying the commonmark text
    // NOTE - debugger says cm_text is empty.
    var markString = document.getElementById('cm_text').innerText;

    // for debugging 
    console.log(markString);


    // will need to bundle with esbuild command for the browser import mini package
    var reader = new commonmark.Parser({smart: true});
    var writer = new commonmark.HtmlRenderer({sourcepos: true, safe: true, softbreak: "<br />"});
    // var writer = new commonmark.HtmlRenderer({sourcepos: true, safe: true, softbreak: "<br />"});
    var parsed = reader.parse(markString); // parsed is a 'Node' tree
    // transform parsed if you like...
    var result = writer.render(parsed); // result is a String

    // for debugging 
    console.log(result);
    
    // // sets the text to be shown in html file as the rendered Commonmark text 
    document.getElementById('cm_text').innerHTML = result;
};

// in case I need to bundle the JS code later
// npx esbuild /chartreuse/static/javascript/cm_render.js --bundle --minify --sourcemap --outfile=./chartreuse/static/cm_render.min.js

// add this to citations page later 
// https://stackoverflow.com/questions/42237388/syntaxerror-import-declarations-may-only-appear-at-top-level-of-a-module
