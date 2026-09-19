import os
import threading
from flask import Flask, render_template, request, redirect, url_for

# 1. Flask App Initialization
app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return '''
        <h2>Pharmacy Login</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username"><br><br>
            <input type="password" name="password" placeholder="Password"><br><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/dashboard')
def dashboard():
    return '<h2>Welcome to Pharmacy Dashboard</h2>'

# 2. Background mein Flask server chalane ka function
def run_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# 3. Kivy App jo WebView ke zariye app ke andar website chalayegi
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget

class PharmacyApp(App):
    def build(self):
        threading.Thread(target=run_flask, daemon=True).start()
        return Widget()

    def on_start(self):
        from kivy.utils import platform
        if platform == 'android':
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            
            WebView = autoclass('android.webkit.WebView')
            WebViewClient = autoclass('android.webkit.WebViewClient')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            
            @run_on_ui_thread
            def create_webview():
                webview = WebView(activity)
                webview.getSettings().setJavaScriptEnabled(True)
                webview.getSettings().setDomStorageEnabled(True)
                webview.setWebViewClient(WebViewClient())
                webview.loadUrl('http://127.0.0.1:5000/login')
                activity.setContentView(webview)
                
            Clock.schedule_once(lambda dt: create_webview(), 1.5)

if __name__ == '__main__':
    PharmacyApp().run()

