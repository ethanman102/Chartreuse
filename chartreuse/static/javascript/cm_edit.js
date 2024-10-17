'use strict'
import { Parser, HtmlRenderer, Node} from 'commonmark';


window.addEventListener('load', main);

function main() {
    // will need to bundle with esbuild command for the browser import mini package
    var reader = new Parser({smart: true});
    var writer = new HtmlRenderer({sourcepos: true, safe: true, softbreak: "<br />"});
    var parsed = reader.parse("Hello *world*"); // parsed is a 'Node' tree
    // transform parsed if you like...
    var result = writer.render(parsed); // result is a String

    // variable to track the html element for displaying the commonmark text
    var htmlString = document.getElementById("cm_text");

    // sets the text to be shown in html file as the rendered Commonmark text 
    htmlString.textContent = result;
};

// npx esbuild ./chartreuse/static/javascript/cm_edit.js --bundle --minify --sourcemap --outfile=./chartreuse/static/javascript/cm_edit.min.js