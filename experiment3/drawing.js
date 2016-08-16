
var GOODCOLOR = getColorForPercentage(1.0);  

var getColorForPercentage = function(pct) {
  if(pct == 0) {
    return 'red';
  } else {
    for (var i = 0; i < percentColors.length; i++) {
      if (pct <= percentColors[i].pct) {
	var lower = (percentColors[i - 1]
		     || { pct: 0.2, color: { r: 0x0, g: 0x00, b: 0 } });
	var upper = percentColors[i];
	var range = upper.pct - lower.pct;
	var rangePct = (pct - lower.pct) / range;
	var pctLower = 1 - rangePct;
	var pctUpper = rangePct;
	var color = {
          r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
          g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
          b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
	};
	return 'rgb(' + [color.r, color.g, color.b].join(',') + ')';
      }
    }
  }
}

// Draw players as triangles using HTML5 canvas
draw_player = function(game, player){
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

draw_label = function(game, player, label) {
    game.ctx.font = "8pt Helvetica";
    game.ctx.fillStyle = 'white';
    game.ctx.fillText(label, player.pos.x+10, player.pos.y + 20); 
}

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

function drawScoreField(game){
  
  var centerX = game.spotScoreLoc.x;
  var centerY = game.spotScoreLoc.y;
  drawSpotlight(game, centerX, centerY);
  
};

function drawSpotlight(game, centerX, centerY) {
  // Draw spotlight
  var radius = 50;
  if(centerX && centerY) {
    game.ctx.save();
    game.ctx.beginPath();
    game.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
    game.ctx.fillStyle = GOODCOLOR;
    game.ctx.fill();
    game.ctx.restore();
  }
}

function drawDestination(game, player) {
  var xCoord = parseFloat(player.destination.x);
  var yCoord = parseFloat(player.destination.y);
  game.ctx.save();
  game.ctx.strokeStyle = player.color;
  game.ctx.beginPath();
  game.ctx.moveTo(xCoord - 5, yCoord- 5);
  game.ctx.lineTo(xCoord + 5, yCoord + 5);

  game.ctx.moveTo(xCoord + 5, yCoord - 5);
  game.ctx.lineTo(xCoord - 5, yCoord + 5);
  game.ctx.stroke();
  game.ctx.restore();
};
