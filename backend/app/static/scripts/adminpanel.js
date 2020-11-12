function delete_player(){
  if (confirm('Bist du sicher das du den Spieler entfernen möchtest. Dies kann nicht rückgängig gemacht werden')) {
    var game = document.getElementById('UUID');
    var game_id = game.innerHTML;
    game_id = game_id.replace(/['"]+/g, '');
    var delete_player = document.getElementById('delete_player');
    var user_id = delete_player.options[delete_player.selectedIndex].value;

    var xhttp = new XMLHttpRequest();
    xhttp.open("DELETE", "/api/game/"+game_id+"/user/"+user_id);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == XMLHttpRequest.DONE) {
        var res=JSON.parse(xhttp.responseText);
        if (xhttp.status != 200){
          alert(''+res.Message);
        }else{
          window.location.reload();
        }
      }
    }
    xhttp.send(JSON.stringify({}));
  }
}

function choose_admin(){
  if (confirm('Bist du sicher das du den Admin wechseln möchtest. Dies kann nur vom neune Admin rückgängig gemacht werden')) {
    var game = document.getElementById('UUID');
    var game_id = game.innerHTML;
    game_id = game_id.replace(/['"]+/g, '');
    var choose_admin = document.getElementById('choose_admin');
    var new_admin_id = choose_admin.options[choose_admin.selectedIndex].value;
    var admin_el = document.getElementById('admin_id');
    var old_admin_id = admin_el.innerHTML;

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/api/game/"+game_id+"/user/"+old_admin_id);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == XMLHttpRequest.DONE) {
        var res=JSON.parse(xhttp.responseText);
        if (xhttp.status != 200){
          alert(''+res.Message);
        }else{
          window.location.reload();
        }
      }
    }
    xhttp.send(JSON.stringify({new_admin_id:new_admin_id}));
  }
}

function back_to_waiting(){
  if (confirm('Bist du sicher das du zurück zum Warteraum willst um einen Spieler hinzuzufügen?')) {
    var game = document.getElementById('UUID');
    var game_id = game.innerHTML;
    game_id = game_id.replace(/['"]+/g, '');

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/api/game/"+game_id+"/back");
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == XMLHttpRequest.DONE) {
        var res=JSON.parse(xhttp.responseText);
        if (xhttp.status != 200){
          alert(''+res.Message);
        }else{
          alert(res.Message + ' Alle Speiler geraten zurück zum Warteraum');
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

    var count = document.getElementById('stack_count_id').value;
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
          var res=JSON.parse(xhttp.responseText);
          alert(''+res.Message);
        }else{
          var res=JSON.parse(xhttp.responseText);
          alert(''+res.Message);
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
