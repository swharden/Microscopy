<html>
<head>
<meta name="viewport" content="width=device-width">
</head>
<body>
<div align="center">
<table width="500"><tr><td>
<span style="font-size:36px;"><b>Reg-A-Gator&trade;</b></span>
<br><br><br>
<form action="gen.php" method="post">

Registrant:<br>
<input type="text" name="name" value="<?php echo($_GET["n"]);?>"><br><br>

PC-ID:<br>
<input type="text" name="pcid" value="<?php echo($_GET["p"]);?>"><br><br>

Version:<br>
<input type="text" name="version" value="3"><br><br>

<input type="submit" value="generate key">
</form>
</td></tr></table>
</div>
</body>
</html>