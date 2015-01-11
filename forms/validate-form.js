function validateForm() {
    var completed = document.forms["quiz"]["completed"].value;
    var dir = document.forms["quiz"]["dir"].value;
    var speed = document.forms["quiz"]["speed"].value;
    var none = document.forms["quiz"]["none"].value;
    var loc = document.forms["quiz"]["loc"].value;
    var comp = document.forms["quiz"]["comp"].value;
    var diff = document.forms["quiz"]["diff"].value;
    var goal = document.forms["quiz"]["goal"].value;
    
    if ((completed != "yes" && completed != "no") ||  (dir != "yes" && dir != "no") ||  (speed != "yes" && speed != "no") ||  (none != "yes" && none != "no") ||  (loc != "yes" && loc != "no") ||  (goal != "yes" && goal != "no") || (comp != "yes" && comp != "no") || (diff != "yes" && diff != "no")){
	alert("Please enter responses to all questions to continue.");
	return false
    }
    if (completed == "yes") {
        window.location = "./notwice.html";
    } else {
	if (dir == "no" || speed == "no" || none == "no" || loc  == "no" || goal == "no" || diff == "no" || goal == "no") {
            window.location = "./fail.html";
	} else {
            window.location = "./pass.html";
	}
    }
    return false
}
