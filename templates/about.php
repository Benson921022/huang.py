<!DOCTYPE html>
<html lang="zh-TW">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>黃柏彰</title>
	<style type="text/css">
		*{font-family: "標楷體";margin-left:auto;margin-right: auto;}
		h1{color:pink;font-size: 60px;}
		h2{color:#33ff33;font-size: 40px;}
	</style>

	<script>
		function change1() {
  			document.getElementById("pic").src = "小花線條小狗.jpg";
  			document.getElementById("h2text").innerText = "靜宜資管";
		}

		function change2() {
  			document.getElementById("pic").src = "下載.jpg";
  			document.getElementById("h2text").innerText = "BO-ZHANG, HUANG";
		}
	</script>


</head>

<body>

	<table width="70%">
		<tr>
			<td>
				<img src="下載.jpg" width="70%" id="pic" onmouseover="change1()" onmouseout="change2()"></img>
			</td>

			<td>
				<h1>黃柏彰</h1>
				<h1><?php echo date("Y-m-d") ?></h1>
				<h2 id="h2text">BO-ZHANG, HUANG</h2>
			</td>
		</tr>
	</table>



	<table width="70%"border="1">
        <tr>
        	<td>
				個人網頁:<a href="https://www.pu.edu.tw/">靜宜大學https://www.pu.edu.tw/</a><br>
				IG:<a href="https://www.instagram.com/tsai_ingwen/?hl=zh-tw" 	target="_blank">tsai_ingwen</a><br>
				TEL:<a href="tel:0910317501">0910317501</a><br>
				E-Mail:<a href="benson921022@gmail.com">benson921022@gmail.com</a><br>
			</td>
		</tr>

		<tr>
        	<td>
				大象席地而坐電影配樂<br>
				<audio controls>
				<source src="elephant.mp3"type="audio/mp3">
				</audio><br>
			</td>
		</tr>

		<tr>
        	<td>
				不要去台灣<br>
				<iframe src="https://www.youtube.com/embed/pW88QFpHXa8"allowfullsctream></iframe>

			</td>
		</tr>

		<tr>
        	<td>
				<iframe
    	allow="microphone;"
    	width="350"
    	height="430"
    	src="https://console.dialogflow.com/api-client/demo/embedded/5267bc98-d21d-48dc-8d45-46ede9db1599">
</iframe>
			</td>
		</tr>


	</table>	


</body>
</html>