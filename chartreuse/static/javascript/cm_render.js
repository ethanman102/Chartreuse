'use strict'

// waiting for the page to load
document.addEventListener("DOMContentLoaded", function() {
    const commonmark = window.commonmark;

    // refer to citation 11 on AI/LLM Citations on our wiki page: https://github.com/uofa-cmput404/f24-project-chartreuse/wiki/AI-LLM-Citations
    var postStrings = document.querySelectorAll("p.cm_text");
    
    var markStrings = Array.from(postStrings).map(function(post) {
        // for debugging 
        console.log(post.textContent);
        let markString = post.innerText

        // following lines are from the https://github.com/commonmark/commonmark.js repo's README

        var reader = new commonmark.Parser({smart: true, linebreak: "<br>"});
        var writer = new commonmark.HtmlRenderer({sourcepos: true, safe: true, softbreak: "<br />"});
        // var writer = new commonmark.HtmlRenderer({sourcepos: true, safe: true, softbreak: "<br />"});
        var parsed = reader.parse(markString); // parsed is a 'Node' tree
        // transform parsed if you like...
        var result = writer.render(parsed); // result is a String

        post.innerHTML = result; 
    }); 
        
});

