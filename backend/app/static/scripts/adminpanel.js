function admin_alert(message){
  document.getElementById('admin_alert').innerHTML = message;
}
function delete_player(){
  if (confirm('Bist du sicher das du den Spieler entfernen möchtest. Dies kann nicht rückgängig gemacht werden. Die Runde startet von vorne!')) {
    var game = document.getElementById('UUID');
    var game_id = game.innerHTML;
    game_id = game_id.replace(/['"]+/g, '');
    var delete_player = document.getElementById('select_delete_player');
    var user_id = delete_player.options[delete_player.selectedIndex].value;

    var xhttp = new XMLHttpRequest();
    xhttp.open("DELETE", "/api/game/"+game_id+"/user/"+user_id);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == XMLHttpRequest.DONE) {
        if (xhttp.status != 200){
          alert('Fehler');
        }else{
          window.location.reload();
        }
      }
    };
    xhttp.send();
  }
}

function sort_dice(){
    var game = document.getElementById('UUID');
    var game_id = game.innerHTML;
    game_id = game_id.replace(/['"]+/g, '');
    var admin_el = document.getElementById('admin_id');
    var admin_id = admin_el.innerHTML;
    var xhttp = new XMLHttpRequest();
    xhttp.open("PUT", "/api/game/"+game_id+"/sort");
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == XMLHttpRequest.DONE) {
        if (xhttp.status != 200){
          var res=JSON.parse(xhttp.responseText);
          admin_alert(''+res.Message);
        }
      }
    }
    xhttp.send(JSON.stringify({admin_id:admin_id}));
}


function choose_admin(){
    var game = document.getElementById('UUID');
    var game_id = game.innerHTML;
    game_id = game_id.replace(/['"]+/g, '');
    var choose_admin_el = document.getElementById('select_choose_admin');
    var new_admin_id = choose_admin_el.options[choose_admin_el.selectedIndex].value;
    var admin_el = document.getElementById('admin_id');
    var old_admin_id = admin_el.innerHTML;

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/api/game/"+game_id+"/user/"+old_admin_id+"/change_admin");
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xhttp.setRequestHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == XMLHttpRequest.DONE) {
        if (xhttp.status != 200){
          admin_alert('Fehler');
        }else{
          window.location.reload();
        }
      }
    }
    if (confirm('Bist du sicher das du den Admin wechseln möchtest. Dies kann nur vom neuen Admin rückgängig gemacht werden')) {
      xhttp.send(JSON.stringify({new_admin_id:new_admin_id}));
      var bladi = 'Hallo';
  }
}

function back_to_waiting(){
  if (confirm('Bist du sicher das du zurück zum Warteraum willst um einen Spieler hinzuzufügen? Die Runde startet von vorne!')) {
    var game = document.getElementById('UUID');
    var game_id = game.innerHTML;
    game_id = game_id.replace(/['"]+/g, '');

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/api/game/"+game_id+"/back");
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == XMLHttpRequest.DONE) {
        if (xhttp.status != 201){
          var res=JSON.parse(xhttp.responseText);
          admin_alert(''+res.Message);
        }
      }
    }
    xhttp.send(JSON.stringify({}));
  }
}

  function transfer_chips(){
    // /game/<gid>/user/chips
    var game = document.getElementById('UUID');
    var gameid = game.innerHTML;
    gameid = gameid.replace(/['"]+/g, '');
    var xhttp = new XMLHttpRequest();

    var stack_count = document.getElementById('stack_count_id');
    var count = stack_count.value;
    // var stack = document.getElementById('stack_cb').checked;
    // var aus = document.getElementById('schockaus_cb').checked;
    var transfer_source = document.getElementById('transfer_source');
    var source = transfer_source.options[transfer_source.selectedIndex].value;
    var transfer_target = document.getElementById('transfer_target');
    var target = transfer_target.options[transfer_target.selectedIndex].value;


    xhttp.open("POST", "/api/game/"+gameid+"/user/chips");
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == XMLHttpRequest.DONE) {
        if (xhttp.status != 200){
          try {
            var res=JSON.parse(xhttp.responseText);
            admin_alert(''+res.Message);
          }
          catch (e) {
            admin_alert('Allgemeiner Fehler');
          }
        }else{
          var res=JSON.parse(xhttp.responseText);
          stack_count.value = 0;
          transfer_source.value = 'stack';
          admin_alert(''+res.Message);
        }
      }
    }
    if (source ==  'stack'){
      xhttp.send(JSON.stringify({count:parseInt(count), stack:true, target:parseInt(target)}));
    }else if (source ==  'schockaus') {
      xhttp.send(JSON.stringify({schockaus:true, target:parseInt(target)}));
    }else{
      xhttp.send(JSON.stringify({count:parseInt(count), source:parseInt(source), target:parseInt(target)}));
    }
  }
