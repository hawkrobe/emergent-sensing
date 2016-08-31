
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
    game.ctx.fillStyle = 'yellow';
    game.ctx.textAlign = 'center';
    game.ctx.fillText(player.message, game.world.width/2, game.world.height/5);
    game.ctx.fillStyle = 'red';
    game.ctx.fillText(player.warning, game.world.width/2, game.world.height/2 - 20);
    //game.ctx.fillText(player.warning2, game.world.width/2, game.world.height/2);
    //game.ctx.fillText(player.warning3, game.world.width/2, game.world.height/2 + 20);
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
  game.ctx.globalAlpha = game.remainingFadeSteps/game.numFadeSteps;
  game.ctx.strokeStyle = player.color;
  game.ctx.beginPath();
  game.ctx.moveTo(xCoord - 5, yCoord- 5);
  game.ctx.lineTo(xCoord + 5, yCoord + 5);

  game.ctx.moveTo(xCoord + 5, yCoord - 5);
  game.ctx.lineTo(xCoord - 5, yCoord + 5);
  game.ctx.stroke();
  game.ctx.restore();
  if(game.remainingFadeSteps > 0) { // stop if done
    game.remainingFadeSteps--;
  }
};


// Make sparkles (https://codepen.io/jackrugile/pen/Gving)
/* super inefficient right now, could be improved */

var rand = function(a,b){return ~~((Math.random()*(b-a+1))+a);};
var dToR = function(degrees){
  return degrees * (Math.PI / 180);
};
var particleMax = 100;

function drawSparkles(game, player) {
  if(!game.circle) {
    game.particles = [];
    game.circle = {
      x: player.pos.x,
      y: player.pos.y,
      radius: player.size.x * 3,
      speed: 5,
      rotation: 0,
      angleStart: 270,
      angleEnd: 90,
      hue: 60,
      thickness: 5,
      blur: 25
    };    
  }
  game.circle.x = player.pos.x;
  game.circle.y = player.pos.y;

  var ctx = game.ctx;
  ctx.save();
  var updateCircle = function(){
    //console.log("updating circle...");
    //console.log(game.circle.rotation);
    if(game.circle.rotation < 360){
      game.circle.rotation += game.circle.speed;
    } else {
      game.circle.rotation = (game.circle.rotation + game.circle.speed) % 360;
    }
  };
  var renderCircle = function(){
    ctx.save();
    ctx.translate(game.circle.x, game.circle.y);
    ctx.rotate(dToR(game.circle.rotation));
    ctx.beginPath();
    ctx.arc(0, 0, game.circle.radius,
	    dToR(game.circle.angleStart), dToR(game.circle.angleEnd), true);
    ctx.lineWidth = game.circle.thickness;
    ctx.strokeStyle = gradient1;
    ctx.stroke();
    ctx.restore();
  };
  var renderCircleBorder = function(){
    ctx.save();
    ctx.translate(game.circle.x, game.circle.y);
    ctx.rotate(dToR(game.circle.rotation));
    ctx.beginPath();
    ctx.arc(0, 0, game.circle.radius + (game.circle.thickness/2),
	    dToR(game.circle.angleStart), dToR(game.circle.angleEnd), true);
    ctx.lineWidth = 2;
    ctx.strokeStyle = gradient2;
    ctx.stroke();
    ctx.restore();
  };
  var createParticles = function(){
    if(game.particles.length < particleMax){
      game.particles.push({
	x: (game.circle.x + game.circle.radius * Math.cos(dToR(game.circle.rotation-85))) +
	  (rand(0, game.circle.thickness*2) - game.circle.thickness),
	y: (game.circle.y + game.circle.radius * Math.sin(dToR(game.circle.rotation-85))) +
	  (rand(0, game.circle.thickness*2) - game.circle.thickness),
	vx: (rand(0, 100)-50)/1000,
	vy: (rand(0, 100)-50)/1000,
	radius: rand(1, 3)/2,
	alpha: rand(10, 20)/100
      });
    }
  };
  var updateParticles = function(){
    var i = game.particles.length;
    while(i--){
      var p = game.particles[i];
      p.vx += (rand(0, 100)-50)/750;
      p.vy += (rand(0, 100)-50)/750;
      p.x += p.vx;
      p.y += p.vy;
      p.alpha -= .01;

      if(p.alpha < .02){
	game.particles.splice(i, 1)
      }
    }
  };
  var renderParticles = function(){
    var i = game.particles.length;
    while(i--){
      var p = game.particles[i];
      ctx.beginPath();
      ctx.fillRect(p.x, p.y, p.radius, p.radius);
      ctx.closePath();
      ctx.fillStyle = 'hsla(0, 100%, 50%, '+p.alpha+')';
    }
  };

  /* Set Constant Properties */
  ctx.shadowBlur = game.circle.blur;
  ctx.shadowColor = 'hsla('+game.circle.hue+', 80%, 60%, 1)';
  ctx.lineCap = 'round';

  var gradient1 = ctx.createLinearGradient(0, -game.circle.radius, 0, game.circle.radius);
  gradient1.addColorStop(0, 'hsla('+game.circle.hue+', 60%, 50%, .25)');
  gradient1.addColorStop(1, 'hsla('+game.circle.hue+', 60%, 50%, 0)');

  var gradient2 = ctx.createLinearGradient(0, -game.circle.radius, 0, game.circle.radius);
  gradient2.addColorStop(0, 'hsla('+game.circle.hue+', 100%, 50%, 0)');
  gradient2.addColorStop(.1, 'hsla('+game.circle.hue+', 100%, 100%, .7)');
  gradient2.addColorStop(1, 'hsla('+game.circle.hue+', 100%, 50%, 0)');

  updateCircle();
  renderCircle();
  renderCircleBorder();
  createParticles();
  createParticles();
  createParticles();
  updateParticles();
  renderParticles();
  ctx.restore();

  /* Loop It, Loop It Good */
  // game.sparkleIntervalID = setInterval(loop, 16);
};

function endSparkles(game, player) {
  //clearInterval(game.sparkleIntervalID);
};

var addSkipButton = function (game){
  var button = document.createElement("BUTTON");
  var text = document.createTextNode("Disconnect");
  button.appendChild(text); 
  button.addEventListener('click',  function() {
    game.socket.send("quit");
  });
  var instructionDiv = document.getElementById("warnings");
  instructionDiv.appendChild(button);
};

var addStartButton = function (game){
  var button = document.createElement("BUTTON");
  var text = document.createTextNode("Start");
  button.appendChild(text); 
  button.addEventListener('click',  function() {
    game.socket.send("start");
  });
  var instructionDiv = document.getElementById("warnings");
  instructionDiv.appendChild(button);
};
