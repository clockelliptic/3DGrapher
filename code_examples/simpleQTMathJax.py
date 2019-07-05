import sys
from PyQt5.QtCore import QFile, QFileInfo, QTextStream, QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView

pageSource = """<!doctype html>
<html>
<head>
<title>Creating mathml from expressions</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
  </script>

<script type="text/javascript">
<!--
function render()
{
  var res = document.getElementById('equation').value;
  var target = document.getElementById('outputDiv');
  target.innerHTML=res;
  MathJax.Hub.Queue(["Typeset",MathJax.Hub,'outputDiv']);
}
// -->
</script>
</head>
<body>
<h1>MathML to MathJax<h1>

<form>
<input type="text" id="equation" size="100" value="<math><msup><mi>x</mi><mn>2</mn>    </msup></math>"/>
<input type="button" value="Render" onClick="render();"/>
</form>

<div id="outputDiv" style="border:1px; font-size:x-large;">

</div>
</body>
</html>"""

app = QApplication(sys.argv)


webView = QWebEngineView()
webView.setHtml(pageSource)
webView.show()

sys.exit(app.exec_())