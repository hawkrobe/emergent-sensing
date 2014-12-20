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
    this.other_color = '#cc0000';
    this.big_payoff = 4
    this.little_payoff = 1
    
    // Create targets and assign fixed position
    this.targets = {
        top :    new target({x : 360, y : 120}),
	    bottom : new target({x : 360, y : 360})};                  

    //Store the instance, if any (passed from game.server.js)
    this.instance = game_instance;

    //Store a flag if we are the server instance
    this.server = this.instance !== undefined;

    //Store a flag if a newgame has been initiated.
    //Used to prevent the loop from continuing to start newgames during timeout.
    this.newgame_initiated_flag = false;

    //Dimensions of world -- Used in collision detection, etc.
    this.world = {width : 720, height : 480};    

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
    
    //The speed at which the clients move (e.g. 10px/tick)
    this.global_speed = 10;

    //Set to true if we want players to act under noise
    this.noise = false;

    //How often the players move forward <global_speed>px in ms.
    this.tick_frequency = 666;

    //Number of games left
    this.games_remaining = 50;

    //Players will replay over and over, so we keep track of which number we're on,
    //to print out to data file
    this.game_number = 1;

    //If draw_enabled is true, players will see their true angle. If it's false,
    //players can set their destination and keep it hidden from the other player.
    this.draw_enabled = true;

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
    this.size = { x:16, y:16, hx:8, hy:8 };
    this.state = 'not-connected';
    this.visible = "visible"; // Tracks whether client is watching game
    this.message = '';
    
    this.info_color = 'rgba(255,255,255,0)';
    this.id = '';
    this.targets_enabled = false; // If true, will display targets
    this.destination = null; // Last place client clicked
    this.points_earned = 0; // keep track of number of points

    //These are used in moving us around later
    this.old_state = {pos:{x:0,y:0}};
    this.cur_state = {pos:{x:0,y:0}};

    //The world bounds we are confined to
    this.pos_limits = {
	    x_min: this.size.hx,
	    x_max: this.game.world.width - this.size.hx,
	    y_min: this.size.hy,
	    y_max: this.game.world.height - this.size.hy
    };

    this.pos = get_random_position(this.game.world);
    this.angle = get_random_angle();
    this.speed = 5;
    this.color = 'white';
}; 

// The target is the payoff-bearing goal. We construct it with these properties
var target = function(location) {
    this.payoff = 1;
    this.location = location;
    this.visited = false;
    this.radius = 10;
    this.outer_radius = this.radius + 35;
    this.color = 'white';
};

// server side we set the 'game_core' class to a global type, so that
// it can use it in other files (specifically, game.server.js)
if('undefined' != typeof global) {
    module.exports = global.game_core = game_core;
}

get_random_position = function(world) {
    return {
        x: Math.floor((Math.random() * world.width) + 1),
        y: Math.floor((Math.random() * world.height) + 1)
    };
};

get_random_angle = function() {
    return Math.floor((Math.random() * 360) + 1);
};

// Method to easily look up player 
game_core.prototype.get_player = function(id) {
    var result = $.grep(this.players, function(e){ return e.id == id; });
    return result[0].player
};

// Method to get whole list of players
game_core.prototype.get_others = function(id) {
    return _.map($.grep(this.players, function(e){return e.id != id}), 
        function(p){return p.player})
};

// Method to get whole list of players
game_core.prototype.get_all_players = function() {
    return _.map(this.players, function(p){return p.player})
};

// Notifies clients of changes on the server side. Server totally
// handles position and points.
game_core.prototype.server_send_update = function(){
    //Make a snapshot of the current state, for updating the clients
    this.laststate = {
        tcc : this.targets.top.color,                //'top target color'
        bcc : this.targets.bottom.color,             //'bottom target color'
        tcp : this.targets.top.payoff,               //'top target payoff'
        bcp : this.targets.bottom.payoff,            //'bottom target payoff'
        cond: this.condition,                        //dynamic or ballistic?
        de  : this.draw_enabled,                    // true to see angle
        g2w : this.good2write,                      // true when game's started
    };
    var players = this.get_all_players()
//    console.log(players)
    // Add info about all players
    _.extend(this.laststate, {pos: _.map(players, function(p){return p.pos})})
    _.extend(this.laststate, {poi: _.map(players, function(p){return p.points_earned})})
    _.extend(this.laststate, {angle: _.map(players, function(p){return p.angle})})
    _.extend(this.laststate, {speed: _.map(players, function(p){return p.speed})})

    var local_laststate = this.laststate;
    //Send the snapshot to the players
    _.map(this.get_all_players(), function(p){p.instance.emit( 'onserverupdate', local_laststate)})
};

