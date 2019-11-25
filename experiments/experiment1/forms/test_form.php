    <?php

ob_start();	

    // define variables and set to empty values
    $completed = $dir = $speed = $none = $loc = $comp = $diff = $goal = "";
    
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $completed = $_POST["completed"];
    $dir = $_POST["dir"];
    $speed = $_POST["speed"];
    $none = $_POST["none"];
    $loc = $_POST["loc"];
    $comp = $_POST["comp"];
    $diff = $_POST["diff"];
    $goal = $_POST["goal"];
    }

    if(($completed != "yes" && $completed != "no") ||  ($dir != "yes" && $dir != "no") ||  ($speed != "yes" && $speed != "no") ||  ($none != "yes" && $none != "no") || ($loc != "yes" && $loc != "no") ||  ($goal != "yes" && $goal != "no") || ($comp != "yes" && $comp != "no") || ($diff != "yes" && $diff != "no")){
echo '<meta http-equiv="refresh" content="0;url=http://projects.csail.mit.edu/ci/turk/forms/fail.html">';
      } else {
      if ($completed == "yes") {
echo '<meta http-equiv="refresh" content="0;url=http://projects.csail.mit.edu/ci/turk/forms/notwice.html">';
      } else {
      if ($dir == "no" || $speed == "no" || $none == "no" || $loc  == "no" || $goal == "no" || $diff == "no" || $goal == "no" || $comp == "no") {
echo '<meta http-equiv="refresh" content="0;url=http://projects.csail.mit.edu/ci/turk/forms/fail.html">';
      } else {
echo '<meta http-equiv="refresh" content="0;url=http://projects.csail.mit.edu/ci/turk/forms/pass.html">';
      }
      }
      }
    ?>
