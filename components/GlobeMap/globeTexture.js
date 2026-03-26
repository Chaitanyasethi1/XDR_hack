import * as THREE from 'three';

/**
 * Generates an Earth texture with glowing cyan grid lines via Canvas.
 */
export const createGlobeTexture = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const context = canvas.getContext('2d');

    // Fill background (Deep Space Blue/Black)
    context.fillStyle = '#01050a';
    context.fillRect(0, 0, canvas.width, canvas.height);

    // Draw Grid Lines (Cyan Lat/Lng)
    context.strokeStyle = 'rgba(0, 212, 255, 0.4)';
    context.lineWidth = 1;

    // Longitudinal lines
    for (let i = 0; i <= 360; i += 20) {
        const x = (i / 360) * canvas.width;
        context.beginPath();
        context.moveTo(x, 0);
        context.lineTo(x, canvas.height);
        context.stroke();
    }

    // Latitudinal lines
    for (let i = 0; i <= 180; i += 20) {
        const y = (i / 180) * canvas.height;
        context.beginPath();
        context.moveTo(0, y);
        context.lineTo(canvas.width, y);
        context.stroke();
    }

    // Add subtle glow nodes at intersections
    context.fillStyle = 'rgba(0, 212, 255, 0.2)';
    for (let x = 0; x <= 360; x += 20) {
        for (let y = 0; y <= 180; y += 20) {
            context.beginPath();
            context.arc((x/360)*canvas.width, (y/180)*canvas.height, 2, 0, Math.PI * 2);
            context.fill();
        }
    }

    const texture = new THREE.CanvasTexture(canvas);
    return texture;
};
