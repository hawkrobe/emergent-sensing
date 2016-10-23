/*  Copyright (c) 2012 Sven "FuzzYspo0N" Bergström, 2013 Robert XD Hawkins
    
    written by : http://underscorediscovery.com
    written for : http://buildnewgames.com/real-time-multiplayer/
    
    modified for collective behavior experiments on Amazon Mechanical Turk

    MIT Licensed.
*/

//require('look').start()

var _ = require('underscore')

    var
        use_db      = false,
        game_server = module.exports = { games : {}, game_count:0, assignment:0},
        fs          = require('fs');
	    
    if (use_db) {
	    database    = require(__dirname + "/database"),
	    connection  = database.getConnection();
    }

global.window = global.document = global;
require('./game.core.js');
utils = require('./utils.js');

var five_counter = 0
var four_counter = 0
var three_counter = 0

// This is the function where the server parses and acts on messages
// sent from 'clients' aka the browsers of people playing the
// game. For example, if someone clicks on the map, they send a packet
// to the server (check the client_on_click function in game.client.js)
// with the coordinates of the click, which this function reads and
// applies.
game_server.server_onMessage = function(client,message) {
    //Cut the message up into sub components
    var message_parts = message.split('.');

    //The first is always the type of message
    var message_type = message_parts[0];
    //console.log("received message: " + message)
    //Extract important variables
    var target = client.game.gamecore.get_player(client.userid);
    var others = client.game.gamecore.get_others(client.userid);
  if (message_type == 'c') {
    //target.speed = target.speed == 0 ? client.game.min_speed : target.speed;    
    target.angle = message_parts[1];
    target.destination = {x : message_parts[2], y : message_parts[3]};
    
  } else if (message_type == 's') {
        target.speed = message_parts[1].replace(/-/g,'.');;
    } else if (message_type == "h") { // Receive message when browser focus shifts
      target.visible = message_parts[1];
    } else if (message_type == "quit") {
      target.instance.disconnect()
      } else if (message_type == "start") {
	game_server.startGame(client.game);
    } else if (message_type == 'pong') {
	var latency = (Date.now() - message_parts[1])/2;
	target.latency = latency;
	if(client.game.gamecore.game_started) {
	    client.game.gamecore.latencyStream.write(String(client.userid)+","+message_parts[2]+","+latency+"\n",
						     function(err) { if(err) throw err; });
	} else {
	    client.game.gamecore.waitingLatencyStream.write(String(client.userid)+","+message_parts[2]+","+latency+"\n",
						     function(err) { if(err) throw err; });
	}
    }
};

/* 
   The following functions should not need to be modified for most purposes
*/

// This is the important function that pairs people up into 'rooms'
// all independent of one another.
game_server.findGame = function(player, demo) {
    this.log('looking for a game. We have : ' + this.game_count);
    //if there are any games created, add this player to it!
    if(this.game_count) {
       var joined_a_game = false;
        for (var gameid in this.games) {
            if(!this.games.hasOwnProperty(gameid)) continue;
            var game = this.games[gameid];
            var gamecore = game.gamecore;
            if(game.player_count < gamecore.players_threshold && !game.active && !game.holding) { 
               joined_a_game = true;
                // player instances are array of actual client handles
                game.player_instances.push({
                    id: player.userid, 
                    player: player
                });
                game.player_count++;
                // players are array of player objects
                game.gamecore.players.push({
                    id: player.userid, 
                    player: new game_player(gamecore,player)
                });
                // Attach game to player so server can look at it later
                player.game = game;
		
                // notify new player that they're joining game
                player.send('s.join.' + gamecore.players.length)

                // notify existing players that someone new is joining
                _.map(gamecore.get_others(player.userid), function(p){p.player.instance.send( 's.add_player.' + player.userid)})
		gamecore.player_count = game.player_count;
                gamecore.server_send_update();
                gamecore.update();
		
                if (game.player_count == gamecore.players_threshold) {
                    this.holdGame(game)
                }
            }
        }
        if(!joined_a_game) { // if we didn't join a game, we must create one
            this.createGame(player, demo);
        }
    }
    else { 
        //no games? create one!
        this.createGame(player, demo);
    }
}; 

