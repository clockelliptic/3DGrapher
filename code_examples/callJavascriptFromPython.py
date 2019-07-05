import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


class FormWidget(QWidget):
    ...
    def __controls(self):
        ...
        self.browser = QWebEngineView()
        self.browser.setPage(WebEnginePage(self.browser))

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.form_widget = FormWidget(self)
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.setCentralWidget(_widget)


class FormWidget(QWidget):
    pageSource = """
        <!DOCTYPE html>
        <html>

        <head>
            <meta charset="UTF-8">
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
            function updateMathJax(TeX) {
                /// set up new mathjax div content
                document.getElementById("MathOutput").innerHTML = TeX;
                /// update new mathjax div content
                MathJax.Hub.Queue(["Typeset",MathJax.Hub,"MathOutput"]);
            }
        </script>
        <div id="MathOutput">
        You typed: ${}$
        </div>
        </body>
        </html>
    """
    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.__controls()
        self.__layout()

    def __controls(self):
        self.browser = QWebEngineView()
        self.browser.setHtml(self.pageSource)
        self.browser.loadFinished.connect(self.onLoadFinished)

    def onLoadFinished(self, ok):
        if ok:
            self.updateJax("Javascript-called-from-python-generated-this-mathjax")

    def updateJax(self, newMath):
            self.browser.page().runJavaScript("updateMathJax(\"$${}$$\")".format(newMath), self.ready)

    def __layout(self):
        self.vbox = QVBoxLayout()
        self.hBox = QVBoxLayout()
        self.hBox.addWidget(self.browser)
        self.vbox.addLayout(self.hBox)
        self.setLayout(self.vbox)

    def ready(self, returnValue):
        print(returnValue)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())