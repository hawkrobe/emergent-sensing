    <?php

ob_start();	

    // define variables and set to empty values
    $others = $loc = $comp = $diff = $goal2 = $goal = "";
    
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $others = $_POST["others"];
    	$loc = $_POST["loc"];
	$comp = $_POST["comp"];
	$diff = $_POST["diff"];
	$goal2 = $_POST["goal2"];
	$goal = $_POST["goal"];
    }

    if(($others != "yes" && $others != "no") ||  ($loc != "yes" && $loc != "no") ||  ($comp != "yes" && $comp != "no") ||  ($diff != "yes" && $diff != "no") || ($goal2 != "yes" && $goal2 != "no") ||  ($goal != "yes" && $goal != "no")){
    		   echo '<meta http-equiv="refresh" content="0;url=http://projects.csail.mit.edu/ci/turk/forms/fail.html">';
      } else {
            if ($others == "no" || $loc == "no" || $comp == "no" || $diff  == "no" || $goal2 == "no" || $goal == "no") {
      	    	 echo '<meta http-equiv="refresh" content="0;url=http://projects.csail.mit.edu/ci/turk/forms/fail.html">';
	    } else {
	      	   echo '<meta http-equiv="refresh" content="0;url=http://projects.csail.mit.edu/ci/turk/forms/pass-2.html?port='.$_GET["port"].'">';
	}
      }
    ?>
