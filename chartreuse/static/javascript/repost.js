import { getCookie } from "./home_page";

const csrfToken = getCookie('csrftoken');

window.addEventListener('load',main);

function main(){
    const repostButton = document.querySelector('.repost-button');

    const repost = async () => {
        let url = 'repost/'
        let response = await fetch(url,{
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            }

        });
    }

    repostButton.addEventListener('click',repost)

}