// This is called every 666ms and simulates the world state. This is
// where we update positions and check whether targets have been reached.
game_core.prototype.server_update_physics = function() {
    var local_this = this;
    _.map(this.get_all_players(), function(p){
        // If a player has reached their destination, stop. Have to put
        // other wrapper because destination is null until player clicks
        // Must use distance from, since the player's position is at the
        // center of the body, which is long. As long as any part of the
        // body is where it should be, we want them to stop.
        // if (p.destination) {
        //     if (this.distance_between(p.pos,p.destination) < 8)
        //         p.speed = 0;
        // }

        // Impose Gaussian noise on movement to create uncertainty
        // Recall base speed is 10, so to avoid moving backward, need that to be rare.
        // Set the standard deviation of the noise distribution.
        // if (this.noise) {
        //     var noise_sd = 4;
        //     var nd = new NormalDistribution(noise_sd,0); 
        //     // If a player isn't moving, no noise. Otherwise they'll wiggle in place.
        //     // Use !good2write as a proxy for the 'waiting room' state
        //     if (p.speed == 0 || !this.good2write) 
        //         p.noise = 0;
        //     else
        //         p.noise = nd.sample();
        // } else {
        //     p.noise = 0;
        // }

        //Handle player one movement (calculate using polar coordinates)
        r1 = p.speed; //+ p.noise;
        theta1 = (p.angle - 90) * Math.PI / 180;
        p.old_state.pos = local_this.pos(p.pos) ;
        var new_dir = {
            x : r1 * Math.cos(theta1), 
            y : r1 * Math.sin(theta1)
        };  
        p.pos = p.game.v_add( p.old_state.pos, new_dir );
        p.game.check_collision( p );
    })
};

// Every second, we print out a bunch of information to a file in a
// "data" directory. We keep EVERYTHING so that we
// can analyze the data to an arbitrary precision later on.
game_core.prototype.writeData = function() {
    // Some funny business going on with angles being negative, so we correct for that
    var host_angle_to_write = this.players.self.angle;
    var other_angle_to_write = this.players.other.angle;
    var file_path ;
    if (this.players.self.angle < 0)
        host_angle_to_write = parseInt(this.players.self.angle, 10) + 360;
    if (this.players.other.angle < 0)
        other_angle_to_write = parseInt(this.players.other.angle, 10)  + 360;
    if (this.condition == "ballistic") 
        file_path = "data/ballistic/game_" + this.game_id + ".csv";
    else if (this.condition == "dynamic") 
        file_path = "data/dynamic/game_" + this.game_id + ".csv";
    
    // Write data for the host player
    var host_data_line = String(this.game_number) + ',';
    host_data_line += String(this.game_clock) + ',';
    host_data_line += this.best_target_string + ',';
    host_data_line += "host,";
    host_data_line += this.players.self.visible + ',';
    host_data_line += this.players.self.pos.x + ',';
    host_data_line += this.players.self.pos.y + ',';
    host_data_line += host_angle_to_write + ',';
    host_data_line += this.players.self.points_earned + ',';
    host_data_line += this.players.self.noise.fixed(2) + ',';
    this.fs.appendFile(file_path, 
                       String(host_data_line) + "\n",
                       function (err) {
                           if(err) throw err;
                       });
    console.log("Wrote: " + host_data_line);

    // Write data for the other player
    var other_data_line = String(this.game_number) + ',';
    other_data_line += String(this.game_clock) + ',';
    other_data_line += this.best_target_string + ',';
    other_data_line += "other,";
    other_data_line += this.players.other.visible + ',';
    other_data_line += this.players.other.pos.x + ',';
    other_data_line += this.players.other.pos.y + ',';
    other_data_line += other_angle_to_write + ',';
    other_data_line += this.players.other.points_earned + ',';
    other_data_line += this.players.other.noise.fixed(2) + ',';
    this.fs.appendFile(file_path,
                       String(other_data_line) + "\n",
                       function (err) {
                           if(err) throw err;
                       });
    console.log("Wrote: " + other_data_line);
};

// This also gets called at the beginning of every new game.
// It randomizes payoffs, resets colors, and makes the targets "fresh and
// available" again.
game_core.prototype.server_reset_targets = function() {

    top_target = this.targets.top;
    bottom_target = this.targets.bottom;
    top_target.color = bottom_target.color = 'white';
    top_target.visited = bottom_target.visited = false;

    // Randomly reset payoffs
    var r = Math.floor(Math.random() * 2);

    if (r == 0) {
        this.targets.top.payoff = this.little_payoff;
        this.targets.bottom.payoff = this.big_payoff;
        this.best_target_string = 'bottom';
    } else {
        this.targets.top.payoff = this.big_payoff;
        this.targets.bottom.payoff = this.little_payoff;
        this.best_target_string = 'top';
    }
}; 


