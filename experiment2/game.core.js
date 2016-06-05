/*  Copyright (c) 2012 Sven "FuzzYspo0N" Bergström, 
    2013 Robert XD Hawkins
    
    written by : http://underscorediscovery.com
    written for : http://buildnewgames.com/real-time-multiplayer/
    
    substantially modified for collective behavior experiments on the web

    MIT Licensed.
*/

/*
  The main game class. This gets created on both server and
  client. Server creates one for each game that is hosted, and each
  client creates one for itself to play the game. When you set a
  variable, remember that it's only set in that instance.
*/
var has_require = typeof require !== 'undefined';

if( typeof _ === 'undefined' ) {
  if( has_require ) {
    var _ = require('underscore');
    var fs = require("fs");
  }
  else throw new Error('mymodule requires underscore, see http://underscorejs.org');
}

var game_core = function(options){
  this.server = options.server;
  
  //Dimensions of world -- Used in collision detection, etc.
  this.world = {width : 485, height : 280};  // 160cm * 3

  //How often the players move forward <global_speed>px in ms.
  this.tick_frequency = 125;     //Update 8 times per second
  this.ticks_per_sec = 1000/125;

  this.waiting_room_limit = 5; // set maximum waiting room time (in minutes)
  this.round_length = 0.2; // set how long each round will last (in minutes)
  this.max_bonus = 15.0 / 60 * this.round_length; // total $ players can make in bonuses 
  this.booting = false;
  
  this.players_threshold = 1;
  
  // game and waiting length in seconds
  this.game_length = this.round_length*60*this.ticks_per_sec;

  //The speed at which the clients move (e.g. # px/tick)
  this.min_speed = 17 /this.ticks_per_sec; // 7.5cm * 3 * .5s 
  this.max_speed = 57 /this.ticks_per_sec; // 7.5cm * 3 * .5s 
  this.self_color = '#2288cc';
  this.other_color = 'white';

  // minimun wage per tick
  var us_min_wage_per_tick = 7.25 / (60*60*(1000 / this.tick_frequency));
  this.waiting_background = 0.10;//us_min_wage_per_tick * this.game_length / this.max_bonus;
  this.waiting_start = new Date(); 

  this.roundNum = -1;
  this.game_clock = 0;

  //We create a player set, passing them the game that is running
  //them, as well. Both the server and the clients need separate
  //instances of both players, but the server has more information
  //about who is who. Clients will be given this info later.
  if(this.server) {
    this.id = options.id;
    this.expName = options.expName;
    this.expInfo = options.experiment_info;
    this.player_count = options.player_count;
    this.players = [{
      id: options.player_instances[0].id,
      instance: options.player_instances[0].player,
      player: new game_player(this,options.player_instances[0].player,false,0)
    }];
    this.trialList = this.makeTrialList();
  } else {
    // Have to create a client-side player array of same length as server-side
    this.players = this.initializeClientPlayers(options.numBots);
  }
}; 

/* The player class
   A simple class to maintain state of a player on screen,
   as well as to draw that state when required.
*/

var game_player = function( game_instance, player_instance, index) {
  //Store the instance, if any
  this.instance = player_instance;
  this.game = game_instance;
  this.index = index;
  
  //Set up initial values for our state information
  this.size = { x:5, y:5, hx:2.5, hy:2.5 }; // 5+5 = 10px long, 2.5+2.5 = 5px wide
  this.state = 'not-connected';
  this.visible = "visible"; // Tracks whether client is watching game
  this.onwall = false;
  this.kicked = false;
  this.hidden_count = 0;
  this.inactive = false;
  this.inactive_count = 0;
  this.lagging = false;
  this.lag_count = 0;
  this.message = '';

  this.info_color = 'rgba(255,255,255,0)';
  this.id = '';
  this.curr_background = 0; // keep track of current background val
  this.avg_score = 0; // keep track of average score, for bonus
  this.total_points = 0; // keep track of total score, for paying participant

  //This is used in moving us around later
  this.old_state = {pos:{x:0,y:0}};

  //The world bounds we are confined to
  this.pos_limits = {
    x_min: this.size.hx,
    x_max: this.game.world.width - this.size.hx,
    y_min: this.size.hy,
    y_max: this.game.world.height - this.size.hy
  };
  this.pos = null;
  this.angle = null;
  this.speed = this.game.min_speed;
  this.destination = this.pos;
  this.old_speed = this.speed;
  this.old_angle = this.angle;
  this.color = 'white';
}; 

