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
        button.disabled = 'disabled';
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
        button.disabled = 'disabled';
        const postId = this.getAttribute('data-post-id');
        const userId = this.getAttribute('data-user-id');
        const url = 'send-follow-request/'; 
        console.log(postId, userId);
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

        if (!event.target.closest('button')) {
            const postUrl = card.getAttribute('data-post-url');
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const postCards = document.querySelectorAll('.post-card');
    
    postCards.forEach(function(card) {
        card.addEventListener('click', function(event) {
            if (!event.target.closest('button')) {
                const postUrl = card.getAttribute('data-post-url');
                window.location.href = postUrl;
            }
        });
    });
});


// document.querySelectorAll('.pfp-button').forEach(button => {
//     button.addEventListener('click', function() {
//         const postId = this.getAttribute('data-post-id');
//         const userId = this.getAttribute('data-user-id');
//         const url = `/chartreuse/set-profile-image/`; 
//         fetch(url, {
//             method: 'POST',
//             headers: {
//                 'X-CSRFToken': csrftoken,
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({
//                 post_id: postId,
//                 user_id: userId
//             })
//         })
//         .then(response => response.json())
//         .then(data => {
//             console.log('Success:', data);
//             window.location.reload();
//         })
//         .catch(error => console.error('Error:', error));
//     });
// });

document.querySelectorAll('.comment-button').forEach(button => {
    button.addEventListener('click', function() {
        button.disabled = 'disabled';
        const postId = this.getAttribute('data-post-id');
        const userId = this.getAttribute('data-user-id');
        const commentText = document.getElementById('comment-text').value;
        const url = `/chartreuse/comment/`;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                post_id: postId,
                user_id: userId,
                comment: commentText,
                contentType: 'text/plain'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Success:', data);
                window.location.reload();
            } else {
                console.error('Error:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

document.querySelectorAll('.like-comment-button').forEach(button => {
    button.addEventListener('click', function(event) {
        button.disabled = 'disabled';
        const postId = this.getAttribute('data-post-id');
        const userId = this.getAttribute('data-user-id');
        const commentId = this.getAttribute('data-comment-id');
        const url = `/chartreuse/comment/like/`;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,  // Use the CSRF token from the cookie
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                post_id: postId,
                user_id: userId,
                comment_id: commentId
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

document.querySelectorAll('.copy-button').forEach(button => {
    button.addEventListener('click', function() {
        const link = this.getAttribute('data-url');
        const fullUrl = window.location.protocol + '//' + window.location.host + link;
        navigator.clipboard.writeText(fullUrl);
        alert('Post link copied to clipboard!');
    });
})