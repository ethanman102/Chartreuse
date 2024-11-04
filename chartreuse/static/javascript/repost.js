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
            },
            body: JSON.stringify({
               content_type: 'repost',
               title:  'REPOST: ',
               visibility: 'PUBLIC',
               description: 'Check out this post by: '
            })

        });
    }

    repostButton.addEventListener('click',repost)

}