// Inherits player properties
var bot = function(game_instance, condition, index) {
  this.base = game_player;
  this.base(game_instance, null, index);
  this.bot = true;
  this.movementInfo = this.game.getBotInfo(condition, index);
};

// server side we set the 'game_core' class to a global type, so that
// it can use it in other files (specifically, game.server.js)
if('undefined' != typeof global) {
  module.exports = global.game_core = game_core;
  module.exports = global.game_player = game_player;
}

// HELPER FUNCTIONS

game_core.prototype.initializeClientPlayers = function(numBots) {
  var players = [];
  for (var i = 0; i < numBots + 1; i++) {
    players.push({
      id: null,
      instance: null,
      player: new game_player(this,null,false)
    });
  }
  return players;
};

game_core.prototype.initializePlayers = function(trialInfo) {
  // Add trial-specific info
  var playerObj = this.players[0];
  playerObj.player = _.extend(playerObj.player, {
    pos : this.getInitPos(trialInfo, 0),
    angle : get_random_angle(),
    destination : this.getInitPos(trialInfo, 0)
  });
  return [playerObj].concat(this.initializeBots(this.trialInfo));
};

game_core.prototype.initializeBots = function(trialInfo) {
  var that = this;
  return _.map(_.range(trialInfo.numBots), function(index) {
    var pid = utils.UUID();
    var bot = new bot(that, trialInfo, index);
    return {
      id: pid,
      instance : 'bot' + index,
      player: _.extend(bot, {
	pos : that.getInitPos(trialInfo, index),
	angle : get_random_angle()
      })
    };
  });
};

game_core.prototype.getInitPos = function(condition, index) {
  // Note: utils.readCSV might be syncronous & blocking
  var pos = utils.readCSV("../metadata/" + condition.botPositions);
  return {x: parseFloat(pos[index]['x_pos']),
	  y: parseFloat(pos[index]['y_pos'])};
};

game_core.prototype.getBotInfo = function(condition, index) {
  var botInput = utils.readCSV("../metadata/" + condition.botPositions);
  return _.filter(botInput, function(line) {
    return parseInt(line.pid) === index;
  });
};

game_core.prototype.getScoreInfo = function(condition) {
  return utils.readCSV("../metadata/" + condition.background );  
};

// Method to easily look up player 
game_core.prototype.get_player = function(id) {
  var result = _.find(this.players, function(e){ return e.id == id; });
  return result.player;
};

// Method to get list of players that aren't the given id
game_core.prototype.get_others = function(id) {
  return _.without(_.map(_.filter(this.players, function(e){return e.id != id;}), 
			 function(p){return p.player ? p : null;}), null);
};

// Method to get whole list of players
game_core.prototype.get_active_players = function() {
  return _.without(_.map(this.players, function(p){
    return p.player && !p.player.bot ? p : null;
  }), null);
};

game_core.prototype.get_active_players_and_bots = function() {
  return _.without(_.map(this.players, function(p){
    return p.player ? p : null;
  }), null);
};

game_core.prototype.get_bots = function() {
  return _.without(_.map(this.players, function(p){
    return p.player.bot ? p : null;
  }), null);
};

game_core.prototype.newRound = function() {
  // If you've reached the planned number of rounds, end the game
  if(this.roundNum == this.numRounds - 1) {
    _.map(this.get_active_players(), function(p){
      p.player.instance.disconnect();
    });
  } else {
    // Otherwise, set stuff up for next round
    this.roundNum += 1;
    this.trialInfo = this.trialList[this.roundNum];
    this.players = this.initializePlayers(this.trialInfo);
    this.scoreLocs = this.getScoreInfo(this.trialInfo);
    this.server_send_update();
    // Launch game after countdown;
    setTimeout(function(){
      this.game_started = true;
      this.game_clock = 0;
    }, 3000);
  }
  // Create simulation after initializing everything on first round
  if(this.roundNum == 0) {
    this.physics_interval_id = this.create_physics_simulation();
  }
};

game_core.prototype.getFixedConds = function() {
  return [{
    name: "initialVisible",
    numBots : 0,
    botPositions : "spot-spot-close_init.csv",
    showBackground : true,    
    background: "spot-spot-far_player_bg.csv"
  }, {
    name: "initialInvisible",
    numBots : 0,
    botPositions : "spot-spot-close_init.csv",
    background: "spot-spot-far_player_bg.csv"
  }];
};

