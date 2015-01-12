// Draw players as triangles using HTML5 canvas
draw_player = function(game, p_obj){
    var player_id = p_obj.id;
    var player = p_obj.player;

    // Draw avatar as triangle
    var v = [[0,-player.size.x],
	     [-player.size.hx,player.size.y],
	     [player.size.hy,player.size.x]];
    game.ctx.save();
    game.ctx.translate(player.pos.x, player.pos.y);
    game.ctx.rotate((player.angle * Math.PI) / 180);

    // This draws the triangle
    game.ctx.fillStyle = player.color;
    game.ctx.strokeStyle = player.color;
    game.ctx.beginPath();
    game.ctx.moveTo(v[0][0],v[0][1]);
    game.ctx.lineTo(v[1][0],v[1][1]);
    game.ctx.lineTo(v[2][0],v[2][1]);
    game.ctx.closePath();
    game.ctx.stroke();
    game.ctx.fill();

    game.ctx.beginPath();
    game.ctx.restore();

    // draw floating label
    //    game.ctx.fillStyle = player.info_color;
    game.ctx.font = "8pt Helvetica";
    if (player_id)
	game.ctx.fillText("Player " + player_id.slice(0,4), player.pos.x+10, player.pos.y + 20); 


    // Draw message in center (for countdown, e.g.)
    game.ctx.font = "10pt Helvetica";
    game.ctx.fillStyle = 'white';
    game.ctx.textAlign = 'center';
    game.ctx.fillText(player.message, game.world.width/2, game.world.height/2);
}; 

draw_visibility_radius = function(game, player) {
    var x = player.pos.x
    var y = player.pos.y
    var r = game.visibility_radius
    game.ctx.beginPath();
    game.ctx.strokeStyle = 'gray';
    game.ctx.arc(x, y, r, 0, 2 * Math.PI, false);
    game.ctx.stroke();
}

draw_other_dot = function(game, player, other) {
    var scaling_factor = game.distance_between(player.pos, other.pos);
    var X = (other.pos.x - player.pos.x);
    var Y = (player.pos.y - other.pos.y);
    var theta = Math.atan2(Y,X);
    game.ctx.beginPath();
    game.ctx.arc(player.pos.x + game.visibility_radius*Math.cos(theta),
		 player.pos.y - game.visibility_radius*Math.sin(theta), 
		 5, 0, 2 * Math.PI, false);
    game.ctx.fillStyle = 'white';
    game.ctx.fill();
    game.ctx.lineWidth = 1;
    game.ctx.strokeStyle = 'gray';
    game.ctx.stroke();
};

// draws instructions at the bottom in a nice style
draw_info = function(game, info) {    
    //Draw information shared by both players
    game.ctx.font = "8pt Helvetica";
    game.ctx.fillStyle = 'rgba(255,255,255,1)';
    game.ctx.fillText(info, 10 , 465); 
    
    //Reset the style back to full white.
    game.ctx.fillStyle = 'rgba(255,255,255,1)';
}; 
