import sys
from PyQt5.QtCore import QFile, QFileInfo, QTextStream, QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView

pageSource = """<!doctype html>
<html>
<head>
<title>MathJax Dynamic Math Test Page</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
  MathJax.Hub.Config({
    extensions: ["tex2jax.js"],
    jax: ["input/TeX","output/HTML-CSS"],
    tex2jax: {inlineMath: [["$","$"],["\\(","\\)"]]}
  });
</script>

</head>
<body>

<script>
  //
  //  Use a closure to hide the local variables from the
  //  global namespace
  //
  (function () {
    var QUEUE = MathJax.Hub.queue;  // shorthand for the queue
    var math = null;                // the element jax for the math output.

    //
    //  Get the element jax when MathJax has produced it.
    //
    QUEUE.Push(function () {
      math = MathJax.Hub.getAllJax("MathOutput")[0];
    });

    //
    //  The onchange event handler that typesets the
    //  math entered by the user
    //
    window.UpdateMath = function (TeX) {
      QUEUE.Push(["Text",math,"{"+TeX+"}"]);
    }
  })();
</script>

Type some TeX code:
<input id="MathInput" size="50" onchange="UpdateMath(this.value)" />
<p>
"""+"""
<div id="MathOutput">
You typed: ${}$
</div>

</body>
</html>"""

app = QApplication(sys.argv)


webView = QWebEngineView()
webView.setHtml(pageSource)
webView.show()

sys.exit(app.exec_())