// Draw players as triangles using HTML5 canvas
draw_player = function(game, player){
    game.ctx.font = "10pt Helvetica";

    // Draw avatar as triangle
    var v = [[0,-8],[-5,8],[5,8]];
    game.ctx.save();
    game.ctx.translate(player.pos.x, player.pos.y);
    // draw_enabled is set to false during the countdown, so that
    // players can set their destinations but won't turn to face them.
    // As soon as the countdown is over, it's set to true and they
    // immediately start using that new angle
    if (player.game.draw_enabled) {
	    game.ctx.rotate((player.angle * Math.PI) / 180);
    } else {
	    game.ctx.rotate((player.start_angle * Math.PI) / 180);
    }
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

    //Draw tag underneath players
    game.ctx.fillStyle = player.info_color;
    game.ctx.fillText(player.state, player.pos.x+10, player.pos.y + 20); 

    // Draw message in center (for countdown, e.g.)
    game.ctx.fillStyle = 'white';
    game.ctx.fillText(player.message, 290, 240);
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

// draws instructions at the bottom in a nice style
draw_info = function(game, info) {    
    //Draw information shared by both players
    game.ctx.font = "8pt Helvetica";
    game.ctx.fillStyle = 'rgba(255,255,255,1)';
    game.ctx.fillText(info, 10 , 465); 
    
    //Reset the style back to full white.
    game.ctx.fillStyle = 'rgba(255,255,255,1)';
}; 
