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
                        if(request.readyState == 4)
                            responseHandler(request);
                    }
                request.open(method, requestUrl, true);
                request.send(data);
            }
        }
    }
}

//alert the user whether removal failed or succeeded, and in the latter case, remove the player element from the DOM
function afterRemovePlayer(request){
    var json_response = JSON.parse(request.responseText);
    var player_id = json_response.data.player_id;
    var result = json_response.result;
    var detail = json_response.detail;
    var playerNode = document.getElementById("player-id-" + player_id);
    if(request.status == 404 || request.status == 500){
        var newElement = ['<div class="alert alert-danger alert-dismissible fade show" role="alert">',
            '<strong>' + result + '</strong>  ' + detail,
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'].join('\n');
        playerNode.insertAdjacentHTML('afterend', newElement);
    }
    else if(request.status == 200){
        playerNode.remove();
        var playersListNode = document.getElementById("players-list");
        var newElement = ['<div class="alert alert-success alert-dismissible fade show" role="alert">',
            '<strong>' + result + '</strong>  ' + detail,
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'].join('\n');
        playersListNode.insertAdjacentHTML('beforebegin', newElement);
    }
    else{
        var newElement = ['<div class="alert alert-danger alert-dismissible fade show" role="alert">',
            '<strong>Failed!  </strong>Status code: ' + request.status + '. Refresh and try again.',
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'].join('\n');
        playerNode.insertAdjacentHTML('afterend', newElement);
    }
}

function createAlert(type, result, detail){

}

function showSearchForm(request){
    var allTeams = JSON.parse(request.responseText).data.teams;
    var datalistInnerHTML = "";
    for(team of allTeams){
        datalistInnerHTML += '<option data-value="' + team.id + '" value="' + team.name + ' (' + team.country + ')">\n';
    }
    var datalist = document.getElementById("teams");
    datalist.innerHTML = datalistInnerHTML;

    document.getElementById("search-form").style.display = "block";
}

function searchForPlayer(){
    var teamName = document.getElementById("team-to-search-for").value;
    var teamId;
    var knownTeam = document.querySelector('#teams option[value="' + teamName + '"]');
    if(knownTeam){
        var teamId = knownTeam.dataset.value;
    }
    var playerName = document.getElementById("player-to-search-for").value;
    var url = "/players/search?player_name=" + playerName;
    if(teamId){
        url += "&team_id=" + teamId;
    }
    else{
        url += "&team_name=" + teamName;
    }
    sendRequest("GET", url, null, handlePlayerSearchResults);
}

function handlePlayerSearchResults(request){
    //Display message that there is no
    //such player for such team. Or if one result, call backend add_player endpoint with afterAddPlayer as the response
    //handler. Or if multiple results, show confirm-choice-form with id of each player as values to the options, and
    //on submit call add_player endpoint with afterAddPlayer as response handler
}

function afterAddPlayer(request){

}