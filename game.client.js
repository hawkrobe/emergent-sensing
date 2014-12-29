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
var game = {};
// A window global for our id, which we can use to look ourselves up
var my_id = null;
// Keeps track of whether player is paying attention...
var visible;
var active_keys = []; 
var speed_change = "none";

// what happens when you press 'left'?
left_turn = function() {
    var self = game.get_player(my_id);
    self.angle = (Number(self.angle) - 5) % 360;
    game.socket.send("a." + self.angle);
};

// what happens when you press 'left'?
right_turn = function() {
    var self = game.get_player(my_id);
    self.angle = (Number(self.angle) + 5) % 360;
    game.socket.send("a." + self.angle);
};

// Function that gets called client-side when someone disconnects
client_ondisconnect = function() {
    // TODO: If server drops us, redirect to "disconnected.html" page
};

/* 
Note: If you add some new variable to your game that must be shared
  across server and client, add it both here and the server_send_update
  function in game.core.js to make sure it syncs 

Explanation: This function is at the center of the problem of
  networking -- everybody has different INSTANCES of the game. The
  server has its own, and both players have theirs too. This can get
  confusing because the server will update a variable, and the variable
  of the same name won't change in the clients (because they have a
  different instance of it). To make sure everybody's on the same page,
  the server regularly sends news about its variables to the clients so
  that they can update their variables to reflect changes.
*/
client_onserverupdate_received = function(data){

    // Update client versions of variables with data received from
    // server_send_update function in game.core.js

    if(data.players) {
        _.map(_.zip(data.players, game.players),
            function(z){
                z[0].id = z[1].id
                if (z[0].player == null) {
                    z[1].player = null
                } else {
                    var s_player = z[0].player
                    var l_player = z[1].player
                    if(z[0].id != my_id | l_player.angle == null) 
                        l_player.angle = s_player.angle
                    l_player.points_earned = s_player.poi
                    l_player.pos = game.pos(s_player.pos)
                    l_player.speed = s_player.speed
                }
            })
    }
    game.condition = data.cond;
    game.draw_enabled = data.de;
    game.good2write = data.g2w;

}; 

// This is where clients parse socket.io messages from the server. If
// you want to add another event (labeled 'x', say), just add another
// case here, then call

//          this.instance.player_host.send("s.x. <data>")

// The corresponding function where the server parses messages from
// clients, look for "server_onMessage" in game.server.js.
client_onMessage = function(data) {

    var commands = data.split('.');
    var command = commands[0];
    var subcommand = commands[1] || null;
    var commanddata = commands[2] || null;

    switch(command) {
    case 's': //server message

        switch(subcommand) {    
        case 'p' :// Permanent Message
            game.players.self.message = commanddata;
            break;
        case 'm' :// Temporary Message
            game.players.self.message = commanddata;
            var local_game = game;
            setTimeout(function(){local_game.players.self.message = '';}, 1000);
            break;
        case 'alert' : // Not in database, so you can't play...
            alert('You did not enter an ID'); 
            window.location.replace('http://nodejs.org'); break;
        case 'join' : //join a game requested
            var num_players = commanddata;
            client_onjoingame(num_players); break;
        case 'add_player' : // New player joined... Need to add them to our list.
            console.log("adding player")
            game.players.push({id: commanddata, player: new game_player(game)}); break;
        case 'begin_game' :
            game.hidden_enabled = true;
            client_newgame(); break;
        case 'blink' : //blink title
            flashTitle("GO!");  break;
        }        
        break; 
    } 
}; 

// Restarts things on the client side. Necessary for iterated games.
client_newgame = function() {
    if (game.round_num == 3) {
        // Redirect to exit survey
        var URL = './static/game_over.html';
        URL += '?id=' + game.players.self.id;
        window.location.replace(URL);
    } else {
        // Decrement number of games remaining
        game.round_num += 1;
    }

    // Initiate countdown (with timeouts)
    game.get_player(my_id).angle = null;
    client_countdown();
}; 

client_countdown = function() {
    var player = game.get_player(my_id);
    player.message = 'Begin in 3...';
    setTimeout(function(){player.message = 'Begin in 2...';}, 
               1000);
    setTimeout(function(){player.message = 'Begin in 1...';}, 
               2000);
    setTimeout(function(){
        player.message = 'GO';     
        game.start_time = new Date();}, 
               3000);
    setTimeout(function(){player.message = '';}, 
               4000);
}

