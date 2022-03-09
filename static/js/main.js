// UTILS:

// data has to be in JSON format
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
                request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                request.send(JSON.stringify(data));
            }
        }
    }
}

function generateAlert(type, result, detail){
    if(type == "danger" || type == "success" || type=="info"){
        return ['<div id="alert-top" class="alert alert-' + type + ' alert-dismissible fade show" role="alert">',
                '<strong>' + result + '</strong>  ' + detail,
                '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
                '</div>'].join('\n');
    }
}

function validateResponse(response){
    var contentNode = document.getElementById("content");
    var result, detail, alert;
    var goodResponse = false;
    try{
        var jsonResponse = JSON.parse(response.responseText);
        result = jsonResponse.result;
        detail = jsonResponse.detail;
        if(response.status == 200){
            goodResponse = true;
        }
        else{
            alert = generateAlert("danger", result, detail);
        }
    }
    catch(e){
        result = "Failed!";
        detail = "Status code: " + response.status + ". Refresh and try again."
        alert = generateAlert("danger", result, detail);
    }
    if (goodResponse){
        return jsonResponse;
    }
    else{
        contentNode.insertAdjacentHTML('beforebegin', alert);
        window.location.href = "#alert-top";
        return null;
    }
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


function afterRemovePlayer(response){
    var jsonResponse = validateResponse(response);
    if(jsonResponse){
        var playerId = jsonResponse.data.player_id;
        var playerNode = document.getElementById("player-id-" + playerId);
        playerNode.remove();
        var alert = generateAlert("success", jsonResponse.result, jsonResponse.detail);
        document.getElementById("content").insertAdjacentHTML('beforebegin', alert);
        window.location.href = "#alert-top";
    }
}

//get all teams from database, populate <datalist id="teams"> with teams as options
//next step: show team-search in search-section
function showSearchSection(response){
    resetSearchSection();
    var jsonResponse = validateResponse(response);
    if(jsonResponse){
        var allTeams = jsonResponse.data.teams;
        var datalist = document.getElementById("teams");
        var datalistInnerHTML = "";
        for(team of allTeams){
            datalistInnerHTML += '<option data-value="' + team.id + '" value="' + team.name + ' (' + team.country + ')">\n';
        }
        datalist.innerHTML = datalistInnerHTML;
        document.getElementById("search-section").style.display = "block";
        document.getElementById("team-search").style.display = "block";
    }
    else{
        resetSearchSection();
    }
}

//if team is unknown, search for it; if it's known, set it as the value of <select id="team-to-confirm">
// next step: show player-search or go to handleTeamSearchResults()
function afterTeamSelection(){
    var teamInputNode = document.getElementById("team-to-search-for");

    teamInputNode.setAttribute("disabled", "");
    document.getElementById("team-to-search-for-submit").setAttribute("disabled", "");

    var teamName = teamInputNode.value;
    var knownTeam = document.querySelector('#teams option[value="' + teamName + '"]'); //not null if user-entered team
                                                                                       //name is in the teams datalist
    if(knownTeam){
        var teamId = knownTeam.getAttribute("data-value");
        var teamToConfirmNode = document.getElementById("team-to-confirm"); //the <select> element
        var optionNode = document.createElement("option")
        optionNode.value = teamId;
        teamToConfirmNode.appendChild(optionNode)
        teamToConfirmNode.value = teamId;
        showPlayerSearch();
    }
    else{
        sendRequest("GET", "/teams/search?name=" + teamName, null, handleTeamSearchResults);
    }
}

//populate <select id="team-to-confirm"> with teams as options
//next step: show team-confirmation
function handleTeamSearchResults(response){
    var jsonResponse = validateResponse(response);
    if(jsonResponse){
        var teams = jsonResponse.data.teams;
        var selectNode = document.getElementById("team-to-confirm");
        teams.forEach(function(team, index){
            var optionNode = document.createElement("option");
            optionNode.value = team.id;
            optionNode.text = team.name + " (" + team.country + ")";
            selectNode.appendChild(optionNode);
        });
        document.getElementById("team-confirmation").style.display = "block";
    }
    else{
        resetSearchSection();
    }
}

//next step: show <div id="player-search">
function showPlayerSearch(){
    document.getElementById("team-to-confirm").setAttribute("disabled", "");
    document.getElementById("team-to-confirm-submit").setAttribute("disabled", "");
    document.getElementById("player-search").style.display = 'block'
}

//send request to backend to search for player with teamId, playerName
//next step: go to handleSearchResults()
function searchForPlayer(){
    document.getElementById("player-to-search-for").setAttribute("disabled", "");
    document.getElementById("player-to-search-for-submit").setAttribute("disabled", "");
    var teamId = document.getElementById("team-to-confirm").value;
    var playerName = document.getElementById("player-to-search-for").value;
    var url = "/players/search?player_name=" + playerName + "&team_id=" + teamId;
    sendRequest("GET", url, null, handlePlayerSearchResults);
}

//if no players found, generate alert, else populate <select id="player-to-confirm"> with players as options
//next step: show alert or show player-confirmation
function handlePlayerSearchResults(response){
    var jsonResponse = validateResponse(response);
    if(jsonResponse){
        var players = jsonResponse.data.players;
        if(players === undefined || players.length == 0){
            var alert = generateAlert("danger", "Failed!", "There is no such player who plays for such a team");
            document.getElementById("content").insertAdjacentHTML('beforebegin', alert);
            window.location.href = "#alert-top";
        }
        else{
            selectNode = document.getElementById("player-to-confirm");
            players.forEach(function(player, index){
                var optionNode = document.createElement("option");
                optionNode.value = player.id;
                optionNode.text = player.name + " (" + player.nationality + ")";
                selectNode.appendChild(optionNode);
            });
            document.getElementById("player-confirmation").style.display = "block";
        }
    }
    else{
        resetSearchSection();
    }
}

//send request to backend to add player with playerId, teamId
//next step: go to afterAddPlayer()
function addPlayer(){
    document.getElementById("player-to-confirm").setAttribute("disabled", "");
    document.getElementById("player-to-confirm-submit").setAttribute("disabled", "");
    teamId = document.getElementById("team-to-confirm").value;
    playerId = document.getElementById("player-to-confirm").value;
    sendRequest("PUT", "/players/", {"player_id": playerId, "team_id": teamId}, afterAddPlayer);
}

//according to backend response, show appropriate alert
//next step: show alert
function afterAddPlayer(response){
    var jsonResponse = validateResponse(response);
    if(jsonResponse){
        var result = jsonResponse.result;
        var detail = jsonResponse.detail;
        if(result == "Success!"){
            detail += ' They\'ll appear in the below list upon <a href="/players">refreshing</a>.';
        }
        var alert = generateAlert("success", result, detail);
        document.getElementById("content").insertAdjacentHTML('beforebegin', alert);
        window.location.href = "#alert-top";
    }
    resetSearchSection();
}

//wipes all inputs/selects/datalists, enables all elements, and hides them
function resetSearchSection(){
    document.getElementById("team-to-search-for").value = "";
    document.getElementById("teams").innerHTML = "";
    document.getElementById("team-to-confirm").innerHTML = "";
    document.getElementById("player-to-search-for").value = "";
    document.getElementById("player-to-confirm").innerHTML = "";

    var disabledElementIds = ["team-to-search-for", "team-to-search-for-submit", "team-to-confirm"
                               , "team-to-confirm-submit", "player-to-search-for", "player-to-search-for-submit"
                               , "player-to-confirm", "player-to-confirm-submit"];
    for(var id of disabledElementIds){
        var elm = document.getElementById(id);
        if(elm.hasAttribute("disabled")){
            elm.removeAttribute("disabled");
        }
    }

    document.getElementById("team-search").style.display = "none";
    document.getElementById("team-confirmation").style.display = "none";
    document.getElementById("player-search").style.display = "none";
    document.getElementById("player-confirmation").style.display = "none";
    document.getElementById("search-section").style.display = "none";
}