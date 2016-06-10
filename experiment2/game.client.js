/*  Copyright (c) 2012 Sven "FuzzYspo0N" Bergström, 
                  2013 Robert XD Hawkins
    
    written by : http://underscorediscovery.com
    written for : http://buildnewgames.com/real-time-multiplayer/
    
    modified for collective behavior experiments on Amazon Mechanical Turk

    MIT Licensed.
*/

/* 
   THE FOLLOWING FUNCTIONS MAY NEED TO BE CHANGED
*/

// A window global for our game root variable.
var globalGame = {};
// Keeps track of whether player is paying attention...
var visible;
var active_keys = []; 
var speed_change = "none";
var started = false;
var ending = false;

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

var debug = getParameterByName('debug') == 'true';

function getSelf () {
  return globalGame.get_player(globalGame.my_id);
};

function client_on_click(game, newX, newY ) {
  // Auto-correcting input, but only between rounds
  var self = getSelf();
  var oldX = self.pos.x;
  var oldY = self.pos.y;
  var dx = newX - oldX;
  var dy = newY - oldY;

  if(debug) {
    checkSkipPress(newX, newY);
  }
  
  if(globalGame.pause) {
    checkButtonPress(newX, newY);
  } else {

    self.destination = {x : Math.round(newX), y : Math.round(newY)};
    self.angle = Math.round((Math.atan2(dy,dx) * 180 / Math.PI) + 90);

    var info_packet = ("c." + self.angle +
		       "."  + self.destination.x +
		       "."  + self.destination.y);
    game.socket.send(info_packet);
  }
};

function checkButtonPress(mx, my) {
  var button = globalGame.advanceButton;
  var dx = mx - button.trueX;
  var dy = my - button.trueY;
  if ((0 < dx) && (dx < button.width) && (0 < dy) && (dy < button.height)) {
    globalGame.socket.send("ready");
    globalGame.pause = false;
  }
};

function checkSkipPress(mx, my) {
  var button = globalGame.advanceButton;
  var dx = mx - button.trueX;
  var dy = my - button.trueY;
  if ((0 < dx) && (dx < button.width) && (0 < dy) && (dy < button.height)) {
    globalGame.socket.send("ready");
    globalGame.pause = false;
  }
};

function client_ondisconnect(data) {
  // Redirect to exit survey
  console.log("server booted");
  
  var self = getSelf();
  var URL = 'http://projects.csail.mit.edu/ci/turk/forms/';
  if(self.hidden) {
    URL += 'away.html';
  } else if(self.inactive) {
    URL += 'inactive.html';
  } else if(self.lagging) {
    URL += 'latency.html';
  } else {
    URL += 'end.html';
  }
  window.location.replace(URL + '?id=' + globalGame.my_id);
};

function client_onserverupdate_received(data){
  // Update client versions of variables with data received from
  // server_send_update function in game.core.js
  var minNumPlayers = _.min([data.players.length, globalGame.players.length]);
  if(data.players) {
    // Match up players
    for(var i = 0; i < minNumPlayers; i++) {
      globalGame.players[i].id = data.players[i].id;
      var s_player = data.players[i].player;
      var l_player = globalGame.players[i].player;
      l_player.destination = s_player.destination;
      l_player.curr_background = s_player.cbg;
      l_player.total_points = s_player.tot;
      l_player.angle = s_player.angle;
      l_player.pos = globalGame.pos(s_player.pos);
      l_player.speed = s_player.speed;
      l_player.onwall = s_player.onwall;
      l_player.hidden = s_player.hidden;
      l_player.inactive = s_player.inactive;
      l_player.lagging = s_player.lagging;
    }
  }
  
  globalGame.game_started = data.gs;
  globalGame.trialInfo = data.trialInfo;

  // Hacky way to know when the round changed
  if(globalGame.roundNum != data.roundNum) {
    globalGame.roundNum = data.roundNum;
    globalGame.start_time = new Date();
  }
  if(globalGame.trialInfo) {
    client_update();
  }
}; 

// This is where clients parse socket.io messages from the server. If
// you want to add another event (labeled 'x', say), just add another
// case here, then call

//          this.instance.player_host.send("s.x. <data>")

