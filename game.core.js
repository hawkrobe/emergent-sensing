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
var has_require = typeof require !== 'undefined'

if( typeof _ === 'undefined' ) {
    if( has_require ) {
        _ = require('underscore')
    }
    else throw new Error('mymodule requires underscore, see http://underscorejs.org');
}

var game_core = function(game_instance){

    // Define some variables specific to our game to avoid
    // 'magic numbers' elsewhere
    this.self_color = '#2288cc';
    this.other_color = 'white';
    
    //Store the instance, if any (passed from game.server.js)
    this.instance = game_instance;

    //Store a flag if we are the server instance
    this.server = this.instance !== undefined;

    //Store a flag if a newgame has been initiated.
    //Used to prevent the loop from continuing to start newgames during timeout.
    this.newgame_initiated_flag = false;

    //Dimensions of world -- Used in collision detection, etc.
    this.world = {width : 485, height : 280};  // 160cm * 3

    // set how long each round will last (in minutes)
    this.round_length = 6

    //How often the players move forward <global_speed>px in ms.
    this.tick_frequency = 125;     //Update 8 times per second

    //The speed at which the clients move (e.g. # px/tick)
    this.min_speed = 21 / (1000 / this.tick_frequency); // 7.5cm * 3 * .5s 
    this.max_speed = 70 / (1000 / this.tick_frequency); // 7.5cm * 3 * .5s 
    
    this.base_pay = .125; // controls conversion b/w background val and cum. points
    this.max_bonus = .625; // total $ players can make in bonuses 

    // This draws the circle in which players can see other players
    this.visibility_radius = 77; // 27.5cm * 3

    //Number of players needed to start the game
    this.players_threshold = 2;

    // Background field holds the background values
    this.background_vals = null;

    //Players will replay over and over, so we keep track of which number we're on,
    //to print out to data file
    this.round_num = 0;
    
    // Determines which background val file we read from
    this.noise_level = 0;

    //If hiding_enabled is true, players will only see others in their visibility radius
    this.hiding_enabled = false;

    //We create a player set, passing them the game that is running
    //them, as well. Both the server and the clients need separate
    //instances of both players, but the server has more information
    //about who is who. Clients will be given this info later.
    if(this.server) {
        this.players = [{
            id: this.instance.player_instances[0].id, 
            player: new game_player(this,this.instance.player_instances[0].player)
        }];
        this.game_clock = 0;
    } else {
        this.players = [{
            id: null, 
            player: new game_player(this)
        }]
    }

    //Start a physics loop, this is separate to the rendering
    //as this happens at a fixed frequency. Capture the id so
    //we can shut it down at end.
    this.physics_interval_id = this.create_physics_simulation();
}; 

/* The player class
        A simple class to maintain state of a player on screen,
        as well as to draw that state when required.
*/
var game_player = function( game_instance, player_instance) {
    //Store the instance, if any
    this.instance = player_instance;
    this.game = game_instance;

    //Set up initial values for our state information
    this.size = { x:14, y:14, hx:7, hy:7 }; // Approximately 5cm * 3 long
    this.state = 'not-connected';
    this.visible = "visible"; // Tracks whether client is watching game
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
    if (this.game.server) {
        this.pos = get_random_position(this.game.world);
        this.angle = get_random_angle();
    } else {
        this.pos = null;
        this.angle = null;
    }
    this.speed = this.game.min_speed;
    this.color = 'white';
}; 

// server side we set the 'game_core' class to a global type, so that
// it can use it in other files (specifically, game.server.js)
if('undefined' != typeof global) {
    module.exports = global.game_core = game_core;
    module.exports = global.game_player = game_player;
}

// HELPER FUNCTIONS

// Method to easily look up player 
game_core.prototype.get_player = function(id) {
    var result = _.find(this.players, function(e){ return e.id == id; });
    return result.player
};

// Method to get list of players that aren't the given id
game_core.prototype.get_others = function(id) {
    return _.without(_.map(_.filter(this.players, function(e){return e.id != id}), 
        function(p){return p.player ? p : null}), null)
};

