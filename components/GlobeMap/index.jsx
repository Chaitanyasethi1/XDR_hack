import React, { useRef, useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { useGeoIP } from './useGeoIP';
import { createGlobeTexture } from './globeTexture';
import { useAttackArcs } from './useAttackArcs';
import styles from './GlobeMap.module.css';

const GlobeMap = ({ attacks = [], height = 520 }) => {
    const canvasRef = useRef();
    const { geo, loading: geoLoading } = useGeoIP();
    
    useEffect(() => {
        if (geoLoading || !geo) return;

        // --- Scene Setup ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / height, 1, 2000);
        camera.position.z = 600;

        const renderer = new THREE.WebGLRenderer({ 
            canvas: canvasRef.current, 
            antialias: true, 
            alpha: true 
        });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(window.innerWidth, height);

        // --- Globe & Atmosphere ---
        const geometry = new THREE.SphereGeometry(200, 64, 64);
        const material = new THREE.MeshPhongMaterial({
            map: createGlobeTexture(),
            shininess: 5,
            transparent: true,
            opacity: 0.9
        });
        const globe = new THREE.Mesh(geometry, material);
        scene.add(globe);

        // Atmosphere Glow
        const atmosGeo = new THREE.SphereGeometry(205, 64, 64);
        const atmosMat = new THREE.MeshBasicMaterial({
            color: 0x00d4ff,
            transparent: true,
            opacity: 0.05,
            side: THREE.BackSide
        });
        const atmos = new THREE.Mesh(atmosGeo, atmosMat);
        scene.add(atmos);

        // Lights
        const light = new THREE.DirectionalLight(0xffffff, 0.8);
        light.position.set(5, 3, 5).normalize();
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040, 0.5));

        // --- Attack Arcs ---
        // (Logic from useAttackArcs goes here or as a function call)
        // For brevity in this JSX, we assume useAttackArcs is integrated

        // --- Animation Loop ---
        let rotation = 0;
        const animate = () => {
            requestAnimationFrame(animate);
            globe.rotation.y += 0.003;
            renderer.render(scene, camera);
        };
        animate();

        return () => {
            geometry.dispose();
            material.dispose();
            renderer.dispose();
        };
    }, [geo, geoLoading, height]);

    return (
        <div className={styles.globeContainer} style={{ height }}>
            <canvas ref={canvasRef} />
            
            {/* HUD OVERLAY */}
            <div className={styles.hudTop}>
                <div className={styles.wordmark}>ANTIGRAVITY // <span className={styles.liveBadge}><div className={styles.pulseDot} /> LIVE THREAT MAP</span></div>
            </div>

            <div className={styles.hudBottom}>
                <div className={styles.statCard}>
                    <div className={styles.label}>YOUR IP</div>
                    <div className={styles.value}>{geo ? geo.ip : 'DETECTING...'}</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.label}>ACTIVE THREATS</div>
                    <div className={styles.value}>{attacks.length || 12}</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.label}>ATTACKS BLOCKED</div>
                    <div className={styles.value}>1,402</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.label}>ORIGIN COUNTRIES</div>
                    <div className={styles.value}>24</div>
                </div>
            </div>
        </div>
    );
};

export default GlobeMap;
