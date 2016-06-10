/*  Copyright (c) 2012 Sven "FuzzYspo0N" Bergström, 2013 Robert XD Hawkins
    
    written by : http://underscorediscovery.com
    written for : http://buildnewgames.com/real-time-multiplayer/
    
    modified for collective behavior experiments on Amazon Mechanical Turk

    MIT Licensed.
*/

//require('look').start()

    var
        game_server = module.exports = { games : {}, game_count:0, assignment:0},
        fs          = require('fs');

global.window = global.document = global;
require('./game.core.js');
var utils = require('./utils.js');

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
  var message_type = message_parts[0];

  //Extract important variables
  var target = client.game.get_player(client.userid);
  var others = client.game.get_others(client.userid);

  if (message_type == 'c') {
    target.speed = target.speed == 0 ? client.game.min_speed : target.speed;    
    target.angle = message_parts[1];
    target.destination = {x : message_parts[2], y : message_parts[3]};
  } else if (message_type == 's') {
    target.speed = message_parts[1].replace(/-/g,'.');;
  } else if (message_type == "h") { 
    target.visible = message_parts[1];
  } else if (message_type == "ready") {
    client.game.update();
    client.game.newRound();
  } else if (message_type == 'pong') {
    var latency = (Date.now() - message_parts[1])/2;
    target.latency = latency;
    var data = String(client.userid) + "," + message_parts[2] + "," + latency + "\n";
    var stream = (client.game.game_started ?
    		          client.game.latencyStream :
    		          client.game.waitingLatencyStream);
    stream.write(data, function(err) { if(err) throw err; });
  }
};

/* 
 The following functions should not need to be modified for most purposes
 */

game_server.findGame = function(player, debug) {
  this.log('looking for a game. We have : ' + this.game_count);
  var joined_a_game = false;
  // for (var gameid in this.games) {
  //   var game = this.games[gameid];
  //   if(game.player_count < game.players_threshold && !game.active && !game.holding) {
  //     // End search
  //     joined_a_game = true;
      
  //     // Add player to game
  //     game.player_count++;
  //     game.players.push({id: player.userid,
	// 		                   instance: player,
	// 		                   player: new game_player(game, player)});
      
  //     // Add game to player
  //     player.game = game;
  //     player.send('s.join.' + game.players.length);

  //     // notify existing players that someone new is joining
  //     _.map(game.get_others(player.userid), function(p){
	//       p.player.instance.send( 's.add_player.' + player.userid);
  //     });
      
  //     // Start game
  //     this.startGame(game);
  //   }
  // }

  // If you couldn't find a game to join, create a new one
  if(!joined_a_game) {
    this.createGame(player, debug);
  }
};

// Will run when first player connects
game_server.createGame = function(player, debug) {
  // Figure out variables
  var options = {
    expName: "couzinExp2",
    numBots: 4,
    server: true,
    id : utils.UUID(),
    player_instances: [{id: player.userid, player: player}],
    player_count: 1,
    experiment_info: player.info,
    debug: debug
  };

  var game = new game_core(options);
  
  player.game = game;
  player.send('s.join.' + game.players.length);
  this.log('player ' + player.userid + ' created a game with id ' + player.game.id);
  //Start updating the game loop on the server
  game.update();

  // add to game collection
  this.games[ game.id ] = game;
  this.game_count++;

  if(game.players_threshold == 1) {
    this.holdGame(game);
  }
  
  var game_server = this;

  // // schedule the game to stop receing new players
  // setTimeout(function() {
  //   if(!game.active) {
  //     game_server.holdGame(game);
  //   }
  // }, game.gamecore.waiting_room_limit*60*1000*4/5.0);

  // // schedule the game to start to prevent players from waiting too long
  // setTimeout(function() {
  //   if(!game.active) {
  //     game_server.startGame(game);
  //   }
  // }, game.gamecore.waiting_room_limit*60*1000);
  
  //return it
  return game;
}; 

// we are requesting to kill a game in progress.
// This gets called if someone disconnects
game_server.endGame = function(gameid, userid) {
  var thegame = this.games [ gameid ];
  if(thegame) {
    //if the game has more than one player, it's fine --
    // let the others keep playing, but let them know
    var player_metric = (thegame.active 
			 ? thegame.get_active_players().length 
			 : thegame.player_count);
    console.log("removing... game has " + player_metric + " players");
    if(player_metric > 1) {
      var i = _.indexOf(thegame.players, _.findWhere(thegame.players, {id: userid}));
      thegame.players[i].player = null;

      // If the game hasn't started yet, allow more players to fill their place.
      // after it starts, don't.
      if (!thegame.active) {
        thegame.player_count--;
	thegame.player_count = thegame.player_count;
        thegame.server_send_update();
        thegame.update();
      }
    } else {
      // If the game only has one player and they leave, remove it.
      thegame.stop_update();
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
  }, 0.0); // game.gamecore.waiting_room_limit*60*1000/5.0)
};

// When the threshold is exceeded, this gets called
game_server.startGame = function(game) {
  
  game.active = true;
  
  var d = new Date();
  var start_time = d.getFullYear() + '-' + d.getMonth() + 1 + '-' + d.getDate() + '-' + d.getHours() + '-' + d.getMinutes() + '-' + d.getSeconds() + '-' + d.getMilliseconds()
  
  var name = start_time + '_' + game.player_count + '_' + game.id;
  
  var game_f = "data/games/" + name + ".csv"
  var latency_f = "data/latencies/" + name + ".csv"

  game.fs = fs;
  
  fs.writeFile(game_f, "pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points,obs_bg_val,goal_x,goal_y\n", function (err) {if(err) throw err;})
  game.gameDataStream = fs.createWriteStream(game_f, {'flags' : 'a'});
  
  fs.writeFile(latency_f, "pid,tick,latency\n", function (err) {if(err) throw err;})
  game.latencyStream = fs.createWriteStream(latency_f, {'flags' : 'a'});

  console.log('game ' + game.id + ' starting with ' + game.player_count + ' players...')
  
  game.newRound();
};

//A simple wrapper for logging so we can toggle it,
//and augment it for clarity.
game_server.log = function() {
  console.log.apply(this,arguments);
};
