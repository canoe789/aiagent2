#!/usr/bin/env python3
"""
HELIX Dynamic Port Management Startup Script
Implements SOP-compliant dynamic port allocation with P4 principle support
"""

import os
import sys
import subprocess
import time
import asyncio
import signal
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class DynamicPortManager:
    """Manages dynamic port allocation for HELIX services"""
    
    def __init__(self):
        self.allocated_ports = {}
        self.max_retries = 3
        self.retry_delay = 1
        
    def find_available_port(self, service_type="api"):
        """Find an available port using the SOP script"""
        script_path = PROJECT_ROOT / "scripts" / "find-port.sh"
        
        if not script_path.exists():
            raise RuntimeError(f"Port discovery script not found: {script_path}")
            
        try:
            result = subprocess.run(
                [str(script_path), "", "", service_type],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                port = int(result.stdout.strip())
                print(f"Found available port for {service_type}: {port}")
                return port
            else:
                raise RuntimeError(f"Port discovery failed: {result.stderr}")
                
        except (subprocess.TimeoutExpired, ValueError) as e:
            raise RuntimeError(f"Port discovery error: {e}")
    
    def allocate_service_port(self, service_name, service_type="api"):
        """Allocate a port for a service with retry logic (P4 principle)"""
        for attempt in range(self.max_retries):
            try:
                port = self.find_available_port(service_type)
                
                # Test if we can actually bind to this port
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.bind(('localhost', port))
                    sock.close()
                    self.allocated_ports[service_name] = port
                    return port
                except OSError:
                    # Port became unavailable between discovery and binding
                    if attempt < self.max_retries - 1:
                        print(f"Port {port} became unavailable, retrying... ({attempt + 1}/{self.max_retries})")
                        time.sleep(self.retry_delay)
                        continue
                    raise
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Port allocation attempt {attempt + 1} failed: {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise RuntimeError(f"Failed to allocate port for {service_name} after {self.max_retries} attempts")
        
        raise RuntimeError(f"Exhausted all retries for {service_name}")

async def start_helix_with_dynamic_ports():
    """Start HELIX system with dynamic port management"""
    
    print("🔧 HELIX Dynamic Port Management Startup")
    print("=" * 50)
    
    port_manager = DynamicPortManager()
    
    try:
        # Allocate ports for services
        api_port = port_manager.allocate_service_port("api", "api")
        
        # Set environment variables for dynamic ports
        os.environ["API_PORT"] = str(api_port)
        os.environ["API_HOST"] = "0.0.0.0"
        
        # Keep database port fixed (best practice)
        postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        print(f"📊 Using fixed database port: {postgres_port}")
        
        print(f"🌐 API Server will start on: http://localhost:{api_port}")
        print(f"📚 API Documentation: http://localhost:{api_port}/docs")
        
        # Import and start the original system
        from start_system import SystemManager
        
        # Override the port in the system manager
        system_manager = SystemManager()
        
        # Start the system
        await system_manager.start_system()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Check if we're in the right directory
        if not (PROJECT_ROOT / "start_system.py").exists():
            print("❌ Error: Please run from HELIX project root directory")
            sys.exit(1)
            
        # Run the dynamic startup
        asyncio.run(start_helix_with_dynamic_ports())
        
    except KeyboardInterrupt:
        print("\n✅ HELIX system shutdown completed")
    except Exception as e:
        print(f"💥 Critical error: {e}")
        sys.exit(1)