// The corresponding function where the server parses messages from
// clients, look for "server_onMessage" in game.server.js.
function client_onMessage(data) {
  
  var commands = data.split('.');
  var command = commands[0];
  var subcommand = commands[1] || null;
  var commanddata = commands[2] || null;

  switch(command) {
  case 's': //server message

    switch(subcommand) {    
    case 'end' :
      // Redirect to exit survey
      console.log("received end message...");
      var URL = ('http://projects.csail.mit.edu/ci/turk/forms/end.html?id=' +
		 globalGame.my_id);
      window.location.replace(URL); break;
    case 'alert' : // Not in database, so you can't play...
      alert('You did not enter an ID'); 
      window.location.replace('http://nodejs.org'); break;
    case 'join' : //join a game requested
      var num_players = commanddata;
      client_onjoingame(num_players); break;
    case 'blink' : //blink title
      flashTitle("GO!");  break;
    case 'showInstructions' :
      globalGame.pause = true;
      drawInstructions(globalGame);
    }        
    break; 
  } 
}; 

function client_countdown() {
  var self = getSelf();
  self.message = 'Begin in 3...';
  setTimeout(function(){self.message = 'Begin in 2...';}, 
             1000);
  setTimeout(function(){self.message = 'Begin in 1...';}, 
             2000);
  setTimeout(function(){
    self.message = 'GO!';     
    globalGame.start_time = new Date();}, 
	     3000);
  setTimeout(function(){self.message = '';}, 
             4000);
}

function client_update() {
  var self = getSelf();
  
  //Clear the screen area
  globalGame.ctx.clearRect(0,0,485,280);

  // Draw background
  if (globalGame.trialInfo.showBackground) {
    draw_spot(globalGame);
  }
    
  // Alter speeds
  if (speed_change != "none") {
    self.speed = speed_change == "up" ? globalGame.max_speed : globalGame.min_speed;
    globalGame.socket.send("s." + String(self.speed).replace(/\./g,'-'));
    speed_change = "none";
  }

  //Draw opponent next
  _.map(globalGame.get_others(globalGame.my_id), function(p){
    if(p.id) {
      draw_player(globalGame, p.player);
      draw_label(globalGame, p.player, "Player " + p.id.slice(0,4));
    }
  });
  
  // Draw points scoreboard 
  $("#cumulative_bonus").html("Total bonus this round: $" +
			      (self.total_points).fixed(2));

  $("#curr_bonus").html("Current Score: <span style='color: " 
			+ getColorForPercentage(self.curr_background) 
			+";'>" + Math.floor(self.curr_background*100) + "%</span>");

  if(!started) {
    var left = timeRemaining(globalGame.waiting_remaining,
			     globalGame.waiting_room_limit);
    var diff = globalGame.players_threshold - globalGame.player_count;
  }
  
  if(globalGame.game_started) {
    var left = Date.now() - globalGame.start_time;
    left = timeRemaining(left, globalGame.round_length);
    // Draw time remaining 
    $("#time").html("Time remaining: " + left['t'] + " " + left['unit']);
  } else {
    $("#time").html('You will join the game soon.');
  }
  
  //And then we draw ourself so we're always in front
  if(globalGame.game_started && self.pos) {
    draw_destination(globalGame, self);
    draw_player(globalGame, self);
    draw_label(globalGame, self, "YOU");
  }
  
  draw_message(globalGame, self);
  
  if(debug) {
    drawButton(globalGame);
  }

};

var timeRemaining = function(remaining, limit) {
  var time_remaining = limit - Math.floor(remaining / (1000*60));
  if(time_remaining > 1) {
    return {t: time_remaining, unit: 'minutes', actual: (limit - remaining/1000)}
  } else {
    time_remaining = 60 * limit - Math.floor(remaining / 1000)
    //time_remaining = Math.max(Math.floor(time_remaining*6)*10, 10)
    return {t: time_remaining, unit: 'seconds', actual: (limit - remaining/1000)}
  }

}


/*
 The following code should NOT need to be changed
 */