// This is a really important function -- it gets called when a round
// has been completed, and updates the database with how much money
// people have made so far. This way, if somebody gets disconnected or
// something, we'll still know what to pay them.
game_core.prototype.server_newgame = function() {
    if (this.use_db) { // set in game.server.js
	    console.log("USING DB");
        var sql1 = 'UPDATE game_participant SET bonus_pay = ' + 
            (this.players.self.points_earned / 100).toFixed(2); 
        sql1 += ' WHERE workerId = "' + this.players.self.instance.userid + '"';
        this.mysql_conn.query(sql1, function(err, rows, fields) {
            if (err) throw err;
            console.log('Updated sql with command: ', sql1);
        });
        var sql2 = 'UPDATE game_participant SET bonus_pay = ' + 
            (this.players.other.points_earned / 100).toFixed(2); 
        sql2 += ' WHERE workerId = "' + this.players.other.instance.userid + '"';
        this.mysql_conn.query(sql2, function(err, rows, fields) {
            if (err) throw err;
            console.log('Updated sql with command: ', sql2);
        });
    }
    
    // Update number of games remaining
    this.games_remaining -= 1;

    // Don't want players moving during countdown
    this.players.self.speed = 0;
    this.players.other.speed = 0;

    // Tell the server about targets being enabled, so it can use it as a flag elsewhere
    this.players.self.targets_enabled = true;
    this.players.other.targets_enabled = true;

    // Don't want to write to file during countdown -- too confusing
    this.good2write = false;

    // Reset destinations
    this.players.self.destination = null;
    this.players.other.destination = null;

    // Don't want people signalling until after countdown/validated input
    this.draw_enabled = false;

    //Reset positions
    this.server_reset_positions();

    //Reset targets
    this.server_reset_targets();

    //Tell clients about it so they can call their newgame procedure (which does countdown)
    this.instance.player_client.send('s.n.');
    this.instance.player_host.send('s.n.');
   
    var local_this = this;

    // For the dynamic version, we want there to be a countdown.
    // For the ballistic version, the game won't start until both players have
    // made valid choices so the function must be checked over and over. It's in
    // server_update_physics.
    if(this.condition == "dynamic"){
        // After countdown, players start moving, we start writing data, and clock resets
        setTimeout(function(){
            local_this.good2write = true;
            local_this.draw_enabled = true;
            console.log("GOOOOOO!");
            local_this.players.self.speed = local_this.global_speed;
            local_this.players.other.speed = local_this.global_speed;
            local_this.game_clock = 0;
        }, 3000);
    } 
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

    var player_host = this.players.self.host ? this.players.self : this.players.other;
    var player_client = this.players.self.host ? this.players.other : this.players.self;

    player_host.pos = this.right_player_start_pos;
    player_client.pos = this.left_player_start_pos;

    player_host.angle = this.right_player_start_angle;
    player_client.angle = this.left_player_start_angle;

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
        this.update_physics();
        this.game_clock += 1;
        if (this.good2write) {
            this.writeData();
        }
    }.bind(this), this.tick_frequency);
};

game_core.prototype.update_physics = function() {
    if(this.server) 
	this.server_update_physics();
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

// Just in case we want to draw from Gaussian to get noise on movement...
function NormalDistribution(sigma, mu) {
    return new Object({
        sigma: sigma,
        mu: mu,
        sample: function() {
            var res;
            if (this.storedDeviate) {
                res = this.storedDeviate * this.sigma + this.mu;
                this.storedDeviate = null;
            } else {
                var dist = Math.sqrt(-1 * Math.log(Math.random()));
                var angle = 2 * Math.PI * Math.random();
                this.storedDeviate = dist*Math.cos(angle);
                res = dist*Math.sin(angle) * this.sigma + this.mu;
            }
            return res;
        },
        sampleInt : function() {
            return Math.round(this.sample());
        }
    });
}

/* Helper functions for the game code:
   Here we have some common maths and game related code to make
   working with 2d vectors easy, as well as some helpers for
   rounding numbers to fixed point.
*/

// (4.22208334636).fixed(n) will return fixed point value to n places, default n = 3
Number.prototype.fixed = function(n) { n = n || 3; return parseFloat(this.toFixed(n)); };

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

//The remaining code runs the update animations

//The main update loop runs on requestAnimationFrame,
//Which falls back to a setTimeout loop on the server
//Code below is from Three.js, and sourced from links below

//http://paulirish.com/2011/requestanimationframe-for-smart-animating/
//http://my.opera.com/emoller/blog/2011/12/20/requestanimationframe-for-smart-er-animating

//requestAnimationFrame polyfill by Erik Möller
//fixes from Paul Irish and Tino Zijdel
var frame_time = 60/1000; // run the local game at 16ms/ 60hz
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
