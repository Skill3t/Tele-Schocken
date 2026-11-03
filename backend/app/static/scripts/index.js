
function createGame(){
  var admin = document.getElementById('adminname');
  var adminname = admin.value;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", "/api/game");
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.onreadystatechange = function() {
    if (xhttp.readyState == XMLHttpRequest.DONE) {
      var res=JSON.parse(xhttp.responseText);
      if (xhttp.status != 201){
        alert('Fehler beim erzeugen: '+res.Message);
        location=location;
      }else{
        localStorage.setItem('name', adminname);
        localStorage.setItem('id', res.Admin_Id);
        // Simulate a mouse click:
        window.location.href = "/game_waiting/"+res.UUID;
      }
    }
  }
  xhttp.send(JSON.stringify({name:adminname}));
}
// accepts the full invite link or just the game id, useful when the page
// is embedded (e.g. as iframe) and there is no address bar to open the link
function joinGame(){
  var input = document.getElementById('joinlink').value;
  var match = input.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i);
  if (match == null){
    alert('Keine gültige Spiel-ID gefunden. Bitte den Link oder die Spiel-ID vom Ersteller des Spiels einfügen.');
    return;
  }
  window.location.href = "/game_waiting/"+match[0].toLowerCase();
}

document.getElementById('create_game_btn').addEventListener('click', createGame);
document.getElementById('join_game_btn').addEventListener('click', joinGame);
document.getElementById('joinlink').addEventListener('keyup', function(event){
  if (event.key === 'Enter'){
    joinGame();
  }
});


