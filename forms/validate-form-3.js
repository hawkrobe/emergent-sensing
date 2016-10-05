function validateForm() {
    
    var count = 0
    var qs = Array('others', 'loc', 'comp', 'diff', 'goal', 'goal2');
    var as = Array(qs.length);
    for (i = 0; i < qs.length; i++) { 
	as[i] = document.forms["quiz"][qs[i]].value;
	if(as[i] != "yes" && as[i] != "no") {
	    alert("Please enter responses to all questions to continue.");
	    return false
	}
    }
}
