import "https://unpkg.com/commonmark@0.29.3/dist/commonmark.js";

'use strict'


window.addEventListener('load', main);

function main() {
    const commonmark = window.commonmark;

    // variable to track the html element for displaying the commonmark text
    var markString = document.getElementById('cm_content').innerText;


    // will need to bundle with esbuild command for the browser import mini package
    var reader = new commonmark.Parser({smart: true});
    var writer = new commonmark.HtmlRenderer({sourcepos: true, safe: true, softbreak: "<br />"});
    // var writer = new commonmark.HtmlRenderer({sourcepos: true, safe: true, softbreak: "<br />"});
    var parsed = reader.parse(markString); // parsed is a 'Node' tree
    // transform parsed if you like...
    var result = writer.render(parsed); // result is a String

    
    // // sets the text to be shown in html file as the rendered Commonmark text 
    document.getElementById('cm_content').innerHTML = result;
};