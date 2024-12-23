function createSession() {
    fetch('/create-session/', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        // Redirect the browser to join-session page
        window.location.href = '/join-session/' + data.code;
    });
}