game_core.prototype.getShuffledConds = function(conditions) {
  return _.map(conditions, function(condition) {
    var localBackground = Math.random() < .5 ? "wall" : "spot";
    var simulationNum = Math.floor(Math.random() * 30);
    var simulationExtension = "_simulation-" + simulationNum + "-non-social.csv";
    return {
      name : condition,
      botPositions : localBackground + "-" + condition + simulationExtension,
      background : localBackground + "-" + condition + "_player_bg.csv"
    };
  });
};

game_core.prototype.makeTrialList = function() {
  var conditions = _.shuffle(['spot-close','spot-far','wall-close','wall-far']);
  var defaults = {showBackground : false,
		  numBots: 4};
  var fixedConds = this.getFixedConds();
  var shuffledConds = this.getShuffledConds(conditions);
  return _.map(fixedConds.concat(shuffledConds), function(obj) {
    return _.defaults(obj, defaults);
  });
};

// Takes two location objects and computes the distance between them
game_core.prototype.distance_between = function(obj1, obj2) {
  x1 = obj1.x;
  x2 = obj2.x;
  y1 = obj1.y;
  y2 = obj2.y;
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
};

//copies a 2d vector like object from one to another
game_core.prototype.pos = function(a) {return {x:a.x,y:a.y}; };

//Add a 2d vector with another one and return the resulting vector
game_core.prototype.v_add = function(a,b) { return { x:(a.x+b.x).fixed(), y:(a.y+b.y).fixed() }; };


// SERVER FUNCTIONS

// Notifies clients of changes on the server side. Server totally
// handles position and points.
game_core.prototype.server_send_update = function(){
  // Add info about all players
  var player_packet = _.map(this.players, function(p){
    if(p.player){
      return {id: p.id,
              player: {
                pos: p.player.pos,
		destination : p.player.destination,
                cbg: p.player.curr_background,
		tot: p.player.total_points,
                angle: p.player.angle,
                speed: p.player.speed,
		onwall: p.player.onwall,
		kicked: p.player.kicked,
		inactive: p.player.inactive,
		lagging: p.player.lagging}};
    } else {
      return {id: p.id,
              player: null};
    }
  });

  if(this.game_started) {
    var gameState = {
      gs : this.game_started                      // true when game's started
    };
  } else {
    var gameState = {
      gs : this.game_started,                      // true when game's started
      pt : this.players_threshold,
      pc : this.player_count,
      wr : new Date() - this.waiting_start
    };
  }
  var state = _.extend(gameState, {players: player_packet});
  console.log(state.players[0].player);
  //Send the snapshot to the players
  this.state = state;
  console.log(this.get_active_players().length);
  _.map(this.get_active_players(), function(p){
    p.player.instance.emit( 'onserverupdate', state);
  });
};

// This is called every few ms and simulates the world state. This is
// where we update positions 
game_core.prototype.server_update_physics = function() {
  var local_this = this;
  _.forEach(this.get_active_players(), function(p){
    var player = p.player;

    // Stop at destination
    // var r = (local_this.distance_between(player.pos, player.destination) < 8 ?
	  //    0 :
	  //          player.speed);
    var r = player.speed;
    var theta = (player.angle - 90) * Math.PI / 180;
    var new_dir = {
      x : r * Math.cos(theta), 
      y : r * Math.sin(theta)
    };      
    player.old_state.pos = local_this.pos(player.pos) ;
    player.pos = local_this.v_add( player.old_state.pos, new_dir );
    if(player.pos) {
      player.game.check_collision( player );
    }
  });
};

game_core.prototype.update_bots = function() {
  var stepNum = this.game_clock + 1;
  _.forEach(this.get_bots(), function(p){
    var player = p.player;
    var x = parseFloat(player.movementInfo[stepNum]["x_pos"]);
    var y = parseFloat(player.movementInfo[stepNum]["y_pos"]);
    var angle = parseFloat(player.movementInfo[stepNum]["angle"]);
    player.pos = {x:x,y:y};
    player.angle = angle;
    player.game.check_collision( player );
  });
};


game_core.prototype.distance_between = function(obj1, obj2) {
  var x1 = obj1.x;
  var x2 = obj2.x;
  var y1 = obj1.y;
  var y2 = obj2.y;
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
};

