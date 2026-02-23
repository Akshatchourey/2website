// Parsing for CSRF Token
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

// Like frontend updating logic
    const likeContainer = document.querySelector('.like-dislike-container');
    if (likeContainer) {
        const likeBtn = document.getElementById('like-button');
        const dislikeBtn = document.getElementById('dislike-button');
        const likeCountElem = document.getElementById('like-count');
        const fetchUrl = likeContainer.dataset.url;

        function updateBackend() {
            fetch(fetchUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({})
            })
            .then(res => res.json())
            .then(data => {
                if (data.likes_count !== undefined) {
                    likeCountElem.textContent = data.likes_count;
                }
            })
            .catch(err => console.error("Error updating status:", err));
        }

        likeBtn.addEventListener('click', (e) => {
            e.preventDefault();

            if (!likeBtn.disabled) {
                let currentCount = parseInt(likeCountElem.textContent) || 0;
                likeBtn.disabled = true;
                likeBtn.textContent = 'Liked! 👍';
                dislikeBtn.disabled = false;
                dislikeBtn.textContent = '👎 Dislike';
                likeCountElem.textContent = currentCount + 1;
                updateBackend();
            }
        });

        dislikeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (!dislikeBtn.disabled) {
                let currentCount = parseInt(likeCountElem.textContent) || 0;
                dislikeBtn.disabled = true;
                dislikeBtn.textContent = 'Disliked! 👎';
                likeBtn.disabled = false;
                likeBtn.textContent = '👍 Like';
                likeCountElem.textContent = Math.max(0, currentCount - 1);
                updateBackend();
            }
        });
    }

// Subscribing frontend updating logic
    const subBtn = document.getElementById('subscribe-btn');
    if (subBtn) {
        const subCountElem = document.getElementById('subscriber-count');
        const toggleUrl = subBtn.dataset.url;

        subBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const isCurrentlySubscribed = subBtn.classList.contains('subscribed');
            let currentCount = parseInt(subCountElem.textContent) || 0;

            if (isCurrentlySubscribed) {
                subBtn.classList.remove('subscribed');
                subBtn.textContent = 'Subscribe';
                subCountElem.textContent = Math.max(0, currentCount - 1);
            } else {
                subBtn.classList.add('subscribed');
                subBtn.textContent = 'Subscribed 🙂';
                subCountElem.textContent = currentCount + 1;
            }

            // Sending request to backend
            fetch(toggleUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    subCountElem.textContent = data.subscriber_count;
                } else {
                    console.error("Subscription failed:", data.message);
                    location.reload();
                }
            })
            .catch(error => console.error('Error toggling subscription:', error));
        });
    }

// Comment frontend updating logic
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const commentBodyInput = document.getElementById('new_comment');
            const commentBody = commentBodyInput.value.trim();
            const commentListContainer = document.getElementById('comment-list-container');
            const noCommentsMsg = document.getElementById('no-comments-msg');
            const csrftoken = getCookie('csrftoken');
            const commentUrl = this.dataset.url;

            if (!commentBody) {
                alert('Comment cannot be empty.');
                return;
            }

            fetch(commentUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    'comment_body': commentBody
                })
            })
            .then(response => {
                if (!response.ok) {
                    if(response.status === 403) {
                         throw new Error('You must be logged in to comment.');
                    }
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    if (noCommentsMsg) {
                        noCommentsMsg.remove();
                    }
                    const newCommentHtml = `
                        <div class="comment">
                            <p>${data.comment_body}</p>
                            <div class="comment-meta">
                                ${data.comment_name} | ${data.comment_date}
                            </div>
                        </div>
                    `;
                    commentListContainer.insertAdjacentHTML('afterbegin', newCommentHtml);

                    commentBodyInput.value = '';
                }
            })
            .catch(error => {
                console.error('Error adding comment:', error);
                alert(`Error: ${error.message}`);
            });
        });
    }
