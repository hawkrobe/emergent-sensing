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
  
  this.debug = options.debug;
  this.test = options.test;
  
  //Dimensions of world -- Used in collision detection, etc.
  this.world = {width : 485, height : 280};  // 160cm * 3
  this.advanceButton = {trueX: 2 * this.world.width / 5,
			trueY: 3 * this.world.height / 4,
			width: this.world.width / 5,
			height: this.world.height / 6};
    
  //How often the players move forward <global_speed>px in ms.
  this.tick_frequency = 125;     //Update 8 times per second
  this.ticks_per_sec = 1000/125;
  this.numFadeSteps = 10;
  
  this.waiting_room_limit = 5; // set maximum waiting room time (in minutes)
  this.round_length = 1.0; // set how long each round will last (in minutes)
  this.max_bonus = 15.0 / 60 * this.round_length; // total $ players can make in bonuses

  // If set to true, boot players for inactivity, hidden tab, and latency issue
  this.booting = true;
  this.game_started = true;
  this.players_threshold = 1;

  this.star_point_value = 1/4800.0;
  this.active_point_value = 1/3200.0;
  
  // game and waiting length in seconds
  this.game_length = this.round_length*60*this.ticks_per_sec;

  //The speed at which the clients move (e.g. # px/tick)
  this.min_speed = 17 /this.ticks_per_sec; // 7.5cm * 3 * .5s 
  this.max_speed = 57 /this.ticks_per_sec; // 7.5cm * 3 * .5s 
  this.self_color = '#2288cc';
  this.other_color = 'white';

  // minimun wage per tick
  // background = us_min_wage_per_tick * this.game_length / this.max_bonus;
  var us_min_wage_per_tick = 7.25 / (60*60*(1000 / this.tick_frequency));
  this.waiting_background = 0.2;
  this.waiting_start = new Date(); 

  this.roundNum = -1;
  this.numRounds = 6;
  this.game_clock = 0;

  this.currScoreLocs = {spot : {x : '', y : ''}, wall : {x : '', y: ''}};
  this.closeScoreLoc = 0;
  this.farScoreLoc = 0;
  
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
    // Randomize which score field players get
    this.backgroundCondition = _.sample(["wall", "spot"]);
    console.log('assigned to ' + this.backgroundCondition + ' condition');
    // Randomize which half the close score field appears
    this.closeHalf = _.sample(['first', 'second']);
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
  this.hidden = false;
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
  this.active_points = 0; // keep track of total score, for paying participant
  this.star_points = 0; // keep track of total score, for paying participant


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
  this.isBot = true;
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
  var initInfo = this.getInitInfo(trialInfo, 0);
  playerObj.player = _.extend(playerObj.player, {
    pos : initInfo.pos,
    angle : initInfo.angle,
    destination : initInfo.pos
  });
  var bots = this.initializeBots(this.trialInfo);
  return [playerObj].concat(bots);
};

game_core.prototype.initializeBots = function(trialInfo) {
  var botList = [];
  for (var i = 0; i < trialInfo.numBots; i++) {
    var pid = utils.UUID();
    var localBot = new bot(this, trialInfo, i + 1);
    var initInfo = this.getInitInfo(trialInfo, i + 1);
    botList.push({
      id: pid,
      instance : 'bot' + i,
      player: _.extend(localBot, {
	pos : initInfo.pos,
	angle : initInfo.angle
      })
    });
  }
  return botList;
};



game_core.prototype.getInitInfo = function(condition, index) {
  // Note: utils.readCSV might be syncronous & blocking
  var positions = utils.readCSV("../metadata/v2/" + condition.positions);
  return {
    pos : {x: parseFloat(positions[index]['x_pos']),
	   y: parseFloat(positions[index]['y_pos'])},
    angle : parseFloat(positions[index]['angle'])
  };
};

game_core.prototype.getBotInfo = function(condition, index) {
  var botInput = utils.readCSV("../metadata/v2/" + condition.positions);
  return _.filter(botInput, function(line) {
    return parseInt(line.pid) === index;
  });
};

