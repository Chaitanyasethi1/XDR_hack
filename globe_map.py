import streamlit.components.v1 as components

def render_3d_globe(height=520):
    """
    Renders the Antigravity 3D Threat Globe with World Map Continents.
    """
    globe_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.7.1/gsap.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; background: #000000; overflow: hidden; font-family: 'Inter', sans-serif; color: #fff; }}
            #canvas-container {{ width: 100%; height: {height}px; position: relative; cursor: grab; }}
            #canvas-container:active {{ cursor: grabbing; }}
            
            .hud-top {{ position: absolute; top: 15px; left: 15px; pointer-events: none; }}
            .wordmark {{ font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; letter-spacing: 4px; font-weight: 800; display: flex; align-items: center; gap: 15px; }}
            .live-badge {{ color: #ff3a3a; font-size: 0.65rem; display: flex; align-items: center; gap: 8px; }}
            .pulse-dot {{ width: 6px; height: 6px; background: #ff3a3a; border-radius: 50%; box-shadow: 0 0 10px #ff3a3a; animation: pulse 2s infinite; }}
            @keyframes pulse {{ 0% {{ transform: scale(0.9); opacity: 0.6; }} 50% {{ transform: scale(1.3); opacity: 1; }} 100% {{ transform: scale(0.9); opacity: 0.6; }} }}

            .hud-bottom {{ position: absolute; bottom: 15px; left: 15px; right: 15px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; pointer-events: none; }}
            .stat-card {{ background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 4px; padding: 12px; text-align: center; backdrop-filter: blur(10px); }}
            .label {{ font-size: 0.55rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; margin-bottom: 4px; }}
            .value {{ font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #00d4ff; text-shadow: 0 0 15px rgba(0, 212, 255, 0.4); }}
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div class="hud-top">
                <div class="wordmark">CIVIC SHIELD // <span class="live-badge"><div class="pulse-dot"></div> LIVE MONITORING</span></div>
            </div>
            <div class="hud-bottom">
                <div class="stat-card"><div class="label">YOUR IP</div><div id="ip-val" class="value">DETECTING...</div></div>
                <div class="stat-card"><div class="label">ACTIVE THREATS</div><div class="value">14</div></div>
                <div class="stat-card"><div class="label">SECURED NODES</div><div class="value">2,842</div></div>
                <div class="stat-card"><div class="label">THREAT LEVEL</div><div class="value" style="color:#ff3a3a">CRITICAL</div></div>
            </div>
        </div>

        <script>
            let scene, camera, renderer, globe, userPos;
            const radius = 200;

            function init() {{
                scene = new THREE.Scene();
                camera = new THREE.PerspectiveCamera(45, window.innerWidth / {height}, 1, 2000);
                camera.position.z = 550;

                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(window.innerWidth, {height});
                document.getElementById('canvas-container').appendChild(renderer.domElement);

                // Create Texture with Continents
                const loader = new THREE.TextureLoader();
                // Using a transparent world map topology for a clean cyber look
                loader.load('https://raw.githubusercontent.com/vasturiano/three-globe/master/example/img/earth-topology.png', (topoTexture) => {{
                    const canvas = document.createElement('canvas');
                    canvas.width = 1024; canvas.height = 512;
                    const ctx = canvas.getContext('2d');
                    ctx.fillStyle = '#01050a'; ctx.fillRect(0,0,1024,512);
                    
                    // Draw Continents (Simplified)
                    const img = topoTexture.image;
                    ctx.globalAlpha = 0.5;
                    ctx.drawImage(img, 0, 0, 1024, 512);
                    ctx.globalAlpha = 1.0;

                    // Draw Grid
                    ctx.strokeStyle = 'rgba(0,212,255,0.15)'; ctx.lineWidth = 1;
                    for(let i=0; i<=360; i+=20) {{ ctx.beginPath(); ctx.moveTo((i/360)*1024, 0); ctx.lineTo((i/360)*1024,512); ctx.stroke(); }}
                    for(let i=0; i<=180; i+=20) {{ ctx.beginPath(); ctx.moveTo(0,(i/180)*512); ctx.lineTo(1024,(i/180)*512); ctx.stroke(); }}

                    const texture = new THREE.CanvasTexture(canvas);
                    const geometry = new THREE.SphereGeometry(radius, 64, 64);
                    const material = new THREE.MeshPhongMaterial({{ 
                        map: texture, 
                        shininess: 10, 
                        transparent: true, 
                        opacity: 0.9,
                        emissive: 0x00d4ff,
                        emissiveIntensity: 0.05
                    }});
                    globe = new THREE.Mesh(geometry, material);
                    scene.add(globe);

                    // Atmosphere
                    const atmosGeo = new THREE.SphereGeometry(radius+8, 64, 64);
                    const atmosMat = new THREE.MeshBasicMaterial({{ color:0x00d4ff, transparent:true, opacity:0.04, side:THREE.BackSide }});
                    scene.add(new THREE.Mesh(atmosGeo, atmosMat));

                    detectIP();
                    animate();
                }});

                // Lights
                const light = new THREE.DirectionalLight(0xffffff, 1.2);
                light.position.set(5,3,5).normalize();
                scene.add(light);
                scene.add(new THREE.AmbientLight(0x404040, 0.8));

                // Star field
                const starGeo = new THREE.BufferGeometry();
                const starPos = [];
                for(let i=0; i<1000; i++) {{
                    starPos.push((Math.random()-0.5)*2000, (Math.random()-0.5)*2000, (Math.random()-0.5)*2000);
                }}
                starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
                scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({{ color: 0x666666, size: 1 }})));
            }}

            async function detectIP() {{
                try {{
                    const res = await fetch('https://ipapi.co/json/');
                    const data = await res.json();
                    document.getElementById('ip-val').innerText = data.ip;
                    userPos = latLngToVector(data.latitude, data.longitude, radius);
                    addPin(userPos, 0x10b981); // Green pin for user
                    addLabel(userPos, "PROTECTED_NODE (INDIA)");
                    setTimeout(() => spawnAttack(), 2000);
                }} catch(e) {{
                    document.getElementById('ip-val').innerText = '127.0.0.1';
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
                const pinGeo = new THREE.SphereGeometry(4, 16, 16);
                const pinMat = new THREE.MeshBasicMaterial({{ color: color }});
                const pin = new THREE.Mesh(pinGeo, pinMat);
                pin.position.copy(pos);
                globe.add(pin);
                
                // Add a glow ring
                const ringGeo = new THREE.RingGeometry(6, 8, 32);
                const ringMat = new THREE.MeshBasicMaterial({{ color: color, side: THREE.DoubleSide, transparent:true, opacity:0.3 }});
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.position.copy(pos.clone().multiplyScalar(1.02));
                ring.lookAt(new THREE.Vector3(0,0,0));
                globe.add(ring);
            }}

            function addLabel(pos, text) {{
                // Simplified labels using console logs as we are in a tight iframe
                console.log("MARKING: " + text);
            }}

            function spawnAttack() {{
                // Specific attacker locations pointing to India (roughly)
                const attackers = [
                    {{ name: 'CHINA_SOURCE', lat: 35.8617, lng: 104.1954, color: 0xff3a3a }},
                    {{ name: 'RUSSIA_SOURCE', lat: 61.5240, lng: 105.3188, color: 0xff3a3a }},
                    {{ name: 'US_EAST_NODE', lat: 37.0902, lng: -95.7129, color: 0x6C63FF }},
                    {{ name: 'EURO_NODE', lat: 48.8566, lng: 2.3522, color: 0x00d4ff }}
                ];
                attackers.forEach((atk, i) => {{
                    setTimeout(() => {{
                        const aPos = latLngToVector(atk.lat, atk.lng, radius);
                        addPin(aPos, atk.color);
                        createArc(atk.lat, atk.lng, atk.color);
                    }}, i * 2000);
                }});
            }}

            function createArc(lat, lng, color) {{
                const start = latLngToVector(lat, lng, radius);
                const end = userPos;
                const mid = start.clone().lerp(end, 0.5).normalize().multiplyScalar(radius + start.distanceTo(end)*0.4);
                const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
                
                const points = curve.getPoints(50);
                const arcLine = new THREE.Line(
                    new THREE.BufferGeometry().setFromPoints(points),
                    new THREE.LineBasicMaterial({{ color: color, transparent:true, opacity:0.3 }})
                );
                globe.add(arcLine);

                const packet = new THREE.Mesh(new THREE.SphereGeometry(3, 8, 8), new THREE.MeshBasicMaterial({{ color: color }}));
                globe.add(packet);

                let p = 0;
                function move() {{
                    p += 0.008;
                    if(p > 1) p = 0;
                    packet.position.copy(curve.getPointAt(p));
                    requestAnimationFrame(move);
                }}
                move();
            }}

            function animate() {{
                requestAnimationFrame(animate);
                if(globe) globe.rotation.y += 0.002;
                renderer.render(scene, camera);
            }}

            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / {height};
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, {height});
            }});

            init();
        </script>
    </body>
    </html>
    """
    components.html(globe_html, height=height)
