import { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from "react-leaflet";
import L from "leaflet";
import Layout from "../components/Layout";
import "../styles/nearby.css";
import "leaflet/dist/leaflet.css";

// Fix default Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
    iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// Custom icons
const userIcon = new L.DivIcon({
    className: "user-marker",
    html: `<div class="user-dot"><div class="user-dot-inner"></div></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
});

const kendraIcon = new L.Icon({
    iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
    iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
});

// Sample Seva Kendra offices across India
const SEVA_KENDRAS = [
    // Maharashtra
    { id: 1, name: "CSC Seva Kendra — Andheri", city: "Mumbai", state: "Maharashtra", lat: 19.1136, lng: 72.8697, address: "Plot No 45, Andheri East, Mumbai 400069", phone: "+91-22-26831234", hours: "10:00 AM – 5:00 PM", services: ["Aadhaar Update", "PAN Card", "Birth Certificate", "Passport"] },
    { id: 2, name: "Digital Seva Kendra — Dadar", city: "Mumbai", state: "Maharashtra", lat: 19.0178, lng: 72.8478, address: "Shop 12, Dadar West, Mumbai 400028", phone: "+91-22-24321567", hours: "9:30 AM – 6:00 PM", services: ["Income Certificate", "Caste Certificate", "Domicile"] },
    { id: 3, name: "e-Seva Kendra — Pune Station", city: "Pune", state: "Maharashtra", lat: 18.5289, lng: 73.8747, address: "Near Pune Station, Shivaji Nagar, Pune 411005", phone: "+91-20-25674321", hours: "10:00 AM – 5:30 PM", services: ["Land Record", "Birth Certificate", "PAN Card"] },
    { id: 4, name: "Jan Seva Kendra — Nashik Road", city: "Nashik", state: "Maharashtra", lat: 19.9832, lng: 73.7917, address: "Nashik Road, Near ST Stand, Nashik 422101", phone: "+91-253-2345678", hours: "10:00 AM – 5:00 PM", services: ["Aadhaar", "Voter ID", "Ration Card"] },
    { id: 5, name: "CSC Kendra — Nagpur", city: "Nagpur", state: "Maharashtra", lat: 21.1458, lng: 79.0882, address: "Dharampeth, Nagpur 440010", phone: "+91-712-2345678", hours: "10:00 AM – 5:00 PM", services: ["PAN Card", "Income Certificate", "Birth Certificate"] },

    // Delhi NCR
    { id: 6, name: "Digital Seva Kendra — Connaught Place", city: "New Delhi", state: "Delhi", lat: 28.6315, lng: 77.2167, address: "Block B, Connaught Place, New Delhi 110001", phone: "+91-11-23456789", hours: "9:00 AM – 5:00 PM", services: ["Aadhaar", "PAN", "Passport", "Voter ID"] },
    { id: 7, name: "Jan Seva Kendra — Dwarka", city: "New Delhi", state: "Delhi", lat: 28.5921, lng: 77.0460, address: "Sector 12, Dwarka, New Delhi 110078", phone: "+91-11-28034567", hours: "10:00 AM – 6:00 PM", services: ["Birth Certificate", "Caste Certificate", "Income Certificate"] },
    { id: 8, name: "e-District Kendra — Noida", city: "Noida", state: "Uttar Pradesh", lat: 28.5355, lng: 77.3910, address: "Sector 62, Noida 201309", phone: "+91-120-4567890", hours: "10:00 AM – 5:30 PM", services: ["Land Record", "Domicile", "Income Certificate"] },

    // Karnataka
    { id: 9, name: "Nada Kacheri — Bengaluru", city: "Bengaluru", state: "Karnataka", lat: 12.9716, lng: 77.5946, address: "MG Road, Bengaluru 560001", phone: "+91-80-22345678", hours: "10:00 AM – 5:30 PM", services: ["Caste Certificate", "Income Certificate", "Birth Certificate"] },
    { id: 10, name: "CSC Seva Kendra — Koramangala", city: "Bengaluru", state: "Karnataka", lat: 12.9352, lng: 77.6245, address: "Koramangala 4th Block, Bengaluru 560034", phone: "+91-80-25674321", hours: "9:30 AM – 5:00 PM", services: ["PAN Card", "Aadhaar Update", "Passport"] },

    // Tamil Nadu
    { id: 11, name: "e-Seva Kendra — T. Nagar", city: "Chennai", state: "Tamil Nadu", lat: 13.0418, lng: 80.2341, address: "T. Nagar, Chennai 600017", phone: "+91-44-24567890", hours: "10:00 AM – 5:00 PM", services: ["Birth Certificate", "Income Certificate", "Community Certificate"] },

    // Rajasthan
    { id: 12, name: "eMitra Kendra — Jaipur", city: "Jaipur", state: "Rajasthan", lat: 26.9124, lng: 75.7873, address: "MI Road, Jaipur 302001", phone: "+91-141-2345678", hours: "9:00 AM – 6:00 PM", services: ["Aadhaar", "Ration Card", "Bhamashah Card"] },

    // West Bengal
    { id: 13, name: "Duare Sarkar — Kolkata", city: "Kolkata", state: "West Bengal", lat: 22.5726, lng: 88.3639, address: "Park Street, Kolkata 700016", phone: "+91-33-22345678", hours: "10:00 AM – 5:00 PM", services: ["Birth Certificate", "Income Certificate", "Caste Certificate"] },

    // Gujarat
    { id: 14, name: "e-Gram Kendra — Ahmedabad", city: "Ahmedabad", state: "Gujarat", lat: 23.0225, lng: 72.5714, address: "CG Road, Ahmedabad 380009", phone: "+91-79-26789012", hours: "10:00 AM – 5:30 PM", services: ["Aadhaar", "PAN Card", "Domicile"] },

    // Telangana
    { id: 15, name: "Mee-Seva — Hyderabad", city: "Hyderabad", state: "Telangana", lat: 17.3850, lng: 78.4867, address: "Abids, Hyderabad 500001", phone: "+91-40-23456789", hours: "10:00 AM – 5:00 PM", services: ["Income Certificate", "Birth Certificate", "Caste Certificate"] },
];

// Calculate distance between two coordinates (Haversine formula)
function getDistanceKm(lat1, lng1, lat2, lng2) {
    const R = 6371;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLng = ((lng2 - lng1) * Math.PI) / 180;
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// Component to fly map to user location
function FlyToUser({ center }) {
    const map = useMap();
    useEffect(() => {
        if (center) {
            map.flyTo(center, 12, { duration: 1.5 });
        }
    }, [center, map]);
    return null;
}

export default function NearbyKendra() {
    const [userLocation, setUserLocation] = useState(null);
    const [locating, setLocating] = useState(false);
    const [locationError, setLocationError] = useState("");
    const [selectedKendra, setSelectedKendra] = useState(null);
    const [nearbyKendras, setNearbyKendras] = useState([]);
    const [showComplaintForm, setShowComplaintForm] = useState(false);
    const [complaintData, setComplaintData] = useState({ name: "", issue: "", details: "" });
    const [complaintSent, setComplaintSent] = useState(false);
    const [searchRadius, setSearchRadius] = useState(50); // km
    const mapRef = useRef(null);

    // Default center (India center)
    const defaultCenter = [20.5937, 78.9629];

    const getUserLocation = () => {
        setLocating(true);
        setLocationError("");

        if (!navigator.geolocation) {
            setLocationError("Geolocation is not supported by your browser.");
            setLocating(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const loc = [pos.coords.latitude, pos.coords.longitude];
                setUserLocation(loc);
                setLocating(false);

                // Calculate distances and sort
                const withDistance = SEVA_KENDRAS.map((k) => ({
                    ...k,
                    distance: getDistanceKm(loc[0], loc[1], k.lat, k.lng),
                }))
                    .filter((k) => k.distance <= searchRadius)
                    .sort((a, b) => a.distance - b.distance);

                setNearbyKendras(withDistance);
            },
            (err) => {
                setLocationError(
                    err.code === 1
                        ? "Location permission denied. Please allow location access."
                        : "Could not get your location. Please try again."
                );
                setLocating(false);
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    };

    // Re-filter when radius changes
    useEffect(() => {
        if (userLocation) {
            const withDistance = SEVA_KENDRAS.map((k) => ({
                ...k,
                distance: getDistanceKm(userLocation[0], userLocation[1], k.lat, k.lng),
            }))
                .filter((k) => k.distance <= searchRadius)
                .sort((a, b) => a.distance - b.distance);
            setNearbyKendras(withDistance);
        }
    }, [searchRadius, userLocation]);

    const openDirections = (kendra) => {
        const url = `https://www.google.com/maps/dir/?api=1&destination=${kendra.lat},${kendra.lng}`;
        window.open(url, "_blank");
    };

    const handleComplaintSubmit = (e) => {
        e.preventDefault();
        setComplaintSent(true);
        setTimeout(() => {
            setShowComplaintForm(false);
            setComplaintSent(false);
            setComplaintData({ name: "", issue: "", details: "" });
        }, 3000);
    };

    return (
        <Layout>
            <div className="nk-page">
                {/* Hero */}
                <div className="nk-hero">
                    <div className="nk-hero-content">
                        <h1>📍 Nearby Seva Kendras</h1>
                        <p>Find government service centers near you. Visit in person or file a complaint online.</p>
                        <div className="nk-hero-actions">
                            <button className="nk-btn-locate" onClick={getUserLocation} disabled={locating}>
                                {locating ? (
                                    <><span className="nk-spinner"></span> Locating...</>
                                ) : (
                                    <><span>📍</span> Find Nearest Centers</>
                                )}
                            </button>
                            <div className="nk-radius-control">
                                <label>Radius:</label>
                                <select value={searchRadius} onChange={(e) => setSearchRadius(Number(e.target.value))}>
                                    <option value={10}>10 km</option>
                                    <option value={25}>25 km</option>
                                    <option value={50}>50 km</option>
                                    <option value={100}>100 km</option>
                                    <option value={500}>500 km</option>
                                    <option value={5000}>All India</option>
                                </select>
                            </div>
                        </div>
                        {locationError && <div className="nk-error">{locationError}</div>}
                    </div>
                </div>

                {/* Main content */}
                <div className="nk-content">
                    <div className="nk-layout">

                        {/* Map */}
                        <div className="nk-map-container">
                            <MapContainer
                                center={defaultCenter}
                                zoom={5}
                                className="nk-map"
                                ref={mapRef}
                                scrollWheelZoom={true}
                            >
                                <TileLayer
                                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                />

                                <FlyToUser center={userLocation} />

                                {/* User location */}
                                {userLocation && (
                                    <>
                                        <Marker position={userLocation} icon={userIcon}>
                                            <Popup>📍 You are here</Popup>
                                        </Marker>
                                        <Circle
                                            center={userLocation}
                                            radius={searchRadius * 1000}
                                            pathOptions={{
                                                color: "#2563eb",
                                                fillColor: "#2563eb",
                                                fillOpacity: 0.06,
                                                weight: 1.5,
                                                dashArray: "6 4",
                                            }}
                                        />
                                    </>
                                )}

                                {/* Office markers */}
                                {(userLocation ? nearbyKendras : SEVA_KENDRAS).map((k) => (
                                    <Marker
                                        key={k.id}
                                        position={[k.lat, k.lng]}
                                        icon={kendraIcon}
                                        eventHandlers={{
                                            click: () => setSelectedKendra(k),
                                        }}
                                    >
                                        <Popup>
                                            <div className="nk-popup">
                                                <strong>{k.name}</strong>
                                                <span>{k.city}, {k.state}</span>
                                                {k.distance && <span className="nk-popup-dist">{k.distance.toFixed(1)} km away</span>}
                                            </div>
                                        </Popup>
                                    </Marker>
                                ))}
                            </MapContainer>

                            {userLocation && nearbyKendras.length > 0 && (
                                <div className="nk-map-badge">{nearbyKendras.length} center{nearbyKendras.length > 1 ? "s" : ""} found within {searchRadius} km</div>
                            )}
                        </div>

                        {/* Sidebar: List + Detail */}
                        <div className="nk-sidebar">
                            {/* Selected kendra detail */}
                            {selectedKendra ? (
                                <div className="nk-detail-card">
                                    <button className="nk-back-btn" onClick={() => setSelectedKendra(null)}>← Back to list</button>
                                    <h3>{selectedKendra.name}</h3>
                                    <div className="nk-detail-meta">
                                        <span>📍 {selectedKendra.city}, {selectedKendra.state}</span>
                                        {selectedKendra.distance && <span className="nk-dist-badge">{selectedKendra.distance.toFixed(1)} km</span>}
                                    </div>

                                    <div className="nk-detail-rows">
                                        <div className="nk-detail-row">
                                            <span className="nk-detail-icon">🏠</span>
                                            <span>{selectedKendra.address}</span>
                                        </div>
                                        <div className="nk-detail-row">
                                            <span className="nk-detail-icon">📞</span>
                                            <span>{selectedKendra.phone}</span>
                                        </div>
                                        <div className="nk-detail-row">
                                            <span className="nk-detail-icon">🕐</span>
                                            <span>{selectedKendra.hours}</span>
                                        </div>
                                    </div>

                                    <div className="nk-services-list">
                                        <h4>Available Services</h4>
                                        <div className="nk-service-tags">
                                            {selectedKendra.services.map((s) => (
                                                <span key={s} className="nk-service-tag">{s}</span>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="nk-detail-actions">
                                        <button className="nk-btn-directions" onClick={() => openDirections(selectedKendra)}>
                                            🗺️ Get Directions
                                        </button>
                                        <button className="nk-btn-complaint" onClick={() => { setShowComplaintForm(true); setComplaintSent(false); }}>
                                            📝 File Complaint
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                /* List of kendras */
                                <div className="nk-list">
                                    <h3 className="nk-list-title">
                                        {userLocation ? `Nearby Centers (${nearbyKendras.length})` : "All Seva Kendras"}
                                    </h3>
                                    {(userLocation ? nearbyKendras : SEVA_KENDRAS).length === 0 ? (
                                        <div className="nk-empty">
                                            <span>🔍</span>
                                            <p>No centers found within {searchRadius} km. Try increasing the radius.</p>
                                        </div>
                                    ) : (
                                        (userLocation ? nearbyKendras : SEVA_KENDRAS).map((k) => (
                                            <div
                                                key={k.id}
                                                className="nk-list-item"
                                                onClick={() => setSelectedKendra(k)}
                                            >
                                                <div className="nk-list-item-top">
                                                    <h4>{k.name}</h4>
                                                    {k.distance && <span className="nk-dist-badge">{k.distance.toFixed(1)} km</span>}
                                                </div>
                                                <p>{k.city}, {k.state}</p>
                                                <div className="nk-list-item-services">
                                                    {k.services.slice(0, 3).map((s) => (
                                                        <span key={s} className="nk-service-tag-sm">{s}</span>
                                                    ))}
                                                    {k.services.length > 3 && <span className="nk-service-tag-sm nk-more">+{k.services.length - 3}</span>}
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Complaint Modal */}
                {showComplaintForm && selectedKendra && (
                    <div className="nk-modal-overlay" onClick={() => setShowComplaintForm(false)}>
                        <div className="nk-modal" onClick={(e) => e.stopPropagation()}>
                            <button className="nk-modal-close" onClick={() => setShowComplaintForm(false)}>✕</button>

                            {complaintSent ? (
                                <div className="nk-complaint-success">
                                    <div className="nk-success-icon">✅</div>
                                    <h3>Complaint Registered!</h3>
                                    <p>Reference: CMP-{Date.now().toString(36).toUpperCase()}</p>
                                    <p>Your complaint about <strong>{selectedKendra.name}</strong> has been successfully submitted.</p>
                                </div>
                            ) : (
                                <>
                                    <h3>📝 File a Complaint</h3>
                                    <p className="nk-modal-sub">Regarding: <strong>{selectedKendra.name}</strong></p>
                                    <form onSubmit={handleComplaintSubmit}>
                                        <div className="nk-form-group">
                                            <label>Your Name</label>
                                            <input
                                                type="text"
                                                value={complaintData.name}
                                                onChange={(e) => setComplaintData({ ...complaintData, name: e.target.value })}
                                                placeholder="Enter your full name"
                                                required
                                            />
                                        </div>
                                        <div className="nk-form-group">
                                            <label>Issue Type</label>
                                            <select
                                                value={complaintData.issue}
                                                onChange={(e) => setComplaintData({ ...complaintData, issue: e.target.value })}
                                                required
                                            >
                                                <option value="">Select issue</option>
                                                <option value="delay">Service Delay</option>
                                                <option value="behavior">Staff Behavior</option>
                                                <option value="wrong_info">Wrong Information</option>
                                                <option value="system_down">System Not Working</option>
                                                <option value="corruption">Corruption / Bribery</option>
                                                <option value="other">Other</option>
                                            </select>
                                        </div>
                                        <div className="nk-form-group">
                                            <label>Details</label>
                                            <textarea
                                                value={complaintData.details}
                                                onChange={(e) => setComplaintData({ ...complaintData, details: e.target.value })}
                                                placeholder="Describe your complaint in detail..."
                                                rows={4}
                                                required
                                            />
                                        </div>
                                        <button type="submit" className="nk-btn-submit-complaint">
                                            Submit Complaint
                                        </button>
                                    </form>
                                </>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </Layout>
    );
}
