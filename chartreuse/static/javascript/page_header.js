

class Title{
    constructor(titleElement){
        this.titleArray = titleElement.innerText.split('');
        this.titleElement = titleElement;
        this.index = 0;
        // set initial title to first char
        this.titleElement.innerText = this.titleArray[0]
    }

    revealNext(){
        if (this.index === (this.titleArray.length - 1)){
            this.index = 0
            this.titleElement.innerText = this.titleArray[this.index];  
        }else{
            this.index += 1;
            this.titleElement.innerText += this.titleArray[this.index];
        }
    }
}

window.addEventListener('load',main);

function main(){
    const header = document.getElementById('header');
    
    const title = new Title(header);

    setInterval(title.revealNext.bind(title),500);

}