// Will run when first player connects
game_server.createGame = function(player, demo) {
    // Figure out variables
    //var thresholds = Array(3,3);
  var thresholds = Array(1, 2, 3, 4, 5, 6);
  //var thresholds = Array(50, 50);
    var players_threshold = thresholds[Math.floor(Math.random()*thresholds.length)];
    //var noise_id = Math.floor(Math.random() * 4) + '-1en01'

  var bg_id = Math.floor(Math.random() * 4) + ''
  
    var d = new Date();
    var start_time = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate() + '-' + d.getHours() + '-' + d.getMinutes() + '-' + d.getSeconds() + '-' + d.getMilliseconds()
  
    var id = utils.UUID();

    var name = start_time + '_' + players_threshold + '_' + bg_id + '_' + id;
    
    //Create a new game instance
    var game = {
	//generate a new id for the game
        id : id,           
	//store list of players in the game
        player_instances: [{id: player.userid, player: player}],
	//for simple checking of state
        player_count: 1
    };
    
    
    //Create a new game core instance (defined in game.core.js)
    game.gamecore = new game_core(game, demo);

    // Tell the game about its own id
    game.gamecore.game_id = id;
    game.gamecore.players_threshold = players_threshold
    game.gamecore.player_count = 1

    game.gamecore.background_id = bg_id
  game.gamecore.name = name

  // assign to exploratory or confirmatory data subsets
  if(Math.random() < 0.5) {
    game.gamecore.data_subset = 'exploratory'
  } else {
    game.gamecore.data_subset = 'confirmatory'
  }

    // Set up the filesystem variable we'll use later, and write headers
    var game_f = "data/" + game.gamecore.data_subset + "/waiting_games/" + name + ".csv"
    var latency_f = "data/" + game.gamecore.data_subset + "/waiting_latencies/" + name + ".csv"

    game.gamecore.fs = fs;
    
    fs.writeFile(game_f, "pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points,obs_bg_val,goal_x,goal_y\n", function (err) {if(err) throw err;})
    game.gamecore.waitingDataStream = fs.createWriteStream(game_f, {'flags' : 'a'});
    fs.writeFile(latency_f, "pid,tick,latency\n", function (err) {if(err) throw err;})
    game.gamecore.waitingLatencyStream = fs.createWriteStream(latency_f, {'flags' : 'a'});
    
    // tell the player that they have joined a game
    // The client will parse this message in the "client_onMessage" function
    // in game.client.js, which redirects to other functions based on the command
    player.game = game;
    player.send('s.join.' + game.gamecore.players.length)
    this.log('player ' + player.userid + ' created a game with id ' + player.game.id);
    //Start updating the game loop on the server
    game.gamecore.update();

    // add to game collection
    this.games[ game.id ] = game;
    this.game_count++;
    if(game.gamecore.players_threshold == 1) {
	this.holdGame(game)
    }
    
    var game_server = this

    // schedule the game to stop receing new players
    setTimeout(function() {
	    if(!game.active) {
		game_server.holdGame(game);
	    }
	}, game.gamecore.waiting_room_limit*60*1000 - 30*1000)

    // schedule the game to start to prevent players from waiting too long
    setTimeout(function() {
	    if(!game.active) {
		game_server.startGame(game);
	    }
	}, game.gamecore.waiting_room_limit*60*1000)
	    
    //return it
    return game;
}; 

// we are requesting to kill a game in progress.
// This gets called if someone disconnects
game_server.endGame = function(gameid, userid) {
    var thegame = this.games [ gameid ];
    if(thegame) {
        //if the game has more than one player, it's fine -- let the others keep playing, but let them know
        var player_metric = (thegame.active 
			     ? thegame.gamecore.get_active_players().length 
			     : thegame.player_count)
        console.log("removing... game has " + player_metric + " players")
        if(player_metric > 1) {
            var i = _.indexOf(thegame.gamecore.players, _.findWhere(thegame.gamecore.players, {id: userid}))
            thegame.gamecore.players[i].player = null;

            // If the game hasn't started yet, allow more players to fill their place. after it starts, don't.
            if (!thegame.active) {
                thegame.player_count--;
		thegame.gamecore.player_count = thegame.player_count;
                thegame.gamecore.server_send_update();
                thegame.gamecore.update();
	    }
        } else {
            // If the game only has one player and they leave, remove it.
            thegame.gamecore.stop_update();
            delete this.games[gameid];
            this.game_count--;
            this.log('game removed. there are now ' + this.game_count + ' games' );
        }
    } else {
        this.log('that game was not found!');
    }   
}; 

// When the threshold is exceeded or time has passed, stop receiving new players and schedule game start
game_server.holdGame = function(game) {
    game.holding = true;
    setTimeout(function() {
	if(!game.active) {
	    game_server.startGame(game);
	}
    }, 30.0 * 1000) // game.gamecore.waiting_room_limit*60*1000/5.0)
};
    
// When the threshold is exceeded, this gets called
game_server.startGame = function(game) {

    game.active = true;
      
    var game_f = "data/" + game.gamecore.data_subset + "/games/" + game.gamecore.name + ".csv"
    var latency_f = "data/" + game.gamecore.data_subset + "/latencies/" + game.gamecore.name + ".csv"
    
    fs.writeFile(game_f, "pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points,obs_bg_val,goal_x,goal_y\n", function (err) {if(err) throw err;})
    game.gamecore.gameDataStream = fs.createWriteStream(game_f, {'flags' : 'a'});
    fs.writeFile(latency_f, "pid,tick,latency\n", function (err) {if(err) throw err;})
    game.gamecore.latencyStream = fs.createWriteStream(latency_f, {'flags' : 'a'});

    console.log('game ' + game.id + ' starting with ' + game.player_count + ' players...')
    
    game.gamecore.server_newgame(); 
};

//A simple wrapper for logging so we can toggle it,
//and augment it for clarity.
game_server.log = function() {
    console.log.apply(this,arguments);
};
