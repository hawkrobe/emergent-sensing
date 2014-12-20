/*  Copyright (c) 2012 Sven "FuzzYspo0N" Bergström, 2013 Robert XD Hawkins
    
    written by : http://underscorediscovery.com
    written for : http://buildnewgames.com/real-time-multiplayer/
    
    modified for collective behavior experiments on Amazon Mechanical Turk

    MIT Licensed.
*/

    var
        use_db      = false,
        game_server = module.exports = { games : {}, game_count:0 },
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

    //Extract important variables
    var change_target = client.game.gamecore.get_player(client.userid);
    var others = client.game.gamecore.get_others(client.userid);
    if(message_type == 'a') {    // Client is changing angle
        // Set their (server) angle 
        change_target.angle = message_parts[1];
        console.log("new angle =", change_target.angle)
        // Notify other clients of angle change
        if(others) {
            _.map(others, function(p) {p.instance.send('s.a.' + client.userid + '.' + message_parts[1])});
        }
    } else if (message_type == 's') {
        change_target.speed = message_parts[1];
    } else if (message_type == "h") { // Receive message when browser focus shifts
        change_target.visible = message_parts[1];
    }
    
    // Any other ways you want players to interact with the game can be added
    // here as "else if" statements.
};

/* 
   The following functions should not need to be modified for most purposes
*/

// Will run when first player connects
game_server.createGame = function(player) {
    var id = UUID();

    //Create a new game instance
    this.game = {
        id : id,           //generate a new id for the game
        player_instances: [{id: player.userid, player: player}],     //store list of players in the game
        player_count: 1             //for simple checking of state
    };

    //Create a new game core instance (defined in game.core.js)
    this.game.gamecore = new game_core(this.game);

    // Tell the game about its own id
    this.game.gamecore.game_id = id;

    // Set up the filesystem variable we'll use to write later
    this.game.gamecore.fs = fs;

    // When workers are directed to the page, they specify which
    // version of the task they're running. 
    this.game.gamecore.condition = player.condition;

    // tell the player that they have joined a game
    // The client will parse this message in the "client_onMessage" function
    // in game.client.js, which redirects to other functions based on the command
    player.game = this.game;
    player.send('s.j.' + this.game.gamecore.players.length)
    this.log('player ' + player.userid + ' created a game with id ' + player.game.id);

    //Start updating the game loop on the server
    this.game.gamecore.update();

    //return it
    return this.game;
}; 

// we are requesting to kill a game in progress.
// This gets called if someone disconnects
game_server.endGame = function(gameid, userid) {
    var thegame = this.game;
    if(thegame) {
        //stop the game updates immediately
        thegame.gamecore.stop_update();

        //if the game has two players, then one is leaving
        if(thegame.player_count > 1) {
            _.map(thegame.gamecore.get_others(userid), function(p) {p.instance.send('s.e')})
        }
        delete this.game;
        this.game_count--;
        this.log('game removed. there are now ' + this.game_count + ' games' );
    } else {
        this.log('that game was not found!');
    }    
}; 

// When second person joins the game, this gets called
game_server.startGame = function(game) {
    
    // Tell host so that their title will flash if not visible
    game.player_host.send('s.b');

    //s=server message, j=you are joining, send player the host id
    game.player_client.send('s.j.' + game.player_host.userid);
    game.player_client.game = game;
    
    //now we tell the server that the game is ready to start
    game.gamecore.server_newgame();    

    //set this flag, so that the update loop can run it.
    game.active = true;

};

// This is the important function that pairs people up into 'rooms'
// all independent of one another.
game_server.findGame = function(player) {
    this.log('looking for a game. We have : ' + this.game_count);
    //if there are any games created, add this player to it!
    if(this.game) {
        var gamecore = this.game.gamecore;
        // player instances are array of actual client handles
        this.game.player_instances.push({
            id: player.userid, 
            player: player
        });
        this.game.player_count++;
        // players are array of player objects
        this.game.gamecore.players.push({
            id: player.userid, 
            player: new game_player(gamecore,player)
        });
        // Attach game to player so server can look at it later
        player.game = this.game;
        console.log("player collection is now: " + this.game.gamecore.players)
        player.send('s.j.' + this.game.gamecore.players.length)
        _.map(gamecore.get_others(player.userid), function(p){p.instance.send( 's.n.' + player.userid)})
        this.game.gamecore.server_send_update();

        // start the server update loop
        gamecore.update();
    } else { 
        //no games? create one!
        this.createGame(player);
    }
}; 

//A simple wrapper for logging so we can toggle it,
//and augment it for clarity.
game_server.log = function() {
    console.log.apply(this,arguments);
};
