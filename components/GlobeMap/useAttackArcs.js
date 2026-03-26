import * as THREE from 'three';

/**
 * Logic for calculating and animating Bezier attack arcs.
 */
export const useAttackArcs = (scene, userLatLng, radius) => {
    const arcs = [];
    
    const latLngToVector3 = (lat, lng, R) => {
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lng + 180) * (Math.PI / 180);
        return new THREE.Vector3(
            -R * Math.sin(phi) * Math.cos(theta),
            R * Math.cos(phi),
            R * Math.sin(phi) * Math.sin(theta)
        );
    };

    const createArc = (attack) => {
        const start = latLngToVector3(attack.lat, attack.lng, radius);
        const end = latLngToVector3(userLatLng.lat, userLatLng.lng, radius);

        // Midpoint lifted for 3D trajectory
        const mid = start.clone().lerp(end, 0.5);
        const distance = start.distanceTo(end);
        mid.normalize().multiplyScalar(radius + distance * 0.4);

        const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
        const points = curve.getPoints(50);
        
        // Arc Line (Ghost Trail)
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ 
            color: attack.severity === 'CRITICAL' ? '#ff3a3a' : '#00d4ff', 
            opacity: 0.15, 
            transparent: true 
        });
        const line = new THREE.Line(geometry, material);
        scene.add(line);

        // Moving Packet (Small Sphere)
        const packetGeo = new THREE.SphereGeometry(2, 8, 8);
        const packetMat = new THREE.MeshBasicMaterial({ 
            color: attack.severity === 'CRITICAL' ? '#ff3a3a' : '#00d4ff', 
            opacity: 0.9, 
            transparent: true 
        });
        const packet = new THREE.Mesh(packetGeo, packetMat);
        scene.add(packet);

        return { curve, packet, line, progress: 0, attack };
    };

    const updateArcs = (delta) => {
        arcs.forEach((arc, index) => {
            arc.progress += delta * 0.5;
            if (arc.progress > 1) {
                arc.progress = 0; // Loop or callback
                window.dispatchEvent(new CustomEvent('globe:attack-hit', { detail: arc.attack }));
            }
            const pos = arc.curve.getPointAt(arc.progress);
            arc.packet.position.copy(pos);
        });
    };

    return { createArc, updateArcs, arcs };
};
