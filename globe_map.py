import streamlit.components.v1 as components
import json

def render_3d_globe(incidents_df, height=450):
    """
    Renders the 3D Threat Globe with a more COMPACT scale.
    """
    incidents_list = []
    if incidents_df is not None and not incidents_df.empty:
        recent_df = incidents_df.tail(15)
        for _, row in recent_df.iterrows():
            incidents_list.append({
                "ip": str(row.get('source_ip', '0.0.0.0')),
                "type": str(row.get('event_type', 'ANOMALY')),
                "severity": str(row.get('risk_level', 'MEDIUM')),
                "lat": row.get('lat', 0), 
                "lng": row.get('lng', 0),
                "city": str(row.get('city', 'Unknown'))
            })

    incidents_json = json.dumps(incidents_list)

    globe_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.7.1/gsap.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; background: #000000; overflow: hidden; font-family: 'Inter', sans-serif; color: #fff; }}
            #canvas-container {{ 
                width: 100vw; 
                height: {height}px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                position: relative; 
                cursor: grab; 
            }}
            #canvas-container:active {{ cursor: grabbing; }}
            
            .hud-top {{ position: absolute; top: 15px; left: 15px; pointer-events: none; }}
            .wordmark {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; letter-spacing: 3px; font-weight: 800; display: flex; align-items: center; gap: 12px; }}
            .live-badge {{ color: #ff3a3a; font-size: 0.6rem; display: flex; align-items: center; gap: 6px; }}
            .pulse-dot {{ width: 5px; height: 5px; background: #ff3a3a; border-radius: 50%; box-shadow: 0 0 10px #ff3a3a; animation: pulse 2s infinite; }}
            @keyframes pulse {{ 0% {{ transform: scale(0.9); opacity: 0.6; }} 50% {{ transform: scale(1.3); opacity: 1; }} 100% {{ transform: scale(0.9); opacity: 0.6; }} }}

            .hud-bottom {{ position: absolute; bottom: 12px; left: 15px; right: 15px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; pointer-events: none; }}
            .stat-card {{ background: rgba(0, 212, 255, 0.04); border: 1px solid rgba(0, 212, 255, 0.15); border-radius: 4px; padding: 8px; text-align: center; backdrop-filter: blur(8px); }}
            .label {{ font-size: 0.45rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; margin-bottom: 2px; }}
            .value {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00d4ff; text-shadow: 0 0 8px rgba(0, 212, 255, 0.3); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            
            .active-alert {{ position: absolute; top: 40px; left: 15px; color: #ff3a3a; font-family: 'JetBrains Mono'; font-size: 0.5rem; letter-spacing: 1px; animation: slideIn 0.5s ease; }}
            @keyframes slideIn {{ from {{ transform: translateX(-15px); opacity:0; }} to {{ transform: translateX(0); opacity:1; }} }}
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div class="hud-top">
                <div class="wordmark">CIVIC SHIELD // <span class="live-badge"><div class="pulse-dot"></div> LIVE TRACKING</span></div>
            </div>
            <div id="alert-feed" class="active-alert"></div>
            <div class="hud-bottom">
                <div class="stat-card"><div class="label">YOUR IP</div><div id="ip-val" class="value">DETECTING...</div></div>
                <div class="stat-card"><div class="label">LIVE INCIDENTS</div><div class="value" id="count-val">0</div></div>
                <div class="stat-card"><div class="label">SECURED NODES</div><div class="value">2,842</div></div>
                <div class="stat-card"><div class="label">STATUS</div><div class="value" id="status-val" style="color:#10b981">STABLE</div></div>
            </div>
        </div>

        <script>
            let scene, camera, renderer, globe, userPos;
            const container = document.getElementById('canvas-container');
            const radius = 200;
            const incidents = {incidents_json};

            function init() {{
                scene = new THREE.Scene();
                const aspect = container.clientWidth / container.clientHeight;
                camera = new THREE.PerspectiveCamera(35, aspect, 1, 2000);
                camera.position.z = 640; // Pulled back for smaller appearance

                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                container.appendChild(renderer.domElement);

                // Persist Rotation
                const savedRotation = localStorage.getItem('globe_rotation') || 0;

                // Load Texture
                const loader = new THREE.TextureLoader();
                loader.load('https://raw.githubusercontent.com/vasturiano/three-globe/master/example/img/earth-topology.png', (topoTexture) => {{
                    const canvas = document.createElement('canvas');
                    canvas.width = 1024; canvas.height = 512;
                    const ctx = canvas.getContext('2d');
                    ctx.fillStyle = '#01050a'; ctx.fillRect(0,0,1024,512);
                    
                    ctx.globalAlpha = 0.5;
                    ctx.drawImage(topoTexture.image, 0, 0, 1024, 512);
                    ctx.globalAlpha = 1.0;

                    ctx.strokeStyle = 'rgba(0,212,255,0.08)'; ctx.lineWidth = 1;
                    for(let i=0; i<=360; i+=20) {{ ctx.beginPath(); ctx.moveTo((i/360)*1024, 0); ctx.lineTo((i/360)*1024,512); ctx.stroke(); }}
                    for(let i=0; i<=180; i+=20) {{ ctx.beginPath(); ctx.moveTo(0,(i/180)*512); ctx.lineTo(1024,(i/180)*512); ctx.stroke(); }}

                    const texture = new THREE.CanvasTexture(canvas);
                    globe = new THREE.Mesh(
                        new THREE.SphereGeometry(radius, 64, 64),
                        new THREE.MeshPhongMaterial({{ map: texture, shininess: 8, transparent: true, opacity: 0.95, emissive: 0x00d4ff, emissiveIntensity: 0.05 }})
                    );
                    globe.rotation.y = parseFloat(savedRotation);
                    scene.add(globe);

                    const atmos = new THREE.Mesh(
                        new THREE.SphereGeometry(radius+6, 64, 64),
                        new THREE.MeshBasicMaterial({{ color:0x00d4ff, transparent:true, opacity:0.03, side:THREE.BackSide }})
                    );
                    scene.add(atmos);

                    detectIP();
                    processIncidents();
                    animate();
                }});

                scene.add(new THREE.AmbientLight(0x404040, 1.2));
                const dLight = new THREE.DirectionalLight(0xffffff, 1);
                dLight.position.set(5,3,5).normalize();
                scene.add(dLight);
                
                window.addEventListener('resize', onWindowResize);
            }}

            function onWindowResize() {{
                const w = container.clientWidth;
                const h = container.clientHeight;
                camera.aspect = w / h;
                camera.updateProjectionMatrix();
                renderer.setSize(w, h);
            }}

            async function detectIP() {{
                try {{
                    const res = await fetch('https://ipapi.co/json/');
                    const data = await res.json();
                    document.getElementById('ip-val').innerText = data.ip;
                    userPos = latLngToVector(data.latitude, data.longitude, radius);
                    addPin(userPos, 0x10b981);
                }} catch(e) {{
                    document.getElementById('ip-val').innerText = '127.0.0.1';
                    userPos = latLngToVector(20.5937, 78.9629, radius);
                    addPin(userPos, 0x10b981);
                }}
            }}

            function latLngToVector(lat, lng, R) {{
                const phi = (90 - lat) * (Math.PI / 180);
                const theta = (lng + 180) * (Math.PI / 180);
                return new THREE.Vector3(
                    -R * Math.sin(phi) * Math.cos(theta),
                    R * Math.cos(phi),
                    R * Math.sin(phi) * Math.sin(theta)
                );
            }}

            function addPin(pos, color) {{
                const pin = new THREE.Mesh(new THREE.SphereGeometry(3, 16, 16), new THREE.MeshBasicMaterial({{ color: color }}));
                pin.position.copy(pos);
                globe.add(pin);
            }}

            function processIncidents() {{
                const countVal = document.getElementById('count-val');
                const alertFeed = document.getElementById('alert-feed');
                const statusVal = document.getElementById('status-val');
                
                countVal.innerText = incidents.length;
                if(incidents.length > 5) {{
                    statusVal.innerText = "THREAT_ACTIVE";
                    statusVal.style.color = "#ff3a3a";
                }}

                incidents.forEach((inc, i) => {{
                    setTimeout(() => {{
                        if(!inc.lat || !inc.lng) {{
                            inc.lat = (Math.random() - 0.5) * 140;
                            inc.lng = (Math.random() - 0.5) * 360;
                        }}
                        const color = inc.severity === 'CRITICAL' ? 0xff3a3a : (inc.severity === 'HIGH' ? 0xffa500 : 0x00d4ff);
                        createArc(inc.lat, inc.lng, color);
                        alertFeed.innerText = "INCOMING: " + inc.type + " [" + inc.ip + "]";
                    }}, i * 1200);
                }});
            }}

            function createArc(lat, lng, color) {{
                if(!userPos) return;
                const start = latLngToVector(lat, lng, radius);
                const end = userPos;
                const mid = start.clone().lerp(end, 0.5).normalize().multiplyScalar(radius + start.distanceTo(end)*0.4);
                const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
                
                const arcLine = new THREE.Line(
                    new THREE.BufferGeometry().setFromPoints(curve.getPoints(50)),
                    new THREE.LineBasicMaterial({{ color: color, transparent:true, opacity:0.3 }})
                );
                globe.add(arcLine);

                const packet = new THREE.Mesh(new THREE.SphereGeometry(3, 8, 8), new THREE.MeshBasicMaterial({{ color: color }}));
                globe.add(packet);

                let p = 0;
                function move() {{
                    p += 0.01;
                    if(p > 1) {{
                        globe.remove(packet);
                        globe.remove(arcLine);
                        return;
                    }}
                    packet.position.copy(curve.getPointAt(p));
                    requestAnimationFrame(move);
                }}
                move();
            }}

            function animate() {{
                requestAnimationFrame(animate);
                if(globe) {{
                    globe.rotation.y += 0.002;
                    localStorage.setItem('globe_rotation', globe.rotation.y);
                }}
                renderer.render(scene, camera);
            }}

            init();
        </script>
    </body>
    </html>
    """
    components.html(globe_html, height=height)
