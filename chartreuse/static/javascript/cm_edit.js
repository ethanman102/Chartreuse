'use strict'
// import { Parser, HtmlRenderer, Node } from "commonmark";
// import { Parser, HtmlRenderer, Node } from " https://unpkg.com/commonmark@0.29.3/dist/commonmark.js";

window.addEventListener('load', main);

function main() {
    const commonmark = window.commonmark;

    // let testString = getElementById("test");
    // will need to bundle with esbuild command for the browser import mini package
    var reader = new commonmark.Parser({smart: true});
    var writer = new commonmark.HtmlRenderer({sourcepos: true, safe: true, softbreak: "<br />"});
    var parsed = reader.parse("Hello **world**"); // parsed is a 'Node' tree
    // transform parsed if you like...
    var result = writer.render(parsed); // result is a String

    // variable to track the html element for displaying the commonmark text
    document.getElementById("cm_text").innerHTML = result;

    // // sets the text to be shown in html file as the rendered Commonmark text 
    // htmlString.textContent = result;
};

// npx esbuild ./chartreuse/static/javascript/cm_edit.js --bundle --minify --sourcemap --outfile=./chartreuse/static/javascript/cm_edit.min.js