'use strict'

// waiting for the page to load
document.addEventListener("DOMContentLoaded", function() {
    const commonmark = window.commonmark;

    // variable to track the html element for displaying the commonmark text
    // NOTE - debugger says cm_text is empty.
    var markString = document.getElementById("cm_text").innerText;

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
    document.getElementById("cm_text").innerHTML = result;
})