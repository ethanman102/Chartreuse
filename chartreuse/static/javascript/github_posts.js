window.addEventListener('load', startPollingAuthors);

function startPollingAuthors() {
    fetchAuthors();
    setInterval(() => {
        fetchAuthors();
    }, 600000); // 10 minutes
}

async function fetchAuthors() {
    let allAuthors = [];
    let page = 1;
    const size = 50;

    const shouldPoll = await fetch('/chartreuse/github/polling/');
    const data = await shouldPoll.json();
    if (data.poll == "True") {
        console.log('Polling is enabled. Fetching authors...');
        try {
            while (true) {
                const response = await fetch(`/chartreuse/api/authors/?page=${page}&size=${size}`);
                if (!response.ok) throw new Error("Network response was not ok");

                const data = await response.json();

                const pageUsers = data.authors || [];
                const filteredUserAttributes = pageUsers.map(user => ({
                    type: "author",
                    id: user.id,
                    host: user.host,
                    displayName: user.displayName,
                    github: user.github,
                    profileImage: user.profileImage,
                    page: `${user.host}authors/${user.username}`
                }));

                allAuthors = allAuthors.concat(filteredUserAttributes);

                if (pageUsers.length < size) break;

                page++;
            }

            const authors = {
                type: "authors",
                authors: allAuthors
            };

            authors.authors.forEach(author => {
                // check whether the users github url is valid or not with regex
                const githubUrl = author.github;
                const githubRegex = /^(https:\/\/github\.com\/)([a-zA-Z0-9-]+)$/;

                // Test the GitHub URL against the regex
                const match = githubUrl.match(githubRegex);
                if (match) {
                    // Extract the username from the matched groups
                    const githubUsername = match[2];
                    if (githubUsername) {
                        fetchStarredReposAndCreatePosts(githubUsername, author.id);
                        fetchGitHubEventsAndCreatePosts(githubUsername, author.id);
                    }
                }
            });

        } catch (error) {
            console.error("Failed to fetch authors:", error);
        }
    } else;
}

async function fetchStarredReposAndCreatePosts(githubUsername, authorId) {
    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content'); // Get CSRF token

        const githubApiUrl = `https://api.github.com/users/${githubUsername}/starred`;
        const response = await fetch(githubApiUrl);

        if (!response.ok) {
            throw new Error(`Failed to fetch starred repos for ${githubUsername}`);
        }

        const starredRepos = await response.json();

        for (const repo of starredRepos) {
            // Prepare the post data
            const postData = new URLSearchParams();
            const postTitle = `⭐ Starred: ${repo.name}`;
            const postDescription = `👾 Repo: ${repo.html_url}`;
            postData.append('title', postTitle);
            postData.append('author_id', authorId);
            postData.append('description', postDescription);
            postData.append('contentType', "text/plain");
            postData.append('content', repo.description || "No description available");
            postData.append('visibility', "PUBLIC");

            const encodedAuthorId = encodeURIComponent(authorId);
        
            const checkDuplicateUrl = `/chartreuse/api/post-exists/`;
            const duplicateCheckResponse = await fetch(checkDuplicateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                },
                body: postData.toString(),
            });

            const isDuplicate = await duplicateCheckResponse.json();
            if (isDuplicate.exists) {
                console.log(`Duplicate post exists for: ${postTitle}. Skipping creation.`);
                continue;
            }

            const postApiUrl = `/chartreuse/api/authors/${encodedAuthorId}/posts/`;
            const postResponse = await fetch(postApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                },
                body: postData.toString(),
            });

            if (!postResponse.ok) {
                const errorData = await postResponse.json();
                console.error(`Failed to create post for ${repo.name}:`, errorData);
                continue;
            }

            const createdPost = await postResponse.json();
            console.log(`Post created for ${repo.name}:`, createdPost);
        }
    } catch (error) {
        console.error(`Error fetching starred repos for ${githubUsername}:`, error);
    }
}

async function fetchGitHubEventsAndCreatePosts(githubUsername, authorId) {
    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content'); // Get CSRF token
        const githubEventsUrl = `https://api.github.com/users/${githubUsername}/events/public`;
        
        const response = await fetch(githubEventsUrl);

        if (!response.ok) {
            throw new Error(`Failed to fetch GitHub events for ${githubUsername}`);
        }

        const events = await response.json();

        for (const event of events) {
            if (event.type === "WatchEvent") {
                const postData = new URLSearchParams();
                postData.append('title', `👀 ${event.actor.display_login} started watching ${event.repo.name}`);
                postData.append('description', `🕙 Started watching at ${event.created_at}`);
                postData.append('contentType', "text/plain");
                postData.append('author_id', authorId);
                postData.append('content', `Watch Event at ${event.repo.url}`);
                postData.append('visibility', "PUBLIC");

                const encodedAuthorId = encodeURIComponent(authorId);
                const checkDuplicateUrl = `/chartreuse/api/post-exists/`;
                const duplicateCheckResponse = await fetch(checkDuplicateUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    },
                    body: postData.toString(),
                });
    
                const isDuplicate = await duplicateCheckResponse.json();
                if (isDuplicate.exists) {
                    console.log(`Duplicate post exists for: ${postTitle}. Skipping creation.`);
                    continue;
                }

                const postApiUrl = `/chartreuse/api/authors/${encodedAuthorId}/posts/`;
                const postResponse = await fetch(postApiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    },
                    body: postData.toString()
                });

                if (!postResponse.ok) {
                    const errorData = await postResponse.json();
                    console.error(`Failed to create post for WatchEvent:`, errorData);
                    continue;
                }

                const createdPost = await postResponse.json();
                console.log(`Post created for WatchEvent:`, createdPost);
            }
        }
    } catch (error) {
        console.error(`Error fetching GitHub events for ${githubUsername}:`, error);
    }
}