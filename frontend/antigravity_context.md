# CropSight Project Context for Antigravity

Hello fellow Antigravity instance! 
If you are reading this, the user's teammate has asked you to help collaborate on **CropSight**, an AI-powered crop health mapping dashboard built for a 24-Hour Hackathon supporting SDG Goal 2 (Zero Hunger).

## Project Overview
- **Goal:** Analyze aerial/drone imagery to detect crop stress and irrigation anomalies, generating an actionable, color-coded health map in under 60 minutes.
- **Frontend Stack:** Pure HTML, CSS (Vanilla), and JS (Vanilla) to optimize for speed, minimalism, and reliability. 
- **Typography:** `Outfit` from Google Fonts.

## Design System: "Agriculture Light Theme"
- **Base Background:** `#f8faf5` (soft airy green/white) featuring a subtle topographic/dotted map pattern overlay.
- **Accents:**
  - `Leaf Green` (Emerald): `#16a34a`
  - `Harvest Yellow`: `#d97706`
  - Text typically uses `#0a1f16` (Deep Forest) and `#3f634d` (Secondary/Muted).
- **Component Style:** Light glassmorphism. Cards use white translucent backgrounds (`rgba(255, 255, 255, 0.7)`), soft borders, 16px to 20px border radii, and gentle liftoff drop shadows on hover (`0 15px 35px rgba(0,0,0,0.05)`).
- **Layout Engine:** The feature grid uses CSS Flexbox with `justify-content: center` so any orphaned cards perfectly center on the bottom row across all screen sizes.

## Current State & Completed Features
- **Landing Page (`index.html`)**: Complete! It includes a responsive navigation bar, a hero map mockup (with dynamic pulsating healthy/stress zones and a floating drone pin 📍), and a gorgeous 10-card feature grid. 
- **Sign-in Flow**: Currently bypassed to speed up the presentation demo. "Sign In" buttons link directly to `dashboard.html`. 
- **Code Pushed**: The initial frontend layout is successfully tracked and fully pushed to the `main` branch of GitHub.

## Next Steps for Immediate Collaboration
- **Your Primary Focus (Backend)**: Your teammate (the one running this Antigravity instance) is responsible for the Backend API & AI Integration! The frontend developer relies on you to build robust endpoints for the VARI crop health analysis, the KMeans clustering logic, and the Google Sign-in verification. 
- **Frontend Context**: The frontend developer is independently working on `dashboard.html` and `index.html`. They will need you to expose REST APIs so they can fetch the severity reports and interactive map data to display on the dashboard UI.
- **Get Started**: You should immediately check out `backend/.env` for configuration and start setting up the server architecture!

Good luck hacking the backend!
