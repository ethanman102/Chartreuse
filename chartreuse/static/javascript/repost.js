import { getCookie } from "./home_page";

const csrfToken = getCookie('csrftoken');

window.addEventListener('load',main);

function main(){
    const repostButton = document.querySelector('.repost-button');

    const repost = async () => {
        let url = 'repost/'

        repostButton.disabled = 'true';
        let response = await fetch(url,{
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
               content_type: 'repost',
               title:  'REPOST: ',
               visibility: 'PUBLIC',
               description: 'Check out this super cool post!'
            })

        });

        let data = await response.json();
        var message = (response.status === 200) ? data.success : data.error;

        const messageElement = document.createElement('p');
        messageElement.innerText = message;
        messageElement.style.color = (response.status === 200) ? 'chartreuse' : 'red';
        repostButton.appendChild(messageElement);

        setInterval(() =>{
            messageElement.remove();
            repostButton.removeAttribute('disabled');

        },10000);
    }

    repostButton.addEventListener('click',repost)

}