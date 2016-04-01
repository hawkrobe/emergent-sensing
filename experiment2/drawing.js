// Draw players as triangles using HTML5 canvas
function draw_player(game, player){
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

  // Draw message in center (for countdown, e.g.)
  game.ctx.font = "bold 12pt Helvetica";
  game.ctx.fillStyle = 'red';
  game.ctx.textAlign = 'center';
  game.ctx.fillText(player.message, game.world.width/2, game.world.height/5);
}; 

function draw_label(game, player, label) {
  game.ctx.font = "8pt Helvetica";
  game.ctx.fillStyle = 'white';
  game.ctx.fillText(label, player.pos.x+10, player.pos.y + 20); 
}

function draw_visibility_radius(game, player) {
  var x = player.pos.x;
  var y = player.pos.y;
  var r = game.visibility_radius;
  game.ctx.beginPath();
  game.ctx.strokeStyle = 'gray';
  game.ctx.arc(x, y, r, 0, 2 * Math.PI, false);
  game.ctx.stroke();
}

function draw_other_dot(game, player, other) {
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

function draw_destination(game, player) {
  game.ctx.strokeStyle = player.color;
  game.ctx.beginPath();
  game.ctx.moveTo(player.destination.x - 5, player.destination.y - 5);
  game.ctx.lineTo(player.destination.x + 5, player.destination.y + 5);

  game.ctx.moveTo(player.destination.x + 5, player.destination.y - 5);
  game.ctx.lineTo(player.destination.x - 5, player.destination.y + 5);
  game.ctx.stroke();
};

// draws instructions at the bottom in a nice style
function draw_info(game, info) {    
  //Draw information shared by both players
  game.ctx.font = "8pt Helvetica";
  game.ctx.fillStyle = 'rgba(255,255,255,1)';
  game.ctx.fillText(info, 10 , 465); 
  
  //Reset the style back to full white.
  game.ctx.fillStyle = 'rgba(255,255,255,1)';
}; 
