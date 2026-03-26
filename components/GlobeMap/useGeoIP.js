import { useState, useEffect } from 'react';

/**
 * Hook to detect user's geolocation using ipapi.co
 */
export const useGeoIP = () => {
    const [geo, setGeo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchIP = async () => {
            try {
                const response = await fetch('https://ipapi.co/json/');
                if (!response.ok) throw new Error('IP Detection Failed');
                const data = await response.json();
                setGeo({
                    ip: data.ip,
                    lat: data.latitude,
                    lng: data.longitude,
                    city: data.city,
                    country: data.country_name
                });
            } catch (err) {
                console.error("GeoIP Error:", err);
                setError(err.message);
                // Fallback to a default location (London) if blocked
                setGeo({ ip: '0.0.0.0', lat: 51.5074, lng: -0.1278, city: 'London', country: 'United Kingdom' });
            } finally {
                setLoading(false);
            }
        };

        fetchIP();
    }, []);

    return { geo, loading, error };
};
export default useGeoIP;