// Method to get whole list of players
game_core.prototype.get_active_players = function() {
    return _.without(_.map(this.players, function(p){
        return p.player ? p : null}), null)
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
game_core.prototype.pos = function(a) { return {x:a.x,y:a.y}; };

//Add a 2d vector with another one and return the resulting vector
game_core.prototype.v_add = function(a,b) { return { x:(a.x+b.x).fixed(), y:(a.y+b.y).fixed() }; };


// SERVER FUNCTIONS

// Notifies clients of changes on the server side. Server totally
// handles position and points.
game_core.prototype.server_send_update = function(){
    //Make a snapshot of the current state, for updating the clients
    var local_game = this;
    

    // Add info about all players
    var player_packet = _.map(local_game.players, function(p){
        if(p.player){
            return {id: p.id,
                    player: {
                        pos: p.player.pos,
                        cbg: p.player.curr_background,
			tot: p.player.total_points,
                        angle: p.player.angle,
                        speed: p.player.speed}}
        } else {
            return {id: p.id,
                    player: null}
        }
    })
    var state = {
        cond: this.condition,                       //dynamic or ballistic?
        de  : this.hiding_enabled,                  // true to see angle
        g2w : this.good2write,                      // true when game's started
    };
    _.extend(state, {players: player_packet})

    //Send the snapshot to the players
    this.state = state;
    _.map(local_game.get_active_players(), function(p){
	    p.player.instance.emit( 'onserverupdate', state)})
};

// This is called every few ms and simulates the world state. This is
// where we update positions 
game_core.prototype.server_update_physics = function() {
    var local_gamecore = this;
    _.map(this.get_active_players(), function(p){
        var player = p.player;
        r1 = player.speed; 
        theta1 = (player.angle - 90) * Math.PI / 180;
        player.old_state.pos = local_gamecore.pos(player.pos) ;
        var new_dir = {
            x : r1 * Math.cos(theta1), 
            y : r1 * Math.sin(theta1)
        };  
        player.pos = player.game.v_add( player.old_state.pos, new_dir );
        player.game.check_collision( player );
        // Also update the current points at this new position
    })
};

// Every second, we print out a bunch of information to a file in a
// "data" directory. We keep EVERYTHING so that we
// can analyze the data to an arbitrary precision later on.
game_core.prototype.writeData = function() {

    // // Some funny business going on with angles being negative, so we correct for that
    // var host_angle_to_write = this.players.self.angle;
    // var other_angle_to_write = this.players.other.angle;
    // var file_path ;
    // if (this.players.self.angle < 0)
    //     host_angle_to_write = parseInt(this.players.self.angle, 10) + 360;
    // if (this.players.other.angle < 0)
    //     other_angle_to_write = parseInt(this.players.other.angle, 10)  + 360;
    file_path = "data/games/game_" + this.game_id + ".csv";
    var local_game = this;
    _.map(local_game.get_active_players(), function(p) {
	    var player_angle = p.player.angle;
	    if (player_angle < 0) 
		player_angle = parseInt(player_angle, 10) + 360;
	    //also, keyboard inputs,  list of players in visibility radius?
	    var line = String(p.id) + ',';
	    line += String(local_game.round_num) + ',';
	    line += String(local_game.game_clock) + ',';
	    line += String(local_game.noise_level) + ',';
	    line += p.player.visible + ',';
	    line += p.player.pos.x +',';
	    line += p.player.pos.y +',';
	    line += p.player.speed +',';
	    line += player_angle +',';
	    line += p.player.curr_background +',';
	    line += p.player.total_points.fixed(2) ;
	    local_game.fs.appendFile(file_path, String(line) + "\n",
			       function (err) {if(err) throw err;});
	    console.log("Wrote: " + line);
	})
};

// This is a really important function -- it gets called when a round
// has been completed, and updates the database with how much money
// people have made so far. This way, if somebody gets disconnected or
// something, we'll still know what to pay them.
game_core.prototype.server_newgame = function() {
    var local_gamecore = this;

    // Update number of games remaining
    this.round_num += 1;

    // Don't want players moving during countdown
    _.map(local_gamecore.get_active_players(), function(p) {p.player.speed = 0;})

    // Don't want to write to file during countdown -- too confusing
    this.good2write = false;

    // Don't want people signalling until after countdown/validated input
    this.hidden_enabled = true;

    //Reset positions
    this.server_reset_positions();

    //Tell clients about it so they can call their newgame procedure (which does countdown)
    _.map(local_gamecore.get_active_players(), function(p) {p.player.instance.send('s.begin_game.')})

    // Launch game after countdown;
    setTimeout(function(){
        local_gamecore.good2write = true;
        _.map(local_gamecore.get_active_players(), function(p) {p.player.speed = local_gamecore.min_speed});
        local_gamecore.game_clock = 0;
    }, 3000);
};

/*
  The following code should NOT need to be changed
*/

//Main update loop -- don't worry about it
game_core.prototype.update = function() {
    //Update the game specifics
    if(!this.server) 
        client_update();
    else 
        this.server_send_update();
    
    //schedule the next update
    this.updateid = window.requestAnimationFrame(this.update.bind(this), 
                                                 this.viewport);
};

// This gets called every iteration of a new game to reset positions
game_core.prototype.server_reset_positions = function() {
    var local_gamecore = this;
    _.map(local_gamecore.get_active_players(), function(p) {
        p.player.pos = get_random_center_position(local_gamecore.world);
        p.player.angle = get_random_angle(local_gamecore.world);
    })
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
        if (this.good2write) {
            this.writeData();
        }
        this.game_clock += 1;

	// Ping to get latency for this update
	var local_game = this;
	if(this.server & this.good2write) {
	    _.map(local_game.get_active_players(), function(p){
		    p.player.instance.emit('ping', {sendTime : Date.now(),
					            tick_num: local_game.game_clock})})}
    this.update_physics();	
    }.bind(this), this.tick_frequency);
};