game_core.prototype.getWallScoreInfo = function(condition) {
  return _.map(utils.readCSV("../metadata/v2/" + condition.wallBackground ), row => {
    return _.mapObject(row, (val, key) => parseFloat(val));
  });
};

game_core.prototype.getSpotScoreInfo = function(condition) {
  return _.map(utils.readCSV("../metadata/v2/" + condition.spotBackground ), row => {
    return _.mapObject(row, (val, key) => parseFloat(val));
  });
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
    return p.player && !p.player.isBot ? p : null;
  }), null);
};

game_core.prototype.get_active_players_and_bots = function() {
  return _.without(_.map(this.players, function(p){
    return p.player ? p : null;
  }), null);
};

game_core.prototype.get_bots = function() {
  return _.without(_.map(this.players, function(p){
    return p.player.isBot ? p : null;
  }), null);
};


game_core.prototype.initRound = function() {
  this.stop_update();
  this.roundNum += 1;
  this.trialInfo = this.trialList[this.roundNum];
  this.players = this.initializePlayers(this.trialInfo);
  this.game_clock = 0;
  this.roundNum -= 1;
  this.server_send_update();
  this.stop_update();
};


game_core.prototype.newRound = function() {
  // If you've reached the planned number of rounds, end the game
  if(this.roundNum == this.numRounds - 1) {
    _.map(this.get_active_players(), function(p){
      p.player.instance.disconnect();
    });
  } else {
    // Otherwise, set stuff up for next round
    this.stop_update();
    this.roundNum += 1;
    this.roundStarted = new Date();
    this.trialInfo = this.trialList[this.roundNum];
    this.players = this.initializePlayers(this.trialInfo);
    this.trialInfo.wallScoreLocs = this.getWallScoreInfo(this.trialInfo);
    this.trialInfo.spotScoreLocs = this.getSpotScoreInfo(this.trialInfo);
    this.closeScoreLoc = 0;
    this.farScoreLoc = 0;
    this.game_clock = 0;
    // (Re)start simulation
    this.physics_interval_id = this.create_physics_simulation();
    this.server_send_update();
  }
};

game_core.prototype.getPositionFile = function(positionSimulationNum) {
  return(['v2', this.backgroundCondition, 'close_first-asocial-smart-0',
	  positionSimulationNum, 'social-simulation.csv'].join('-'));
}

game_core.prototype.getFixedConds = function() {
  
  var bg_list = _.shuffle(_.range(100));
  var position_list = _.shuffle(_.range(100));

  return [{
    name: "initialVisible1",
    numBots : 0,
    simulationNum : visibleSimulationNum1,
    positions : this.getPositionFile(position_list[0]),
    wallBackground : 'wall-demo' + bg_list[0] + '_bg.csv',
    spotBackground : 'spot-demo' + bg_list[0] + '_bg.csv',
    showBackground : true,
    nonsocial: true,
    oneBackground : true
  }, {
    name: "initialVisible2",
    numBots : 0,
    simulationNum : visibleSimulationNum2,
    positions : this.getPositionFile(position_list[1]),
    wallBackground : 'wall-demo' + bg_list[1] + '_bg.csv',
    spotBackground : 'spot-demo' + bg_list[1] + '_bg.csv',
    showBackground : true,
    nonsocial: true,
    oneBackground : true
  }, {
    name: "initialInvisible1",
    numBots : 0,
    simulationNum : invisibleSimulationNum1,
    positions : this.getPositionFile(position_list[2]),
    wallBackground : 'wall-demo' + bg_list[2] + '_bg.csv',
    spotBackground : 'spot-demo' + bg_list[2] + '_bg.csv', 
    nonsocial: true,
    oneBackground : true
  }, {
    name: "initialInvisible2",
    numBots : 0,
    simulationNum : invisibleSimulationNum2,
    positions : this.getPositionFile(position_list[3]),
    wallBackground : 'wall-demo' + bg_list[3] + '_bg.csv',
    spotBackground : 'spot-demo' + bg_list[3] + '_bg.csv', 
    nonsocial: true,
    oneBackground : true
  }];
};