// Every second, we print out a bunch of information to a file in a
// "data" directory. We keep EVERYTHING so that we
// can analyze the data to an arbitrary precision later on.
game_core.prototype.writeData = function() {
  var local_game = this;
  _.map(local_game.get_active_players(), function(p) {
    var player_angle = p.player.angle;
    if (player_angle < 0) 
      player_angle = parseInt(player_angle, 10) + 360;
    //also, keyboard inputs,  list of players in visibility radius?
    var line = String(p.id) + ',';
    line += String(local_game.game_clock) + ',';
    line += p.player.visible + ',';
    line += p.player.pos.x +',';
    line += p.player.pos.y +',';
    line += p.player.speed +',';
    line += player_angle +',';
    line += p.player.curr_background +',';
    line += p.player.total_points.fixed(2) +',';
    line += p.player.curr_background +',';
    line += p.player.destination.x +',';
    line += p.player.destination.y;
    local_game.gameDataStream.write(String(line) + "\n",
    				                        function (err) {if(err) throw err;});
  });
};

game_core.prototype.server_newgame = function() {
  var local_gamecore = this;
  
};

//Main update loop
game_core.prototype.update = function() {
  //Update the game specifics
  if(!this.server) 
    client_update();

  //schedule the next update
  this.updateid = window.requestAnimationFrame(this.update.bind(this), 
                                               this.viewport);
};

//For the server, we need to cancel the setTimeout that the polyfill creates
game_core.prototype.stop_update = function() {  

  // Stop old game from animating anymore
  window.cancelAnimationFrame( this.updateid );  

  // Stop loop still running from old game (if someone is still left,
  // game_server.endGame will start a new game for them).
  clearInterval(this.physics_interval_id);
};

game_core.prototype.create_physics_simulation = function() {    
  return setInterval(function(){
    // finish this interval by writing and checking whether it's the end
    if (this.server){
      this.update_physics();
      this.update_bots();
    }
    
    var local_game = this; // need a new local game w/ game clock change
    if(this.server) {
      var active_players = local_game.get_active_players();
      for(i=0;i<active_players.length;i++) {
	var p = active_players[i];
	// ping players to estimate latencies
	p.player.instance.emit('ping', {sendTime : Date.now(),
					tick_num: local_game.game_clock});
	// compute scores
	if(p.player) {

	  var on_wall = local_game.check_collision(p.player)
	  if(on_wall) {
	    p.player.curr_background = 0;
	    p.player.onwall = true;
	  } else if(!this.game_started) {
	    p.player.curr_background = local_game.waiting_background;
	    p.player.onwall = false;
	  } else {
	    p.player.onwall = false;
	  }
	  
	  p.player.avg_score = p.player.avg_score + p.player.curr_background/local_game.game_length;
	  p.player.total_points = p.player.avg_score * local_game.max_bonus;
	  
	  // Handle inactive, hidden, or high latency players...
	  if(p.player.kicked || p.player.inactive || p.player.lagging) {
	    p.player.instance.disconnect();
	  } else {
	    if(p.player.visible == 'hidden') {
	      p.player.hidden_count += 1
	    }
	    if(p.player.hidden_count > local_game.ticks_per_sec*15) { // kick after being hidden for 15 seconds
	      if(local_game.booting) {
		p.player.kicked = true
		console.log('Player ' + p.id + ' will be disconnected for being hidden.')
	      }
	    }
	    var not_changing = p.player.last_speed == p.player.speed && p.player.last_angle == p.player.angle;
	    p.player.last_speed = p.player.speed
	    p.player.last_angle = p.player.angle
	    if(on_wall && not_changing) {
	      p.player.inactive_count += 1
	    }
	    if(p.player.inactive_count > local_game.ticks_per_sec*30) {  // kick after being inactive for 30 seconds
	      if(local_game.booting) {
		if(p.player.lag_count > local_game.game_clock*0.1) {
		  p.player.lagging = true
		  console.log('Player ' + p.id + ' will be disconnected because of latency.')
		} else {
		  p.player.inactive = true
		  console.log('Player ' + p.id + ' will be disconnected for inactivity.')
		}
	      }
	    }
	    if(p.player.latency > this.tick_frequency) {
	      if(p.player.visible != 'hidden') {
		p.player.lag_count += 1
	      }
	    }
	    if(p.player.lag_count > local_game.game_length*0.1) {
	      p.player.lagging = true
	      console.log('Player ' + p.id + ' will be disconnected because of latency.')
	    }
	  }
	}
      }
    }

    if (this.server){
      this.server_send_update();
      this.writeData();
    }
    
    local_game.game_clock += 1;
    
    if(this.server && this.game_started && this.game_clock >= this.game_length) {
      this.stop_update();
      _.map(this.get_active_players(), function(p){
	      p.player.instance.disconnect();
      });
    }
  }.bind(this), this.tick_frequency);
};

