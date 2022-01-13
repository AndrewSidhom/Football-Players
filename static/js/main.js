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
    //TODO
}

function showSearchSection(request){
    var allTeams = JSON.parse(request.responseText).data.teams;
    var datalistInnerHTML = "";
    for(team of allTeams){
        datalistInnerHTML += '<option data-value="' + team.id + '" value="' + team.name + ' (' + team.country + ')">\n';
    }
    var datalist = document.getElementById("teams");
    datalist.innerHTML = datalistInnerHTML;
    document.getElementById("search-section").style.display = "block";
    document.getElementById("team-search").style.display = "block";
}

function afterTeamSelection(){
    var teamName = document.getElementById("team-to-search-for").value;
    var teamId;
    var knownTeam = document.querySelector('#teams option[value="' + teamName + '"]'); //True if user-entered team name
                                                                                       //is in the teams datalist
    if(knownTeam){
        var teamId = knownTeam.getAttribute("data-value");
        var playerSearch = document.getElementById("player-search");
        playerSearch.style.display = "block";
    }
    else{
        sendRequest("GET", "/teams/search?name="+teamName, null, confirmTeam);
    }
    }

function confirmTeam(request){
    var teams = JSON.parse(request.responseText).data.teams;
    var selectElement = document.getElementById("teams-for-confirmation");
    teams.forEach(function(team, index) {
        var optionElement = document.createElement('option');
        optionElement.text = team.name + " (" + team.country + ")";
        optionElement.value = team.id;
        selectElement.appendChild(optionElement);
        });
    teamConfirmationElement = document.getElementById("team-confirmation");
    teamConfirmationElement.style.display = "block";
}

function searchForPlayer(){
    var selectElement = document.getElementById("teams-for-confirmation");
    teamId = selectElement.value;
    var playerName = document.getElementById("player-to-search-for").value;
    var url = "/players/search?player_name=" + playerName + "&team_id=" + teamId;
    sendRequest("GET", url, null, handlePlayerSearchResults);
}

function handlePlayerSearchResults(request){
    //TODO: Display message that there is no such player for such team.
    //TODO: Or if one result, call backend add_player endpoint with afterAddPlayer as the response handler.
    //TODO: Or if multiple results, show player-confirmation with select with id and names of players
}

function afterAddPlayer(request){
    //TODO: Fail or success message, add to players html list if success
}