game_core.prototype.getShuffledConds = function(conditions) {
  return _.map(_.shuffle(conditions), function(condition) {

    var simulationNum = _.sample(_.range(100));
    
    var numBots = condition === 'social' ? 4 : 0;

    var conditionPrefix = 'v2-' + this.backgroundCondition + '-close_' + this.closeHalf;
    var fileStr = conditionPrefix + '-asocial-smart-0-' + simulationNum + '-social-';
    var match = fileStr + 'matched_bg.csv';
    var mismatch = fileStr + 'mismatch_bg.csv';
    
    return {
      name : condition,
      nonsocial: condition === 'nonsocial',      
      numBots : numBots,
      simulationNum : simulationNum,
      positions : fileStr + 'simulation.csv',
      wallBackground : this.backgroundCondition === 'wall' ? match : mismatch,
      spotBackground : this.backgroundCondition === 'wall' ? mismatch : match
    };
  }, this);
};

game_core.prototype.makeTrialList = function() {
  var conditions = _.shuffle(['social', 'nonsocial']);
  var defaults = {showBackground : false,
		  oneBackground : false,
		  wallBG : this.backgroundCondition == "wall"};
  var fixedConds = this.getFixedConds();
  var shuffledConds = this.getShuffledConds(conditions);
//  return _.map(shuffledConds, function(obj) {  
  return _.map(fixedConds.concat(shuffledConds), function(obj) {
    return _.defaults(obj, defaults);
  });
};

//copies a 2d vector like object from one to another
game_core.prototype.pos = function(a) {
  return {x:a.x,y:a.y};
};

game_core.prototype.validLoc = function(obj) {
  return parseInt(obj.x) && parseInt(obj.y);
};

//Add a 2d vector with another one and return the resulting vector
game_core.prototype.v_add = function(a,b) {
  return { x:(a.x+b.x).fixed(), y:(a.y+b.y).fixed() };
};

game_core.prototype.distance = function(obj1, obj2) {
  if(this.validLoc(obj1) && this.validLoc(obj2)) {
    var x1 = obj1.x;
    var x2 = obj2.x;
    var y1 = obj1.y;
    var y2 = obj2.y;
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
  } else {
    return Infinity;
  }
};

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
		act: p.player.active_points,
		star: p.player.star_points,
		onwall: p.player.onWall,		
                angle: p.player.angle,
                speed: p.player.speed,
		hidden: p.player.hidden,
		inactive: p.player.inactive,
		lagging: p.player.lagging}};
    } else {
      return {id: p.id,
              player: null};
    }
  });

  var state = {
    clock : this.game_clock,
    roundNum : this.roundNum,
    gs : this.game_started,
    players: player_packet,
    condition: this.backgroundCondition,
    trialInfo: {nonsocial : this.trialInfo.nonsocial,
		oneBackground : this.trialInfo.oneBackground,
		spotScoreLoc: this.currScoreLocs['spot'],
		wallScoreLoc: this.currScoreLocs['wall'],
		showBackground : this.trialInfo.showBackground,
		wallBG : this.trialInfo.wallBG}
  };
  //Send the snapshot to the players
  this.state = state;
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
    // player.speed = (local_this.distance(player.pos, player.destination) < 8 ?
    // 		    0 :
    // 		    player.speed);
    var theta = (player.angle - 90) * Math.PI / 180;
    var new_dir = {
      x : player.speed * Math.cos(theta), 
      y : player.speed * Math.sin(theta)
    };      
    player.old_state.pos = local_this.pos(player.pos) ;
    player.pos = local_this.v_add( player.old_state.pos, new_dir );
    if(player.pos) {
      player.game.checkCollision( player, {tolerance: 0, stop: true});
    }
  });
};

