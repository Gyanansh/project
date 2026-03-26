const planetData = {
    Mercury: { grav: "3.7 m/s²", temp: "167°C", desc: "Mercury is the fastest planet, zipping around the Sun every 88 Earth days." },
    Venus: { grav: "8.87 m/s²", temp: "464°C", desc: "Venus is the hottest planet because of its thick, heat-trapping atmosphere." },
    Earth: { grav: "9.8 m/s²", temp: "15°C", desc: "Our home planet is the only place we know of so far that's inhabited by living things." },
    Mars: { grav: "3.71 m/s²", temp: "-65°C", desc: "Mars is a cold desert world. It has a very thin atmosphere and two moons." },
    Jupiter: { grav: "24.79 m/s²", temp: "-110°C", desc: "Jupiter is a giant gas world and the largest planet in our solar system." },
    Saturn: { grav: "10.44 m/s²", temp: "-140°C", desc: "Adorned with a dazzling, complex system of icy rings, Saturn is unique." },
    Uranus: { grav: "8.69 m/s²", temp: "-195°C", desc: "Uranus is an ice giant that rotates at a nearly 90-degree angle from the plane of its orbit." },
    Neptune: { grav: "11.15 m/s²", temp: "-201°C", desc: "Neptune is dark, cold, and whipped by supersonic winds. It is the last of the gas giants." }
};

function openModal(name) {
    const data = planetData[name];
    document.getElementById('m-name').innerText = name;
    document.getElementById('m-grav').innerText = data.grav;
    document.getElementById('m-temp').innerText = data.temp;
    document.getElementById('m-desc').innerText = data.desc;
    
    document.getElementById('planetModal').style.display = "block";
}

function closeModal() {
    document.getElementById('planetModal').style.display = "none";
}

// Close the modal if clicking the dark background
window.onclick = function(event) {
    const modal = document.getElementById('planetModal');
    if (event.target == modal) {
        closeModal();
    }
}