/*  Copyright (c) 2012 Sven "FuzzYspo0N" Bergström, 2013 Robert XD Hawkins
    
    written by : http://underscorediscovery.com
    written for : http://buildnewgames.com/real-time-multiplayer/
    
    modified for collective behavior experiments on Amazon Mechanical Turk

    MIT Licensed.
*/

require('look').start()

    var
        use_db      = false,
        game_server = module.exports = { games : {}, game_count:0, 
                                         curr_assignments : [], finished_assignments:[]},
        UUID        = require('node-uuid'),
        fs          = require('fs');
	    
    if (use_db) {
	    database    = require(__dirname + "/database"),
	    connection  = database.getConnection();
    }

global.window = global.document = global;
require('./game.core.js');

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
    if(message_type == 'a') {    // Client is changing angle
        // Set their (server) angle 
        target.angle = message_parts[1];
    } else if (message_type == 's') {
        target.speed = message_parts[1];
    } else if (message_type == "h") { // Receive message when browser focus shifts
        target.visible = message_parts[1];
    } else if (message_type == 'pong') {
	var latency = (Date.now() - message_parts[1])/2;
	client.game.gamecore.latencyStream.write(String(client.userid)+","+client.game.gamecore.round_num+","+message_parts[2]+","+latency+"\n",
			   function(err) { if(err) throw err; });
    }
};

/* 
   The following functions should not need to be modified for most purposes
*/

// This is the important function that pairs people up into 'rooms'
// all independent of one another.
game_server.findGame = function(player) {
    this.log('looking for a game. We have : ' + this.game_count);
    //if there are any games created, add this player to it!
    if(this.game_count) {
       var joined_a_game = false;
        for (var gameid in this.games) {
            if(!this.games.hasOwnProperty(gameid)) continue;
            var game = this.games[gameid];
            var gamecore = game.gamecore;
            if(game.player_count < gamecore.players_threshold) { 
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
                gamecore.server_send_update();
                gamecore.update();

                if (game.player_count == gamecore.players_threshold) {
                    this.startGame(game)
                }
            }
        }
        if(!joined_a_game) { // if we didn't join a game, we must create one
            this.createGame(player);
        }
    }
    else { 
        //no games? create one!
        this.createGame(player);
    }
}; 

// Will run when first player connects
game_server.createGame = function(player) {
    // Figure out variables
    var local_this = this;
    var assignment = _.filter(_.range(8), function(i) {
	    return (!_.contains(local_this.curr_assignments, i)
		    & !_.contains(local_this.finished_assignments, i))})[0]
    this.curr_assignments.push(assignment)
    var game_params = this.param_guide[assignment].split(',')
    var id = parseInt(game_params[0])
    var players_threshold = parseInt(game_params[1])
    var noise_location = game_params[2]
    
    if(id == null)
	id = UUID();

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
    game.gamecore = new game_core(game);

    // Tell the game about its own id
    game.gamecore.game_id = id;
    game.gamecore.players_threshold = players_threshold
    game.gamecore.noise_location = noise_location

    // Set up the filesystem variable we'll use later, and write headers
    game.gamecore.fs = fs;
    fs.writeFile("data/games/game_" +id+ ".csv", "pid, tick, active, x_pos, y_pos, velocity, angle, bg_val, total_points\n", function (err) {if(err) throw err;})
    game.gamecore.gameDataStream = fs.createWriteStream("data/games/game_" +id+ ".csv", {'flags' : 'a'});
    fs.writeFile("data/latencies/game_"+id+".csv", "pid, tick, latency\n", function (err) {if(err) throw err;})
    game.gamecore.latencyStream = fs.createWriteStream("data/latencies/game_"+id+".csv", {'flags' : 'a'});

    // When workers are directed to the page, they specify which
    // version of the task they're running. 
    game.gamecore.condition = player.condition;

    // tell the player that they have joined a game
    // The client will parse this message in the "client_onMessage" function
    // in game.client.js, which redirects to other functions based on the command
    player.game = game;
    player.send('s.join.' + game.gamecore.players.length)
    this.log('player ' + player.userid + ' created a game with id ' + player.game.id);
    this.log('curr_assignments are' + this.curr_assignments);
    //Start updating the game loop on the server
    game.gamecore.update();

    // add to game collection
    this.games[ game.id ] = game;
    this.game_count++;
    if(game.gamecore.players_threshold == 1)
	this.startGame(game)
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
            if (!thegame.active) 
                thegame.player_count--;
        } else {
            // If the game only has one player and they leave, remove it.
            thegame.gamecore.stop_update();
            delete this.games[gameid];
            this.game_count--;
	    // Remove from assignments, so someone else can be assigned to this condition
	    var index = this.curr_assignments.indexOf(gameid);
	    if(index > -1) 
		this.curr_assignments.splice(index, 1);

            this.log('game removed. there are now ' + this.game_count + ' games' );
	    this.log("curr assignments is now " + this.curr_assignments)
        }
    } else {
        this.log('that game was not found!');
    }   
}; 
    
// When the threshold is exceeded, this gets called
game_server.startGame = function(game) {
    game.active = true;
    game.gamecore.server_newgame(); 
};

//A simple wrapper for logging so we can toggle it,
//and augment it for clarity.
game_server.log = function() {
    console.log.apply(this,arguments);
};