game_core.prototype.update_physics = function() {
  if(this.server) {
    this.server_update_physics();
    var t = 0;
    // start reading csv and updating background once game starts
    if(this.game_started && this.game_clock < this.game_length) {
      t = this.game_clock;
    }
    if(t % 1 == 0) {
      var local_game = this;
      _.forEach(local_game.get_active_players(), function(p) {
        loc = {x:local_game.scoreLocs[t]["x_pos"], y:local_game.scoreLocs[t]["y_pos"]};
        dist = local_game.distance_between(loc, p.player.pos);
        if(dist < 50) {
          p.player.curr_background = 1.0;
        } else {
	        p.player.curr_background = 0.10;
        }
      });
    }    
  };
}

//Prevents people from leaving the arena
game_core.prototype.check_collision = function( item ) {
  
  var collision = false
  //Left wall.
  if(item.pos.x <= item.pos_limits.x_min){
    collision = true
    item.pos.x = item.pos_limits.x_min;
  }
  //Right wall
  if(item.pos.x >= item.pos_limits.x_max ){
    collision = true
    item.pos.x = item.pos_limits.x_max;
  }

  //Roof wall.
  if(item.pos.y <= item.pos_limits.y_min) {
    collision = true
    item.pos.y = item.pos_limits.y_min;
  }

  //Floor wall
  if(item.pos.y >= item.pos_limits.y_max ) {
    collision = true
    item.pos.y = item.pos_limits.y_max;
  }

  //Fixed point helps be more deterministic
  item.pos.x = item.pos.x.fixed(4);
  item.pos.y = item.pos.y.fixed(4);
  return collision
};

// MATH FUNCTIONS

get_random_position = function(world) {
  return {
    x: Math.floor((Math.random() * world.width) + 1),
    y: Math.floor((Math.random() * world.height) + 1)
  };
};

// At beginning of round, want to start people close enough 
// together that they can see at least one or two others...
// In circle with radius quarter size of tank.
get_random_center_position = function(world) {
  var theta = Math.random()*Math.PI*2;
  return {
    x: world.width /2 + (Math.cos(theta)* world.width /16),
    y: world.height/2 + (Math.sin(theta)* world.height/16)
  };
}

get_random_angle = function() {
  return Math.floor((Math.random() * 360) + 1);
};

// (4.22208334636).fixed(n) will return fixed point value to n places, default n = 3
Number.prototype.fixed = function(n) { n = n || 3; return parseFloat(this.toFixed(n)); };

function zeros(dimensions) {
  var array = [];

  for (var i = 0; i < dimensions[0]; ++i) {
    array.push(dimensions.length == 1 ? 0 : zeros(dimensions.slice(1)));
  }

  return array;
}

//The remaining code runs the update animations

//The main update loop runs on requestAnimationFrame,
//Which falls back to a setTimeout loop on the server
//Code below is from Three.js, and sourced from links below

//http://paulirish.com/2011/requestanimationframe-for-smart-animating/

//requestAnimationFrame polyfill by Erik Möller
//fixes from Paul Irish and Tino Zijdel
var frame_time = 60 / 1000; // run the local game at 16ms/ 60hz
if('undefined' != typeof(global)) frame_time = 4; //on server we run at 45ms, 22hz

( function () {

  var lastTime = 0;
  var vendors = [ 'ms', 'moz', 'webkit', 'o' ];

  for ( var x = 0; x < vendors.length && !window.requestAnimationFrame; ++ x ) {
    window.requestAnimationFrame = window[ vendors[ x ] + 'RequestAnimationFrame' ];
    window.cancelAnimationFrame = window[ vendors[ x ] + 'CancelAnimationFrame' ] || window[ vendors[ x ] + 'CancelRequestAnimationFrame' ];
  }

  if ( !window.requestAnimationFrame ) {
    window.requestAnimationFrame = function ( callback, element ) {
      var currTime = Date.now(), timeToCall = Math.max( 0, frame_time - ( currTime - lastTime ) );
      var id = window.setTimeout( function() { callback( currTime + timeToCall ); }, timeToCall );
      lastTime = currTime + timeToCall;
      return id;
    };
  }

  if ( !window.cancelAnimationFrame ) {
    window.cancelAnimationFrame = function ( id ) { clearTimeout( id ); };
  }
}() );
