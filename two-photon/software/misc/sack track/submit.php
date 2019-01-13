<html>
<body>
<div align="center">
<h2>SacTrack</h2>

<?php if ($_POST["name"]==""): ?>
<h3 style="color:red;">ERROR: no name given</h3>

<?php elseif ($_POST["animal"]==""): ?>
<h3 style="color:red;">ERROR: no animal given</h3>

<?php else: ?>

<h3 style="color:green;">Added sac of <?php echo $_POST["animal"] . "/" . $_POST["strain"]; ?> to the log.</h3>
<h3 style="color:green;">Email sent to <?php echo $_POST["email"]; ?>.</h3>


<?php
$myFile = "log.txt";
$fh = fopen($myFile, 'a');
$stringData = "<li> " . $_POST["when"] . " - " . $_POST["animal"] . "/" . $_POST["strain"] . " sacked by " . $_POST["name"] . "\n";
$emailData = $_POST["animal"] . "/" . $_POST["strain"] . " sacked by " . $_POST["name"] . " on " . $_POST["when"];
fwrite($fh, $stringData);
fclose($fh);
?>

<?php
$to = $_POST["email"];
$subject = "sacked ".$_POST["animal"]." by ".$_POST["name"];
$message = $emailData . "\n" . "LINK: http://www.WEBSITE.com/lab/sac/";
$from = "WEBSITE@gmail.com";
$headers = "From:" . $from;
mail($to,$subject,$message,$headers);
?>

<?php
$to = "WEBSITE@gmail.com";
$subject = "sacked ".$_POST["animal"]." by ".$_POST["name"];
$message = $emailData . "\n" . "LINK: http://www.WEBSITE.com/lab/sac/";
$from = "WEBSITE@gmail.com";
$headers = "From:" . $from;
mail($to,$subject,$message,$headers);
?>

</div>
<div align="left">
<ul>
<?php include("log.txt");?>
</ul>

<?php endif ?>
</div>

</body>
</html>