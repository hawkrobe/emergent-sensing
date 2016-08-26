
var babyparse = require("babyparse");
var fs = require("fs");

// https://en.wikipedia.org/wiki/Marsaglia_polar_method
var sampleGaussian = function(mean,std) {
  if(this.extra == undefined){
    var u,v;var s = 0;
    while(s >= 1 || s == 0){
      u = Math.random()*2 - 1; v = Math.random()*2 - 1;
      s = u*u + v*v;
    }
    var n = Math.sqrt(-2 * Math.log(s)/s);
    this.extra = v * n;
    return mean + u * n * std;
  } else{
    var r = mean + this.extra * std;
    this.extra = undefined;
    return r;
  }
};

module.exports = {
  readCSV : function(filename){
    return babyparse
      .parse(fs.readFileSync(filename, 'utf8'),
	     {header : true})
      .data;
  },

  sampleGaussianJitter : function(sd) {
    return {
      x : sampleGaussian(0, sd),
      y : sampleGaussian(0, sd)
    };	    
  },
  
  UUID: function() {
    var name = (Math.floor(Math.random() * 10) +
		'' + Math.floor(Math.random() * 10) +
		'' + Math.floor(Math.random() * 10) +
		'' + Math.floor(Math.random() * 10));
    var id = (name + '-' + 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx')
	  .replace(/[xy]/g, function(c) {
	    var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
	    return v.toString(16);
	  });
    return id;
  },

  
  /**
   * Randomize array element order in-place.
   * Using Durstenfeld shuffle algorithm.
   */
  shuffle : function(array) {
    for (var i = array.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = array[i];
      array[i] = array[j];
      array[j] = temp;
    }
    return array;
  }
};
