function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrfToken = getCookie('csrftoken');

window.addEventListener('load',main);

function main(){
    const repostButton = document.querySelector('.repost-button');
    let content = repostButton.getAttribute('data-post-id');
    

    const repost = async () => {
        let url = 'repost/'
        console.log(content)

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
               description: 'Check out this super cool post!',
               content: content
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