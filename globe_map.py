import streamlit.components.v1 as components
import json

def render_3d_globe(incidents_df, height=450):
    """
    Renders the 3D Threat Globe with mouse drag rotation and clear continent/country borders.
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
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: #000000; overflow: hidden; font-family: 'Inter', sans-serif; color: #fff; }}
            #canvas-container {{ 
                width: 100vw; 
                height: {height}px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                position: relative; 
                cursor: grab; 
                user-select: none;
            }}
            #canvas-container:active {{ cursor: grabbing; }}
            
            /* HUD */
            .hud-top {{ position: absolute; top: 15px; left: 15px; pointer-events: none; z-index: 10; }}
            .wordmark {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; letter-spacing: 3px; font-weight: 800; display: flex; align-items: center; gap: 12px; }}
            .live-badge {{ color: #ff3a3a; font-size: 0.6rem; display: flex; align-items: center; gap: 6px; }}
            .pulse-dot {{ width: 5px; height: 5px; background: #ff3a3a; border-radius: 50%; box-shadow: 0 0 10px #ff3a3a; animation: pulse 2s infinite; }}
            @keyframes pulse {{ 0% {{ transform: scale(0.9); opacity: 0.6; }} 50% {{ transform: scale(1.3); opacity: 1; }} 100% {{ transform: scale(0.9); opacity: 0.6; }} }}

            /* Drag hint */
            .drag-hint {{
                position: absolute;
                top: 15px;
                right: 15px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.55rem;
                color: rgba(0,212,255,0.5);
                letter-spacing: 1px;
                pointer-events: none;
                z-index: 10;
                animation: fadeHint 4s forwards;
            }}
            @keyframes fadeHint {{ 0% {{ opacity:1; }} 70% {{ opacity:1; }} 100% {{ opacity:0; }} }}

            .hud-bottom {{ position: absolute; bottom: 12px; left: 15px; right: 15px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; pointer-events: none; z-index: 10; }}
            .stat-card {{ background: rgba(0, 212, 255, 0.04); border: 1px solid rgba(0, 212, 255, 0.15); border-radius: 4px; padding: 8px; text-align: center; backdrop-filter: blur(8px); }}
            .label {{ font-size: 0.45rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; margin-bottom: 2px; }}
            .value {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00d4ff; text-shadow: 0 0 8px rgba(0, 212, 255, 0.3); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            
            .active-alert {{ position: absolute; top: 40px; left: 15px; color: #ff3a3a; font-family: 'JetBrains Mono'; font-size: 0.5rem; letter-spacing: 1px; animation: slideIn 0.5s ease; z-index: 10; }}
            @keyframes slideIn {{ from {{ transform: translateX(-15px); opacity:0; }} to {{ transform: translateX(0); opacity:1; }} }}

            /* Tooltip */
            #tooltip {{
                position: absolute;
                background: rgba(0,10,20,0.85);
                border: 1px solid rgba(0,212,255,0.4);
                border-radius: 4px;
                padding: 6px 10px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.55rem;
                color: #00d4ff;
                pointer-events: none;
                display: none;
                z-index: 20;
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div class="hud-top">
                <div class="wordmark">CIVIC SHIELD // <span class="live-badge"><div class="pulse-dot"></div> LIVE TRACKING</span></div>
            </div>
            <div class="drag-hint">⟳ DRAG TO ROTATE</div>
            <div id="alert-feed" class="active-alert"></div>
            <div id="tooltip"></div>
            <div class="hud-bottom">
                <div class="stat-card"><div class="label">YOUR IP</div><div id="ip-val" class="value">DETECTING...</div></div>
                <div class="stat-card"><div class="label">LIVE INCIDENTS</div><div class="value" id="count-val">0</div></div>
                <div class="stat-card"><div class="label">SECURED NODES</div><div class="value">2,842</div></div>
                <div class="stat-card"><div class="label">STATUS</div><div class="value" id="status-val" style="color:#10b981">STABLE</div></div>
            </div>
        </div>

        <script>
            let scene, camera, renderer, globe, userPos;
            let isDragging = false;
            let prevMouse = {{ x: 0, y: 0 }};
            let rotVelocity = {{ x: 0, y: 0 }};
            let autoRotate = true;
            let autoRotateTimeout = null;
            const container = document.getElementById('canvas-container');
            const radius = 200;
            const incidents = {incidents_json};

            function init() {{
                scene = new THREE.Scene();
                const aspect = container.clientWidth / container.clientHeight;
                camera = new THREE.PerspectiveCamera(35, aspect, 1, 2000);
                camera.position.z = 620;

                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                container.appendChild(renderer.domElement);

                // Lighting
                scene.add(new THREE.AmbientLight(0x445566, 2.0));
                const dLight = new THREE.DirectionalLight(0xffffff, 1.2);
                dLight.position.set(5, 3, 5).normalize();
                scene.add(dLight);
                const backLight = new THREE.DirectionalLight(0x0044aa, 0.3);
                backLight.position.set(-5, -2, -5).normalize();
                scene.add(backLight);

                buildGlobe();
                setupMouseControls();
                window.addEventListener('resize', onWindowResize);
            }}

            function buildGlobe() {{
                // ── Earth texture: use NASA Blue Marble (clear land/ocean contrast) ──
                const loader = new THREE.TextureLoader();

                // Primary texture: Blue Marble natural earth (clear continents)
                const earthTexUrl = 'https://raw.githubusercontent.com/turban/webgl-earth/master/images/2_no_clouds_4k.jpg';
                // Fallback: topology
                const fallbackUrl = 'https://unpkg.com/three-globe/example/img/earth-day.jpg';

                function buildMesh(texture) {{
                    // Draw country/coastal borders on top of the texture
                    const canvas = document.createElement('canvas');
                    canvas.width = 2048; canvas.height = 1024;
                    const ctx = canvas.getContext('2d');

                    // Draw base texture
                    ctx.drawImage(texture.image, 0, 0, 2048, 1024);

                    // Tint oceans slightly darker/bluer for cyber look
                    ctx.fillStyle = 'rgba(0, 5, 30, 0.25)';
                    ctx.fillRect(0, 0, 2048, 1024);

                    // Draw grid lines (lat/lng)
                    ctx.strokeStyle = 'rgba(0,212,255,0.07)';
                    ctx.lineWidth = 0.8;
                    for (let lon = 0; lon <= 360; lon += 15) {{
                        ctx.beginPath();
                        ctx.moveTo((lon / 360) * 2048, 0);
                        ctx.lineTo((lon / 360) * 2048, 1024);
                        ctx.stroke();
                    }}
                    for (let lat = 0; lat <= 180; lat += 15) {{
                        ctx.beginPath();
                        ctx.moveTo(0, (lat / 180) * 1024);
                        ctx.lineTo(2048, (lat / 180) * 1024);
                        ctx.stroke();
                    }}

                    // Bright equator & prime meridian
                    ctx.strokeStyle = 'rgba(0,212,255,0.18)';
                    ctx.lineWidth = 1.2;
                    ctx.beginPath(); ctx.moveTo(0, 512); ctx.lineTo(2048, 512); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(1024, 0); ctx.lineTo(1024, 1024); ctx.stroke();

                    const finalTex = new THREE.CanvasTexture(canvas);

                    globe = new THREE.Mesh(
                        new THREE.SphereGeometry(radius, 80, 80),
                        new THREE.MeshPhongMaterial({{
                            map: finalTex,
                            shininess: 12,
                            transparent: true,
                            opacity: 0.97,
                            emissive: 0x001122,
                            emissiveIntensity: 0.15,
                            specular: 0x334455,
                        }})
                    );
                    globe.rotation.y = -Math.PI / 2; // Start centered on Europe/Africa
                    scene.add(globe);

                    // Atmosphere glow
                    const atmos = new THREE.Mesh(
                        new THREE.SphereGeometry(radius + 8, 64, 64),
                        new THREE.MeshBasicMaterial({{ color: 0x00aaff, transparent: true, opacity: 0.04, side: THREE.BackSide }})
                    );
                    scene.add(atmos);

                    // Wide outer glow ring
                    const outerGlow = new THREE.Mesh(
                        new THREE.SphereGeometry(radius + 18, 64, 64),
                        new THREE.MeshBasicMaterial({{ color: 0x003366, transparent: true, opacity: 0.02, side: THREE.BackSide }})
                    );
                    scene.add(outerGlow);

                    detectIP();
                    processIncidents();
                    animate();
                }}

                // Try primary, fallback on error
                loader.load(earthTexUrl, buildMesh, undefined, () => {{
                    loader.load(fallbackUrl, buildMesh, undefined, () => {{
                        // Manual fallback: draw land shapes on canvas
                        const canvas = document.createElement('canvas');
                        canvas.width = 2048; canvas.height = 1024;
                        const ctx = canvas.getContext('2d');
                        ctx.fillStyle = '#01090f'; ctx.fillRect(0, 0, 2048, 1024);

                        // Simple colored continent blobs
                        const continents = [
                            // [x%, y%, w%, h%, label]
                            [27, 18, 15, 28, 'North America'],
                            [30, 48, 10, 20, 'South America'],
                            [46, 18, 18, 30, 'Europe/Africa'],
                            [62, 18, 22, 32, 'Asia'],
                            [72, 55, 10, 12, 'Australia'],
                        ];
                        continents.forEach(([x, y, w, h]) => {{
                            const gx = (x / 100) * 2048;
                            const gy = (y / 100) * 1024;
                            const gw = (w / 100) * 2048;
                            const gh = (h / 100) * 1024;
                            const grad = ctx.createRadialGradient(gx+gw/2, gy+gh/2, 0, gx+gw/2, gy+gh/2, Math.max(gw,gh)/2);
                            grad.addColorStop(0, 'rgba(0,80,40,0.9)');
                            grad.addColorStop(1, 'rgba(0,30,15,0.1)');
                            ctx.fillStyle = grad;
                            ctx.fillRect(gx, gy, gw, gh);
                        }});

                        // Grid
                        ctx.strokeStyle = 'rgba(0,212,255,0.1)'; ctx.lineWidth = 1;
                        for (let i = 0; i <= 360; i += 15) {{ ctx.beginPath(); ctx.moveTo((i/360)*2048, 0); ctx.lineTo((i/360)*2048, 1024); ctx.stroke(); }}
                        for (let i = 0; i <= 180; i += 15) {{ ctx.beginPath(); ctx.moveTo(0, (i/180)*1024); ctx.lineTo(2048, (i/180)*1024); ctx.stroke(); }}

                        const tex = new THREE.CanvasTexture(canvas);
                        buildMesh({{ image: canvas }});
                    }});
                }});
            }}

            function setupMouseControls() {{
                const el = renderer.domElement;

                // Mouse
                el.addEventListener('mousedown', (e) => {{
                    isDragging = true;
                    prevMouse = {{ x: e.clientX, y: e.clientY }};
                    rotVelocity = {{ x: 0, y: 0 }};
                    autoRotate = false;
                    clearTimeout(autoRotateTimeout);
                }});

                window.addEventListener('mousemove', (e) => {{
                    if (!isDragging || !globe) return;
                    const dx = e.clientX - prevMouse.x;
                    const dy = e.clientY - prevMouse.y;
                    globe.rotation.y += dx * 0.005;
                    globe.rotation.x += dy * 0.005;
                    // Clamp vertical rotation
                    globe.rotation.x = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, globe.rotation.x));
                    rotVelocity.x = dy * 0.003;
                    rotVelocity.y = dx * 0.003;
                    prevMouse = {{ x: e.clientX, y: e.clientY }};
                }});

                window.addEventListener('mouseup', () => {{
                    if (!isDragging) return;
                    isDragging = false;
                    // Resume auto-rotate after 3s of inactivity
                    autoRotateTimeout = setTimeout(() => {{
                        autoRotate = true;
                    }}, 3000);
                }});

                // Touch support
                el.addEventListener('touchstart', (e) => {{
                    isDragging = true;
                    prevMouse = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
                    rotVelocity = {{ x: 0, y: 0 }};
                    autoRotate = false;
                    clearTimeout(autoRotateTimeout);
                    e.preventDefault();
                }}, {{ passive: false }});

                window.addEventListener('touchmove', (e) => {{
                    if (!isDragging || !globe) return;
                    const dx = e.touches[0].clientX - prevMouse.x;
                    const dy = e.touches[0].clientY - prevMouse.y;
                    globe.rotation.y += dx * 0.005;
                    globe.rotation.x += dy * 0.005;
                    globe.rotation.x = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, globe.rotation.x));
                    rotVelocity.x = dy * 0.003;
                    rotVelocity.y = dx * 0.003;
                    prevMouse = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
                    e.preventDefault();
                }}, {{ passive: false }});

                window.addEventListener('touchend', () => {{
                    isDragging = false;
                    autoRotateTimeout = setTimeout(() => {{ autoRotate = true; }}, 3000);
                }});
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
                    addPin(userPos, 0x10b981, 4, '📍 YOU');
                }} catch(e) {{
                    document.getElementById('ip-val').innerText = '127.0.0.1';
                    userPos = latLngToVector(20.5937, 78.9629, radius);
                    addPin(userPos, 0x10b981, 4, '📍 YOU');
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

            function addPin(pos, color, size=3, label='') {{
                const pin = new THREE.Mesh(
                    new THREE.SphereGeometry(size, 16, 16),
                    new THREE.MeshBasicMaterial({{ color: color }})
                );
                pin.position.copy(pos);

                // Glow ring
                const ring = new THREE.Mesh(
                    new THREE.RingGeometry(size + 1, size + 3, 32),
                    new THREE.MeshBasicMaterial({{ color: color, transparent: true, opacity: 0.4, side: THREE.DoubleSide }})
                );
                ring.position.copy(pos);
                ring.lookAt(0, 0, 0);

                globe.add(pin);
                globe.add(ring);
            }}

            function processIncidents() {{
                const countVal = document.getElementById('count-val');
                const alertFeed = document.getElementById('alert-feed');
                const statusVal = document.getElementById('status-val');
                
                countVal.innerText = incidents.length;
                if (incidents.length > 5) {{
                    statusVal.innerText = "THREAT_ACTIVE";
                    statusVal.style.color = "#ff3a3a";
                }}

                incidents.forEach((inc, i) => {{
                    setTimeout(() => {{
                        if (!inc.lat || !inc.lng) {{
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
                if (!userPos) return;
                const start = latLngToVector(lat, lng, radius);
                const end = userPos;
                const mid = start.clone().lerp(end, 0.5).normalize().multiplyScalar(radius + start.distanceTo(end) * 0.4);
                const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
                
                const arcLine = new THREE.Line(
                    new THREE.BufferGeometry().setFromPoints(curve.getPoints(60)),
                    new THREE.LineBasicMaterial({{ color: color, transparent: true, opacity: 0.5 }})
                );
                globe.add(arcLine);

                const packet = new THREE.Mesh(
                    new THREE.SphereGeometry(3.5, 8, 8),
                    new THREE.MeshBasicMaterial({{ color: color }})
                );
                globe.add(packet);

                // Add source pin
                const srcPos = latLngToVector(lat, lng, radius);
                addPin(srcPos, color, 2.5);

                let p = 0;
                function move() {{
                    p += 0.012;
                    if (p > 1) {{
                        globe.remove(packet);
                        setTimeout(() => globe.remove(arcLine), 3000);
                        return;
                    }}
                    packet.position.copy(curve.getPointAt(p));
                    requestAnimationFrame(move);
                }}
                move();
            }}

            function animate() {{
                requestAnimationFrame(animate);
                if (globe) {{
                    if (!isDragging) {{
                        // Inertia: decay velocity
                        rotVelocity.x *= 0.92;
                        rotVelocity.y *= 0.92;
                        globe.rotation.x += rotVelocity.x;
                        globe.rotation.y += rotVelocity.y;
                        globe.rotation.x = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, globe.rotation.x));

                        // Gentle auto-rotate when idle
                        if (autoRotate) {{
                            globe.rotation.y += 0.0015;
                        }}
                    }}
                }}
                renderer.render(scene, camera);
            }}

            init();
        </script>
    </body>
    </html>
    """
    components.html(globe_html, height=height)