// When loading the page, we store references to our
// drawing canvases, and initiate a game instance.
window.onload = function(){
  //Create our game client instance.
  globalGame = new game_core({server: false, numBots : 4});
  
  //Connect to the socket.io server!
  client_connect_to_server(globalGame);
  
  //Fetch the viewport
  globalGame.viewport = document.getElementById('viewport');
  
  //Adjust its size
  globalGame.viewport.width = globalGame.world.width;
  globalGame.viewport.height = globalGame.world.height;

  $('#viewport').click(function(e){
    e.preventDefault();
    // e.pageX is relative to whole page -- we want
    // relative to GAME WORLD (i.e. viewport)
    var offset = $(this).offset();
    var relX = e.pageX - offset.left;
    var relY = e.pageY - offset.top;
    client_on_click(globalGame, relX, relY);
  });
  
  KeyboardJS.on('space', 
		function(){speed_change = "up";}, 
		function(){speed_change = "down";});


  //Fetch the rendering contexts
  globalGame.ctx = globalGame.viewport.getContext('2d');

  //Set the draw style for the font
  globalGame.ctx.font = '11px "Helvetica"';

  //Finally, start the loop
  globalGame.start_time = new Date();  
  globalGame.update();
};

// Associates callback functions corresponding to different socket messages
function client_connect_to_server(game) {
  //Store a local reference to our connection to the server
  game.socket = io.connect();

  //When we connect, we are not 'connected' until we have a server id
  //and are placed in a game by the server. The server sends us a message for that.
  game.socket.on('connect', function(){
    //        game.state = 'connecting';
  }.bind(game));

  // game.socket.on('ping', function(data){
  //   game.socket.send('pong.' + data.sendTime + "." + data.tick_num);
  // });
  //Sent when we are disconnected (network, server down, etc)
  game.socket.on('disconnect', client_ondisconnect.bind(game));
  //Sent each tick of the server simulation. This is our authoritive update
  game.socket.on('onserverupdate', client_onserverupdate_received);
  //Handle when we connect to the server, showing state and storing id's.
  game.socket.on('onconnected', client_onconnected.bind(game));
  //On message from the server, we parse the commands and send it to the handlers
  game.socket.on('message', client_onMessage.bind(game));
}; 

function client_onconnected(data) {
  //The server responded that we are now in a game,
  //this lets us store the information about ourselves  
  // so that we remember who we are.
  console.log("setting id to " + data.id);
  globalGame.my_id = data.id;
  globalGame.players[0].id = data.id;
};

function client_onjoingame(num_players) {
  // Set self color, leave others default white
  var self = getSelf();
  self.color = globalGame.self_color;
  self.speed = globalGame.min_speed;
  self.message = '';
  //self.message = 'Please remain active while you wait.';    
}; 

// Automatically registers whether user has switched tabs...
(function() {
  document.hidden = hidden = "hidden";

  // Standards:
  if (hidden in document)
    document.addEventListener("visibilitychange", onchange);
  else if ((hidden = "mozHidden") in document)
    document.addEventListener("mozvisibilitychange", onchange);
  else if ((hidden = "webkitHidden") in document)
    document.addEventListener("webkitvisibilitychange", onchange);
  else if ((hidden = "msHidden") in document)
    document.addEventListener("msvisibilitychange", onchange);
  // IE 9 and lower:
  else if ('onfocusin' in document)
    document.onfocusin = document.onfocusout = onchange;
  // All others:
  else
    window.onpageshow = window.onpagehide = window.onfocus 
    = window.onblur = onchange;
})();

function onchange (evt) {
  var v = 'visible', h = 'hidden',
      evtMap = { 
        focus:v, focusin:v, pageshow:v, blur:h, focusout:h, pagehide:h 
      };
  evt = evt || window.event;
  if (evt.type in evtMap) {
    document.body.className = evtMap[evt.type];
  } else {
    document.body.className = evt.target.hidden ? "hidden" : "visible";
  }
  visible = document.body.className;
  globalGame.socket.send("h." + document.body.className);
};

function dict_to_query_string(info) {
  out = '';
  for (var key in info) {
    var value = info[key];
    out += '&' + key + '=' + value
  }
  return out;
}

// Flashes title to notify user that game has started
(function () {

  var original = document.title;
  var timeout;

  window.flashTitle = function (newMsg, howManyTimes) {
    function step() {
      document.title = (document.title == original) ? newMsg : original;
      if (visible == "hidden") {
        timeout = setTimeout(step, 500);
      } else {
        document.title = original;
      }
    };
    cancelFlashTitle(timeout);
    step();
  };

  window.cancelFlashTitle = function (timeout) {
    clearTimeout(timeout);
    document.title = original;
  };

}());
