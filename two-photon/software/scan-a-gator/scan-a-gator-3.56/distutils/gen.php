<html>
<head>
<meta name="viewport" content="width=device-width">
</head>
<body>
<div align="center">
<span style="font-size:36px;"><b>Reg-A-Gator&trade;</b></span>
<br><br><br>
<code>


<?php 
/*
function keygenOld($name,$pcid){
	$name = str_replace(' ', '', $name);
	$name=strtoupper($name);
	$pcid=intval($pcid);
	$s=0;
	$chars = str_split($name);
	foreach($chars as $char){$s=$s+pow(ord($char)-64,2);}
	$s=pow($s*$pcid,2);
	$s=strval($s);
	while (strlen($s)%4) {$s=$s."0";}
	$s=str_split($s,4);
	$key="";
	foreach($s as $chunk){$key=$key."-".$chunk;}
	$key=substr($key,1,strlen($key));
	return $key;
}*/
function keygenRaw($s,$h){ #use h as a seed
	$numbers=4; // length of key
	$chars = str_split($s);
	foreach($chars as $char){
		$h=($h<<5)+$h+pow(ord($char),2);
		$h=$h%pow(10,$numbers);
	}
	while ($h<pow(10,($numbers-1))){
		$h=($h<<1)+$h;
	}
	$h=$h%pow(10,$numbers);
	return $h;
}

function keygen($name,$pcid,$ver){
	$ver=intval($ver);
	$s=$pcid.$name;
	$s=strtoupper($s);
	$s=str_replace(' ', '', $s);
	$s=str_replace('-', '', $s);
	$s=str_replace('.', '', $s);
	
	$key="";
	$key=$key.sprintf("%04d", keygenRaw($s,11+$ver)).'-';
	$key=$key.sprintf("%04d", keygenRaw($s,13+$ver)).'-';
	$key=$key.sprintf("%04d", keygenRaw($s,15+$ver));
	return $key;
}

?>

REGISTRATION: SUCCESSFUL<br><br>
Registrant: <?php echo($_POST["name"]);?><br>
PC-ID: <?php echo($_POST["pcid"]);?><br>
Version: <?php echo($_POST["version"]);?><br>
<br><br>
YOUR REGISTRATION KEY IS:<br>
<b><?php echo(keygen($_POST["name"],$_POST["pcid"],$_POST["version"]));?></b><br>

</code>
</div>
</body>
</html>