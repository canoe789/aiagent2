/**
 * HELIX Frontend Port Discovery Module
 * Implements dynamic API endpoint discovery for SOP compliance
 */

class PortDiscovery {
    constructor() {
        // Align with SOP script port ranges
        this.knownPorts = [8000, 8001, 8002, 8003, 8004, 8005]; // Quick common ports
        this.apiPortRange = { start: 8000, end: 8099 }; // API service range (SOP compliant)
        this.orchestratorPortRange = { start: 8100, end: 8199 }; // Orchestrator range
        this.apiBase = null;
        this.discoveryTimeout = 5000; // 5 seconds timeout
        this.healthCheckPath = '/api/v1/health';
        this.maxScanAttempts = 50; // Align with find-port.sh MAX_ATTEMPTS
    }

    /**
     * Discover the active API endpoint
     * Implements P4 principle: idempotent and recoverable
     */
    async discoverApiEndpoint() {
        console.log('🔍 Starting API endpoint discovery...');
        
        // Try current page origin first (most likely to work)
        const currentOrigin = window.location.origin;
        if (await this.testEndpoint(currentOrigin)) {
            this.apiBase = currentOrigin;
            console.log(`✅ API discovered at current origin: ${this.apiBase}`);
            return this.apiBase;
        }

        // Try common localhost ports
        for (const port of this.knownPorts) {
            const testUrl = `http://localhost:${port}`;
            if (await this.testEndpoint(testUrl)) {
                this.apiBase = testUrl;
                console.log(`✅ API discovered at: ${this.apiBase}`);
                return this.apiBase;
            }
        }

        // Fallback: scan API service range (SOP compliant)
        console.log('📡 Scanning API service range (SOP compliant)...');
        const scannedPorts = new Set();
        
        for (let attempt = 0; attempt < this.maxScanAttempts; attempt++) {
            // Generate random port in API range (matches find-port.sh behavior)
            const port = Math.floor(Math.random() * (this.apiPortRange.end - this.apiPortRange.start + 1)) + this.apiPortRange.start;
            
            // Skip if already scanned
            if (scannedPorts.has(port)) {
                continue;
            }
            scannedPorts.add(port);
            
            const testUrl = `http://localhost:${port}`;
            if (await this.testEndpoint(testUrl)) {
                this.apiBase = testUrl;
                console.log(`✅ API discovered at: ${this.apiBase}`);
                return this.apiBase;
            }
        }

        throw new Error('❌ Could not discover API endpoint. Please ensure HELIX system is running.');
    }

    /**
     * Test if an endpoint is the active HELIX API
     */
    async testEndpoint(baseUrl) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000); // 2 second timeout per test

            const response = await fetch(`${baseUrl}${this.healthCheckPath}`, {
                method: 'GET',
                signal: controller.signal,
                cache: 'no-cache'
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                const health = await response.json();
                // Verify this is actually HELIX API
                if (health.status === 'healthy' && health.components) {
                    return true;
                }
            }
        } catch (error) {
            // Endpoint not available or not HELIX
            console.debug(`Endpoint test failed for ${baseUrl}:`, error.message);
        }
        return false;
    }

    /**
     * Get the discovered API base URL
     */
    getApiBase() {
        if (!this.apiBase) {
            throw new Error('API endpoint not yet discovered. Call discoverApiEndpoint() first.');
        }
        return this.apiBase;
    }

    /**
     * Build full API URL
     */
    buildApiUrl(path) {
        return `${this.getApiBase()}${path}`;
    }
}

// Global instance
const portDiscovery = new PortDiscovery();

/**
 * Initialize API discovery on page load
 * This ensures the frontend can always find the API regardless of dynamic ports
 */
window.initializeHelixApi = async function() {
    try {
        await portDiscovery.discoverApiEndpoint();
        console.log('🚀 HELIX API connection established');
        return true;
    } catch (error) {
        console.error('💥 HELIX API discovery failed:', error);
        return false;
    }
};

/**
 * Get the API base URL (after discovery)
 */
window.getHelixApiBase = function() {
    return portDiscovery.getApiBase();
};

/**
 * Build API URL with discovered base
 */
window.buildHelixApiUrl = function(path) {
    return portDiscovery.buildApiUrl(path);
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PortDiscovery, portDiscovery };
}