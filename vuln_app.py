#!/usr/bin/env python3
"""
Deliberately Vulnerable Login Page - Hydra Practice Target
Run this on your own machine only.
"""

from flask import Flask, request, render_template_string, redirect, url_for, session
import hashlib

app = Flask(__name__)
app.secret_key = "vulnerable_app_practice_key"

# The "correct" credentials - intentionally weak so Hydra can find them fast
VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"   # Common rockyou entry - Hydra will find this in seconds

# The cool login page
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXUS // Secure Access</title>
<style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
        font-family: 'Courier New', monospace;
        background: #0a0e1a;
        color: #00ff9d;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
    }

    /* Animated matrix background */
    #matrix {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: 0;
        opacity: 0.15;
    }

    .login-container {
        position: relative;
        z-index: 10;
        background: rgba(10, 14, 26, 0.9);
        border: 2px solid #00ff9d;
        border-radius: 12px;
        padding: 50px 40px;
        width: 400px;
        max-width: 90%;
        box-shadow:
            0 0 20px rgba(0, 255, 157, 0.3),
            0 0 60px rgba(0, 255, 157, 0.1),
            inset 0 0 20px rgba(0, 255, 157, 0.05);
        backdrop-filter: blur(10px);
        animation: pulse-border 3s ease-in-out infinite;
    }

    @keyframes pulse-border {
        0%, 100% { box-shadow: 0 0 20px rgba(0,255,157,0.3), 0 0 60px rgba(0,255,157,0.1); }
        50% { box-shadow: 0 0 30px rgba(0,255,157,0.5), 0 0 90px rgba(0,255,157,0.2); }
    }

    .logo {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        letter-spacing: 6px;
        margin-bottom: 8px;
        text-shadow: 0 0 10px #00ff9d, 0 0 20px #00ff9d;
        animation: flicker 4s infinite;
    }

    @keyframes flicker {
        0%, 100% { opacity: 1; }
        92% { opacity: 1; }
        93% { opacity: 0.3; }
        94% { opacity: 1; }
        96% { opacity: 0.5; }
        97% { opacity: 1; }
    }

    .subtitle {
        text-align: center;
        font-size: 11px;
        color: #4a7a6a;
        letter-spacing: 3px;
        margin-bottom: 40px;
    }

    .status-line {
        font-size: 10px;
        color: #4a7a6a;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-dot {
        width: 8px; height: 8px;
        background: #00ff9d;
        border-radius: 50%;
        box-shadow: 0 0 8px #00ff9d;
        animation: blink 1.5s infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .input-group {
        margin-bottom: 25px;
        position: relative;
    }

    .input-group label {
        display: block;
        font-size: 10px;
        color: #4a7a6a;
        letter-spacing: 2px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }

    .input-group input {
        width: 100%;
        padding: 14px 16px;
        background: rgba(0, 255, 157, 0.03);
        border: 1px solid #1a4a3a;
        border-radius: 6px;
        color: #00ff9d;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        letter-spacing: 1px;
        outline: none;
        transition: all 0.3s;
    }

    .input-group input:focus {
        border-color: #00ff9d;
        background: rgba(0, 255, 157, 0.08);
        box-shadow: 0 0 15px rgba(0, 255, 157, 0.3);
    }

    .input-group input::placeholder {
        color: #2a4a3a;
        letter-spacing: 2px;
    }

    .login-btn {
        width: 100%;
        padding: 15px;
        background: transparent;
        border: 2px solid #00ff9d;
        color: #00ff9d;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        font-weight: bold;
        letter-spacing: 4px;
        text-transform: uppercase;
        cursor: pointer;
        border-radius: 6px;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }

    .login-btn:hover {
        background: #00ff9d;
        color: #0a0e1a;
        box-shadow: 0 0 30px #00ff9d;
    }

    .login-btn::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }

    .login-btn:hover::before {
        left: 100%;
    }

    .error-box {
        margin-top: 20px;
        padding: 12px;
        background: rgba(255, 0, 80, 0.1);
        border: 1px solid #ff0050;
        border-radius: 6px;
        color: #ff0050;
        font-size: 12px;
        text-align: center;
        letter-spacing: 1px;
        animation: shake 0.3s;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-8px); }
        75% { transform: translateX(8px); }
    }

    .footer {
        text-align: center;
        margin-top: 30px;
        font-size: 10px;
        color: #2a4a3a;
        letter-spacing: 2px;
    }

    .scan-line {
        position: absolute;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff9d, transparent);
        animation: scan 4s linear infinite;
        opacity: 0.5;
    }

    @keyframes scan {
        0% { top: 0; }
        100% { top: 100%; }
    }
</style>
</head>
<body>
<canvas id="matrix"></canvas>

<div class="login-container">
    <div class="scan-line"></div>
    <div class="logo">NEXUS</div>
    <div class="subtitle">SECURE ACCESS TERMINAL</div>

    <div class="status-line">
        <div class="status-dot"></div>
        <span>SYSTEM ONLINE // ENCRYPTED CHANNEL</span>
    </div>

    <form method="POST" action="/login">
        <div class="input-group">
            <label>▸ Username</label>
            <input type="text" name="username" placeholder="enter username" autocomplete="off" autofocus>
        </div>

        <div class="input-group">
            <label>▸ Password</label>
            <input type="password" name="password" placeholder="enter password" autocomplete="off">
        </div>

        <button type="submit" class="login-btn">Authenticate</button>
    </form>

    {% if error %}
    <div class="error-box">✗ ACCESS DENIED // INVALID CREDENTIALS</div>
    {% endif %}

    <div class="footer">[ NEXUS SECURITY v2.4.1 ]</div>
</div>

<script>
// Matrix rain effect
const canvas = document.getElementById('matrix');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
const fontSize = 14;
const columns = canvas.width / fontSize;
const drops = Array(Math.floor(columns)).fill(1);

function drawMatrix() {
    ctx.fillStyle = 'rgba(10, 14, 26, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#00ff9d';
    ctx.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        drops[i]++;
    }
}
setInterval(drawMatrix, 50);

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});
</script>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>ACCESS GRANTED</title>
<style>
    body {
        font-family: 'Courier New', monospace;
        background: #0a0e1a;
        color: #00ff9d;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        text-align: center;
    }
    .box {
        border: 2px solid #00ff9d;
        padding: 60px;
        border-radius: 12px;
        box-shadow: 0 0 60px rgba(0,255,157,0.5);
    }
    h1 {
        font-size: 48px;
        letter-spacing: 8px;
        text-shadow: 0 0 20px #00ff9d;
        margin-bottom: 20px;
    }
    p { color: #4a7a6a; letter-spacing: 3px; }
</style>
</head>
<body>
<div class="box">
    <h1>✓ GRANTED</h1>
    <p>WELCOME, ADMINISTRATOR</p>
</div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(LOGIN_PAGE, error=False)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        return render_template_string(SUCCESS_PAGE)
    else:
        return render_template_string(LOGIN_PAGE, error=True)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════╗
║   NEXUS VULNERABLE APP - RUNNING         ║
║   Target: http://127.0.0.1:5000          ║
║   Valid creds: admin / password123       ║
║   Practice with Hydra on this app only   ║
╚══════════════════════════════════════════╝
    """)
    app.run(host="127.0.0.1", port=5000, debug=False)