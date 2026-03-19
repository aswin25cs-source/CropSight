// Initialize Lucide Icons
lucide.createIcons();

document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const processingState = document.getElementById('processingState');
    const resultState = document.getElementById('resultState');
    const emptyAnalytics = document.getElementById('emptyAnalytics');
    const analyticsContent = document.getElementById('analyticsContent');
    const mapOverlay = document.getElementById('mapOverlay');

    // Handle Drag & Drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    // Handle Click Upload
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        // Only accept images
        if (!file.type.startsWith('image/')) {
            alert('Please upload a valid image file (RGB or GeoTIFF equivalent).');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const imageUrl = e.target.result;
            simulateProcessing(imageUrl);
        };
        reader.readAsDataURL(file);
    }

    function simulateProcessing(imageUrl) {
        // UI Transitions
        uploadZone.classList.add('hidden');
        processingState.classList.remove('hidden');
        
        // Simulate API call to ML pipeline
        setTimeout(() => {
            processingState.classList.add('hidden');
            resultState.classList.remove('hidden');
            emptyAnalytics.classList.add('hidden');
            analyticsContent.classList.remove('hidden');
            
            displayResults(imageUrl);
        }, 3000); // 3 seconds simulation
    }

    function displayResults(imageUrl) {
        // Set background image
        mapOverlay.style.backgroundImage = `url(${imageUrl})`;
        mapOverlay.style.backgroundSize = 'contain';
        mapOverlay.style.backgroundRepeat = 'no-repeat';
        mapOverlay.style.backgroundPosition = 'center';
        
        // Create an SVG overlay layer to draw zones
        const svgHTML = `
            <svg width="100%" height="100%" style="position: absolute; top:0; left:0; pointer-events: none;">
                <!-- Zone Alpha (Critical) -->
                <polygon points="20%,20% 40%,25% 35%,50% 15%,40%" fill="rgba(239, 68, 68, 0.4)" stroke="#ef4444" stroke-width="2" style="animation: pulse 2s infinite"/>
                
                <!-- Zone Beta (Warning) -->
                <polygon points="50%,30% 80%,20% 85%,60% 60%,50%" fill="rgba(245, 158, 11, 0.3)" stroke="#f59e0b" stroke-width="2"/>
                
                <!-- Zone Gamma (Healthy) -->
                <polygon points="10%,60% 45%,55% 50%,90% 20%,85%" fill="rgba(16, 185, 129, 0.2)" stroke="#10b981" stroke-width="2"/>
                
                <!-- Info Badges -->
                <g transform="translate(25%, 35%)">
                    <circle cx="0" cy="0" r="12" fill="#1a1a1e" stroke="#ef4444" stroke-width="2"/>
                    <text x="0" y="4" font-family="Inter" font-size="10" font-weight="bold" fill="#fff" text-anchor="middle">A</text>
                </g>
                <g transform="translate(68%, 40%)">
                    <circle cx="0" cy="0" r="12" fill="#1a1a1e" stroke="#f59e0b" stroke-width="2"/>
                    <text x="0" y="4" font-family="Inter" font-size="10" font-weight="bold" fill="#fff" text-anchor="middle">B</text>
                </g>
                <g transform="translate(30%, 75%)">
                    <circle cx="0" cy="0" r="12" fill="#1a1a1e" stroke="#10b981" stroke-width="2"/>
                    <text x="0" y="4" font-family="Inter" font-size="10" font-weight="bold" fill="#fff" text-anchor="middle">C</text>
                </g>
            </svg>
            <style>
                @keyframes pulse {
                    0% { fill: rgba(239, 68, 68, 0.3); }
                    50% { fill: rgba(239, 68, 68, 0.6); }
                    100% { fill: rgba(239, 68, 68, 0.3); }
                }
            </style>
        `;
        
        mapOverlay.innerHTML = svgHTML;
        
        // Initialize download report feature
        setupDownloadReport();

        // Add staggered animation to zone cards
        const cards = document.querySelectorAll('.zone-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.4s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 * (index + 1) + 300); // Trigger after UI shows up
        });
    }

    // Handle view toggles
    const viewBtns = document.querySelectorAll('.view-btn');
    viewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            viewBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Just simulate a change effect if an image is loaded
            if (!resultState.classList.contains('hidden')) {
                // Apply a quick transition effect
                mapOverlay.style.filter = 'contrast(1.2) saturate(1.5)';
                setTimeout(() => {
                    if (btn.innerText === 'NDVI') {
                        mapOverlay.style.filter = 'hue-rotate(90deg) saturate(2)';
                    } else if (btn.innerText === 'Thermal') {
                        mapOverlay.style.filter = 'hue-rotate(-180deg) saturate(3)';
                    } else {
                        mapOverlay.style.filter = 'none';
                    }
                }, 150);
            }
        });
    });

    function setupDownloadReport() {
        const downloadBtn = document.querySelector('.analytics-panel .icon-btn');
        if (downloadBtn && !downloadBtn.hasAttribute('data-initialized')) {
            downloadBtn.setAttribute('data-initialized', 'true');
            downloadBtn.addEventListener('click', () => {
                if (!analyticsContent.classList.contains('hidden')) {
                    const btnIcon = downloadBtn.querySelector('i');
                    const originalIcon = btnIcon.getAttribute('data-lucide');
                    
                    // Show loading state
                    btnIcon.setAttribute('data-lucide', 'loader-2');
                    downloadBtn.classList.add('animate-spin');
                    lucide.createIcons();
                    
                    setTimeout(() => {
                        // Reset
                        downloadBtn.classList.remove('animate-spin');
                        btnIcon.setAttribute('data-lucide', 'check');
                        lucide.createIcons();
                        
                        // Simulate Download
                        const a = document.createElement('a');
                        a.href = 'data:application/json;charset=utf-8,' + encodeURIComponent(JSON.stringify({
                            reportId: "RPT-" + new Date().toISOString().split('T')[0],
                            overallScore: 72,
                            status: "Moderate Stress",
                            zones: [
                                { id: "Alpha", health: 45, issue: "Severe water stress detected", action: "Increase irrigation by 20% immediately" },
                                { id: "Beta", health: 68, issue: "Early signs of nutrient deficiency", action: "Schedule nitrogen top-dressing" },
                                { id: "Gamma", health: 94, issue: "Optimal growth conditions", action: "Maintain current regimen" }
                            ]
                        }, null, 2));
                        a.download = 'CropSight_Health_Report.json';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        
                        setTimeout(() => {
                            btnIcon.setAttribute('data-lucide', originalIcon);
                            lucide.createIcons();
                        }, 2000);
                    }, 1500);
                } else {
                    alert('Please analyze an image first before exporting a report.');
                }
            });
        }
    }
});