game_core.prototype.update_bots = function() {
  var stepNum = this.game_clock;// + 1;
  _.forEach(this.get_bots(), function(p){
    var player = p.player;
    var x = parseFloat(player.movementInfo[stepNum]["x_pos"]);
    var y = parseFloat(player.movementInfo[stepNum]["y_pos"]);
    var angle = parseFloat(player.movementInfo[stepNum]["angle"]);
    player.pos = {x:x,y:y};
    player.angle = angle;
    player.game.checkCollision( player , {tolerance: 0, stop: true});
  });
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
    line += p.player.destination.y + ',';
    line += p.player.onWall + ',';
    line += String(local_game.closeScoreLoc) + ',';
    line += String(local_game.farScoreLoc) + ',';
    line += String(local_game.roundNum) + ',';
    line += String(local_game.trialInfo.name)  + ',';
    line += local_game.backgroundCondition + ',';
    line += local_game.closeHalf + ',';
    line += String(local_game.trialInfo.simulationNum);

    local_game.gameDataStream.write(String(line) + "\n",
    				    function (err) {if(err) throw err;});
  });
};

//Main update loop
game_core.prototype.update = function() {
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

game_core.prototype.getInClose = function(whichHalf) {

  var onOne = {'first' : 8, 'second' : 38}[whichHalf] * this.ticks_per_sec;
  var offOne = {'first' : 9, 'second' : 39}[whichHalf] * this.ticks_per_sec;
  var onTwo = {'first' : 10, 'second' : 40}[whichHalf] * this.ticks_per_sec;
  var offTwo = {'first' : 13, 'second' : 43}[whichHalf] * this.ticks_per_sec;
  var onThree = {'first' : 14, 'second' : 44}[whichHalf] * this.ticks_per_sec;
  var offThree = {'first' : 17, 'second' : 47}[whichHalf] * this.ticks_per_sec;
  var onFour = {'first' : 18, 'second' : 48}[whichHalf] * this.ticks_per_sec;
  var offFour = {'first' : 20, 'second' : 50}[whichHalf] * this.ticks_per_sec;

  var t = this.game_clock;
  
  var inTimeWindow =  (t > onOne && t < offOne) || (t > onTwo && t < offTwo) || (t > onThree && t < offThree) || (t > onFour && t < offFour);

  return(inTimeWindow);
}

game_core.prototype.updateCloseScoreLoc = function(p) {
  // Move score field to player at specified time (in seconds)
  // (i.e. a second before the bot intervention in the specified half)

  var farHalf;
  if(this.closeHalf == 'first') {
    farHalf = 'second';
  } else {
    farHalf = 'first';
  }

  var inTimeWindow = this.getInClose(this.closeHalf);

  // place score 
  if(inTimeWindow) {
    this.closeScoreLoc = 1;
  }

  // Turn off score loc after endTime
  if (!inTimeWindow) {
    this.closeScoreLoc = 0;
  } 


  var inTimeWindow = this.getInClose(farHalf);

  // place score 
  if(inTimeWindow) {
    this.farScoreLoc = 1;
  }

  // Turn off score loc after endTime
  if (!inTimeWindow) {
    this.farScoreLoc = 0;
  } 

};

game_core.prototype.updateScores = function(p) {
  if(p) {

    // Only do close spotlight intervention in expt conditions
    if(_.contains(['social', 'nonsocial'], this.trialInfo.name)) {
      this.updateCloseScoreLoc(p);
    }

    this.currScoreLocs = {
      'spot' : {
	x : this.trialInfo.spotScoreLocs[this.game_clock]["x_pos"],
	y : this.trialInfo.spotScoreLocs[this.game_clock]["y_pos"]},
      'wall' : {
	x : this.trialInfo.wallScoreLocs[this.game_clock]["x_pos"],
	y : this.trialInfo.wallScoreLocs[this.game_clock]["y_pos"]}};

    // if oneBackground set, only use background from your condition
    // otherwise concatenate score fields
    var that = this;    
    var dist = (this.trialInfo.oneBackground ?
		this.distance(this.currScoreLocs[this.backgroundCondition], p.pos) :
		_.min(_.map(_.values(this.currScoreLocs),
			    function(x) {return that.distance(x, p.pos);})));

    // check whether on wall
    p.onWall = this.checkCollision(p, {tolerance: 0, stop: false});
    
    // get full points when inside spotlight & not on wall
    p.curr_background = !p.onWall & (dist < 50 | this.closeScoreLoc);
    
    p.star_points += p.curr_background;
    p.active_points += p.onWall; 

    p.total_points += (this.star_point_value * p.curr_background +
		       this.active_point_value * (1 - p.onWall));
  }
};

game_core.prototype.handleHiddenTab = function(p, id) {
  // count ticks with hidden tab
  if(p.visible == 'hidden') {
    p.hidden_count += 1;
  }

  // kick after being hidden for 15 seconds  
  if(p.hidden_count > this.ticks_per_sec * 30 && !this.debug) { 
    p.hidden = true;
    console.log('Player ' + id + ' will be disconnected for being hidden.');
  }
};

game_core.prototype.handleInactivity = function(p, id) {
  // Player is inactive if they're sitting in one place; reset after they move again
  if(p.onWall) {
    p.inactive_count += 1;
  } else {
    p.inactive_count = 0;
  }
  
  // kick after being inactive for 30 seconds
  if(p.inactive_count > this.ticks_per_sec*30 && !this.debug) {  
    p.inactive = true;
    console.log('Player ' + id + ' will be disconnected for inactivity.');
  }
};

game_core.prototype.handleBootingConditions = function(p, id) {
  if(this.booting) {
    this.handleHiddenTab(p, id);
    this.handleInactivity(p, id);
  }
};

game_core.prototype.create_physics_simulation = function() {    
  return setInterval(function(){
    // finish this interval by writing and checking whether it's the end
    if (this.server){
      this.server_update_physics();
      this.update_bots();

      var active_players = this.get_active_players();
      for (var i=0; i < active_players.length; i++) {
	var p = active_players[i];

	// ping players to estimate latencies
	p.player.instance.emit('ping', {sendTime : Date.now(),
					tick_num: this.game_clock});
	// handle scoring
	this.updateScores(p.player);

	// Handle inactive, hidden, or high latency players...
	this.handleBootingConditions(p.player, p.id);
      }

      this.server_send_update();
      this.writeData();
      this.game_clock += 1;

      for (var i=0; i < active_players.length; i++) {
	var p = active_players[i].player;

	if((p.hidden || p.inactive || p.lagging) && !this.debug) {
	  p.instance.disconnect();
	} 
      }

    }

    // Pause & show player next instruction set when time is out
    if(this.server && this.game_started && this.game_clock >= this.game_length) {
      this.stop_update();
      _.map(this.get_active_players(), function(p){
	p.player.curr_background = 0;
	p.player.instance.send('s.showInstructions');
      });
    }
  }.bind(this), this.tick_frequency);
};

game_core.prototype.showInstructions = function() {
  _.map(this.get_active_players(), function(p){
    p.player.instance.send('s.showInstructions');
  });
}

//Prevents people from leaving the arena
game_core.prototype.checkCollision = function(item, options) {
  var collision = 0;
  var tolerance = options.tolerance;
  var stop = options.stop;
  
  //Left wall.
  if(item.pos.x <= item.pos_limits.x_min + tolerance){
    collision = 1;
    item.pos.x = stop ? item.pos_limits.x_min : item.pos.x;
  }
  //Right wall
  if(item.pos.x >= item.pos_limits.x_max - tolerance){
    collision = 1;
    item.pos.x = stop ? item.pos_limits.x_max : item.pos.x;
  }

  //Roof wall.
  if(item.pos.y <= item.pos_limits.y_min + tolerance) {
    collision = 1;
    item.pos.y = stop ? item.pos_limits.y_min : item.pos.y;
  }

  //Floor wall
  if(item.pos.y >= item.pos_limits.y_max - tolerance) {
    collision = 1;
    item.pos.y = stop ? item.pos_limits.y_max : item.pos.y;
  }

  //Fixed point helps be more deterministic
  item.pos.x = item.pos.x.fixed(4);
  item.pos.y = item.pos.y.fixed(4);
  return collision;
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