client_update = function() {
    var player = game.get_player(my_id)

    //Clear the screen area
    game.ctx.clearRect(0,0,280,485);

    // Alter speeds
    if (speed_change != "none") {
        var self = game.get_player(my_id);
        self.speed = speed_change == "up" ? game.max_speed : game.min_speed;
        game.socket.send("s." + self.speed);
        speed_change = "none"
    }

    // Turn if key is still being held... Don't do anything if both are held
    if (active_keys.length < 2) {
        if(_.contains(active_keys, 'right')) right_turn();
        if(_.contains(active_keys, 'left')) left_turn() ;
    }

    //Draw opponent next (but only those in radius)
    _.map(game.get_others(my_id), function(p){
        if(!game.hidden_enabled || game.distance_between(p.player.pos, player.pos) < game.visibility_radius)
            draw_player(game, p.player)});

    // Draw visibility radius
    if(player.pos) draw_visibility_radius(game, player)
    
    // Draw points scoreboard 
    $("#cumulative_bonus").html("Total bonus so far: $" + (player.points_earned / 100).fixed(2));

    $("#curr_bonus").html("Current bonus: <span style='color: " 
        + getColorForPercentage(player.points_earned) 
        +";'>" + Math.abs(player.points_earned) + "</span>");

    // Draw time remaining 
    var time_remaining = game.round_length - Math.floor((new Date() - game.start_time) / (1000 * 60))
    $("#time").html(game.good2write ? "Time remaining: " + time_remaining + " minutes" : "You are in the waiting room.");

    //And then we draw ourself so we're always in front
    if(player.pos) draw_player(game, player);
};

var percentColors = [
    { pct: 0.0, color: { r: 0xff, g: 0x00, b: 0 } },
    { pct: 0.5, color: { r: 0xff, g: 0xff, b: 0xff } },
    { pct: 1.0, color: { r: 0x00, g: 0xff, b: 0 } } ];
 
var getColorForPercentage = function(pct) {
    for (var i = 0; i < percentColors.length; i++) {
        if (pct <= percentColors[i].pct) {
            var lower = percentColors[i - 1] || { pct: 0.1, color: { r: 0x0, g: 0x00, b: 0 } };
            var upper = percentColors[i];
            var range = upper.pct - lower.pct;
            var rangePct = (pct - lower.pct) / range;
            var pctLower = 1 - rangePct;
            var pctUpper = rangePct;
            var color = {
                r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
                g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
                b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
            };
            return 'rgb(' + [color.r, color.g, color.b].join(',') + ')';
        }
    }
}

/*
  The following code should NOT need to be changed
*/

// When loading the page, we store references to our
// drawing canvases, and initiate a game instance.
window.onload = function(){
    //Create our game client instance.
    game = new game_core();
    
    //Connect to the socket.io server!
    client_connect_to_server(game);
    
    //Fetch the viewport
    game.viewport = document.getElementById('viewport');
    
    //Adjust its size
    game.viewport.width = game.world.width;
    game.viewport.height = game.world.height;

    // Keep track of which keys are being pressed
    KeyboardJS.on('left', 
        function(){if(!_.contains(active_keys, 'left')) active_keys.push('left');},//if(_.contains(active_keys, 'left')) ;}, 
        function(){active_keys = _.without(active_keys, 'left');});//active_keys = _.without(active_keys, 'left');})
    KeyboardJS.on('right', 
        function(){if(!_.contains(active_keys, 'right')) active_keys.push('right');}, 
        function(){active_keys = _.without(active_keys, 'right');})
    KeyboardJS.on('space', 
        function(){speed_change = "up"}, 
        function(){speed_change = "down"})


    //Fetch the rendering contexts
    game.ctx = game.viewport.getContext('2d');

    //Set the draw style for the font
    game.ctx.font = '11px "Helvetica"';

    //Finally, start the loop
    game.update();
};

// Associates callback functions corresponding to different socket messages
client_connect_to_server = function(game) {
    //Store a local reference to our connection to the server
    game.socket = io.connect();

    //When we connect, we are not 'connected' until we have a server id
    //and are placed in a game by the server. The server sends us a message for that.
    game.socket.on('connect', function(){
//        game.state = 'connecting';
    }.bind(game));

    //Sent when we are disconnected (network, server down, etc)
    game.socket.on('disconnect', client_ondisconnect.bind(game));
    //Sent each tick of the server simulation. This is our authoritive update
    game.socket.on('onserverupdate', client_onserverupdate_received.bind(game));
    //Handle when we connect to the server, showing state and storing id's.
    game.socket.on('onconnected', client_onconnected.bind(game));
    //On message from the server, we parse the commands and send it to the handlers
    game.socket.on('message', client_onMessage.bind(game));
}; 

client_onconnected = function(data) {
    //The server responded that we are now in a game,
    //this lets us store the information about ourselves  
    // so that we remember who we are.  
    my_id = data.id;
    game.players[0].id = my_id;
    game.get_player(my_id).online = true;
};

client_onjoingame = function(num_players) {
    // Need client to know how many players there are, so they can set up the appropriate data structure
    _.map(_.range(num_players - 1), function(i){game.players.unshift({id: null, player: new game_player(game)})});
    // Set self color, leave others default white
    game.get_player(my_id).color = game.self_color;
    // Start 'em moving
    game.get_player(my_id).speed = game.min_speed;
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
//    game.socket.send("h." + document.body.className);
};

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
