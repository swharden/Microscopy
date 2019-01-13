<html>
<head>

<style>
body{font-family: Verdana, sans-serif;}
.lnk{color: blue; text-decoration: underline;}
table{font-size: 12px;}


</style>

<script language="JavaScript" type="text/javascript"> 
<!-- 

function tb(obj,mess){ 
 document.getElementById(obj).value=mess; 
} 

//--> 
</script> 

</head>
<body>
<div align="center">

<h1>SacTrack</h1>

<form action="submit.php" method="post">
<table>
	<tr>
		<td align="right">You are:</td>
		<td><input type="text" name="name" value="<?php echo($_GET["name"]);?>" readonly></td>
	</tr>
	<tr>
		<td align="right">You sacked:</td>
		<td><input type="text" name="animal"></td>
	</tr>
	<tr>
		<td align="right">Strain:</td>
		<td><input type="text" id="strain" name="strain"></td>
	</tr>
	<tr>
		<td colspan="2" align="right">
		<span class="lnk" onclick="javascript:tb('strain','AT2 reporter');">AT2</span> | 
		<span class="lnk" onclick="javascript:tb('strain','CRH reporter');">CRH</span> | 
		<span class="lnk" onclick="javascript:tb('strain','MC4 reporter');">MC4</span>
		</td>
	</tr>
	<tr>
		<td align="right">Report to:</td>
		<!-- hhiller@ufl.edu -->
		<td><input type="text" name="email" value="hhiller@ufl.edu" readonly></td>
	</tr>
	<tr>
		<td align="right">Date:</td>
		<td><input type="text" name="when" value="<?php echo(date("Y-m-d H:i:s"));?>" readonly></td>
	</tr>
	<tr>
		<td colspan="2" align="center"><input type="submit" value="LOG THIS SAC"></td>
	</tr>
</table>
</form>
</div>

</body>
</html>