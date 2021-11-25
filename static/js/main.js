function sendRequest(method, requestUrl, data, responseHandler){
    if(typeof method != "string"){
        console.log("Invalid HTTP method. Cannot initiate AJAX request");
    }
    else{
        method = method.toUpperCase();
        if(method != "GET" && method!="POST" && method!="PUT" && method!="DELETE"){
            console.log("Invalid HTTP method. Cannot initiate AJAX request");
        }
        else{
            if(!window.XMLHttpRequest){
                console.log("Cannot initiate AJAX request. AJAX is not supported.");
            }
            else{
                var request = new XMLHttpRequest();
                request.onreadystatechange =
                    function(){
                        if(request.readystate == 4 && request.status == 200)
                            responseHandler(request);
                    }
                request.open(method, requestUrl, true);
                request.send(data);
            }
        }
    }
}

function afterRemovePlayer(request){
    if(request.json.status == 1 || request.json.status == 3){
        document.getElementById("content").innerHTML = request.responseText;
    }
    else if(request.json.status=2){
        document.getElementById("content").innerHTML = request.responseText;
    }
    /* In second case, modify html, remove this player id, in first case, show Bootstrap alert */
}