// https://www.w3schools.com/howto/howto_js_copy_clipboard.asp
function coppy() {
/* Get the text field */
var copyText = document.getElementById("link_input");

/* Select the text field */
copyText.select();
copyText.setSelectionRange(0, 99999); /*For mobile devices*/
/* Copy the text inside the text field */
document.execCommand("copy");
}

function joinGame(){
  var user = document.getElementById('Name');
  var game = document.getElementById('UUID');
  var uuid = game.innerHTML;
  // uuid = uuid.replace(/\s/g, '');
  // uuid = uuid.replace(/['"]+/g, '');
  uuid = uuid.replace(/^"(.+)"$/,'$1');
  var usernname = user.value;
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", "/api/game/"+uuid+"/user");
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.onreadystatechange = function() {
    if (xhttp.readyState == XMLHttpRequest.DONE) {
      var res=JSON.parse(xhttp.responseText);
      if (xhttp.status != 200){
        alert('Fehler beim erzeugen: '+res.Message);
        location=location;
      }else{
        localStorage.setItem('name', usernname);
        for (num in res.User) {
          var juser = res.User[num];
          var name = juser['Name'];
          if (name == usernname){
            localStorage.setItem('id', juser['Id']);
          }
        }
        var id = localStorage.getItem('id');
        window.location.href = "/game_waiting/"+uuid;
      }
    }
  }
  xhttp.send(JSON.stringify({name:usernname}));
}

function refreshGame(){
  location=location;
}
function startGame(){
  var name = localStorage.getItem('name');

  var game = document.getElementById('UUID');
  var gameid = game.innerHTML;
  gameid = gameid.replace(/^"(.+)"$/,'$1');
  var stack_max = document.getElementById("stack_max").value;

  var play_final_cb = document.getElementById('final_cb');
  var play_final = play_final_cb.checked;


  var xhttp = new XMLHttpRequest();
  xhttp.open("POST", "/api/game/"+gameid+"/start");
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.onreadystatechange = function() {
    if (xhttp.readyState == XMLHttpRequest.DONE) {
      if (xhttp.status != 201){
        try {
          var res=JSON.parse(xhttp.responseText);
          alert(''+res.Message);
        }
        catch (e) {
          alert('Allgemeiner Fehler');
        }
      }
    }
  }
  xhttp.send(JSON.stringify({stack_max:stack_max, play_final:play_final}));
}

function startup(){
  faq();
  feedback();
  var id = localStorage.getItem('id');
  var admin_el = document.getElementById('admin_id');
  var admin_id = admin_el.innerHTML;
  var setdamin = document.getElementById('admin');
  if (id != admin_id){
    var all_admin_elements = document.getElementsByClassName("admin_interface");
    for (let admin_element of all_admin_elements){
      admin_element.style.display = "none";
    }
  }

  if (id == admin_id){
    var joincontainer = document.getElementById('joincontainer');
      joincontainer.style.display = "none";
    var button = document.getElementById('startgame_id');
    button.disabled = false;
    var hand = document.getElementById('inline_button_text');
    hand.style.webkitAnimationName = 'run'; // you had a trailing space here which does NOT get trimmed

    setdamin.innerHTML = 'Du bist Admin. Bitte starten wenn alle Spieler in der Liste stehen.'
  }else{
    var button = document.getElementById('startgame_id');
    button.style.display = "none";
    var hand = document.getElementById('inline_button_text');
    hand.style.display = "none";
    setdamin.innerHTML = 'Bitte warte bis der Admin das Spiel startet.'
  }
}

// event handlers (inline onclick is blocked by the CSP)
document.getElementById('jointbtn').addEventListener('click', joinGame);
document.getElementById('coppy_btn').addEventListener('click', coppy);
document.getElementById('startgame_id').addEventListener('click', startGame);
startup();

// Use a "/game_waiting" namespace.
// An application can open a connection on multiple namespaces, and
// Socket.IO will multiplex all those connections on a single
// physical channel. If you don't care about multiple channels, you
// can set the namespace to an empty string.
namespace = '/game';

// Connect to the Socket.IO server.
// The connection URL has the following format, relative to the current page:
//     http[s]://<domain>:<port>[/<namespace>]
const socket = io(namespace, {
  reconnection: true,             // whether to reconnect automatically
  reconnectionAttempts: Infinity, // number of reconnection attempts before giving up
  reconnectionDelay: 1000,        // how long to initially wait before attempting a new reconnection
  reconnectionDelayMax: 5000,     // maximum amount of time to wait between reconnection attempts. Each attempt increases the reconnection delay by 2x along with a randomization factor
  randomizationFactor: 0.5
});
// Event handler for new connections.
// The callback function is invoked when a connection with the
// server is established.
socket.on('connect', function() {
    var game = document.getElementById('UUID');
    var gameid = game.innerHTML;
    gameid = gameid.replace(/^"(.+)"$/,'$1');
    socket.emit('join', {room: gameid});
});

socket.on('reload_game', function(game, cb) {
    if (game){
      var game_el = document.getElementById('UUID');
      var gameid = game_el.innerHTML;
      gameid = gameid.replace(/^"(.+)"$/,'$1');

      var id = localStorage.getItem('id');
      var res = game;
      var sate = res.State
      var table = document.getElementById('player_tbody');
      table.innerHTML = '';
      for (num in res.User) {
        var juser = res.User[num];

        // reload table data
        var tr = document.createElement('tr');
        var th = document.createElement('th');
        th.className = 'counterCell';
        th.scope = 'row';
        var td = document.createElement('td');
        td.innerHTML = juser['Name']
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);

        if (juser['Id'] == id){
          var name = document.getElementById('Name');
          name.disabled = true;
          var btn = document.getElementById('jointbtn');
          btn.disabled = true;
        }
      }
      if (sate == 'started'){
        //alert('Spiel vom admin gestartet eine moment noch');
        window.location.href = "/game/"+gameid;
      }
    }
});

