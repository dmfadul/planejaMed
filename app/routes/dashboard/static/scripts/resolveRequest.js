function resolveRequest(request, response) {
    fetch('/resolve-request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request: request, response: response })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        sessionStorage.setItem("clickButton", true)
        window.location.reload();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}