game_core.prototype.update_physics = function() {
    if(this.server) {
        this.server_update_physics();
        // start reading csv and updating background once game starts
	if(this.good2write) {
            var local_game = this;
            var background_vals = []
            local_game.fs.open('/home/pkrafft/couzin/output/background/1-1en01/t' + local_game.game_clock + '.csv', 'r', function(err, fd) {
                if(err) throw err;
                _.map(local_game.get_active_players(), function(p){
		    var pos = p.player.pos;
		    var loc = (280*5 + 1)*Math.round(pos.x) + Math.round(pos.y)*5;
		    local_game.fs.read(fd, new Buffer(4), 0, 4, loc, function(err, bytesRead, buffer) {
                        if(err) throw err;
			    //			console.log("on tick " + local_game.game_clock + ", updated points earned to " + Number(buffer.toString('utf8')))
                        p.player.curr_background = Number(buffer.toString('utf8'))
			p.player.avg_score = (((p.player.avg_score * (local_game.game_clock - 1)) + p.player.curr_background) 
					      / local_game.game_clock)
			p.player.total_points = (local_game.base_pay*(local_game.game_clock/480) 
						 + p.player.avg_score * local_game.max_bonus)
			local_game.fs.close(fd, function(){})
                    });
                });
            })
        }
    }
};

//Prevents people from leaving the arena
game_core.prototype.check_collision = function( item ) {
    //Left wall.
    if(item.pos.x <= item.pos_limits.x_min)
        item.pos.x = item.pos_limits.x_min;
 
    //Right wall
    if(item.pos.x >= item.pos_limits.x_max )
        item.pos.x = item.pos_limits.x_max;
       
    //Roof wall.
    if(item.pos.y <= item.pos_limits.y_min) 
        item.pos.y = item.pos_limits.y_min;
    
    //Floor wall
    if(item.pos.y >= item.pos_limits.y_max ) 
        item.pos.y = item.pos_limits.y_max;

    //Fixed point helps be more deterministic
    item.pos.x = item.pos.x.fixed(4);
    item.pos.y = item.pos.y.fixed(4);
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
        x: world.width /2 + (Math.cos(theta)* world.width /4),
        y: world.height/2 + (Math.sin(theta)* world.height/4)
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
if('undefined' != typeof(global)) frame_time = 45; //on server we run at 45ms, 22hz

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
