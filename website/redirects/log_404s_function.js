function handler(event) {
    var request = event.request;
    var response = event.response;

    // Only capture 404s under /files/documents
    if (response.status == 404 && request.uri.startsWith("/files/documents")) {
        console.log(JSON.stringify({
            referrer: request.headers.referer ? request.headers.referer.value : null,
            requested_url: request.uri,
            timestamp: new Date().toISOString(),
            user_agent: request.headers['user-agent'] ? request.headers['user-agent'].value : null,
            ip: request.clientIp
        }));
    }

return response;
}
