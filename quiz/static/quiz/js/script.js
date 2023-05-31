function send(type_doc) {
    var options = {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'Content-Type': 'text/javascript',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'type': type_doc})
    };
}