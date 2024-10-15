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

const csrftoken = getCookie('csrftoken');

document.querySelectorAll('.like-button').forEach(button => {
    button.addEventListener('click', function(event) {
        const postId = this.getAttribute('data-post-id');
        const userId = this.getAttribute('data-user-id');
        const url = `like-post/`;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,  // Use the CSRF token from the cookie
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                post_id: postId,
                user_id: userId
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            if (data.likes_count) {
                this.innerText = `${data.likes_count} likes`;  // Update the like count on the button
            } else {
                console.error('Failed to like post:', data.error);
            }
            window.location.reload();  // Reload the page to update the like count
        })
        .catch(error => console.error('Error:', error));
    });
});

document.querySelectorAll('.follow-button').forEach(button => {
    button.addEventListener('click', function(event) {
        const postId = this.getAttribute('data-post-id');
        const userId = this.getAttribute('data-user-id');
        const url = 'send-follow-request/'; 
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,  // Use the CSRF token from the cookie
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                post_id: postId,
                user_id: userId
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            window.location.reload();
        })
        .catch(error => console.error('Error:', error));
    });
});

document.querySelectorAll('.post-card').forEach(button => {
    button.addEventListener('click', function(event) {
        const postCards = document.querySelectorAll('.post-card');

        print(event)
        if (!event.target.closest('button')) {
            const postUrl = card.getAttribute('data-post-url');
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const postCards = document.querySelectorAll('.post-card');
    
    postCards.forEach(function(card) {
        card.addEventListener('click', function(event) {
            // Prevent click action on buttons or other elements inside the card
            print(event)
            if (!event.target.closest('button')) {
                const postUrl = card.getAttribute('data-post-url');
                window.location.href = postUrl;
            }
        });
    });
});
