"""
Agent Worker for Project HELIX v2.0
Multi-agent worker that polls for tasks and processes them
"""

import asyncio
import structlog
from typing import Dict

from sdk.agent_sdk import AgentWorker, BaseAgent
from agents.creative_director import CreativeDirectorAgent

logger = structlog.get_logger(__name__)


class MockVisualDirectorAgent(BaseAgent):
    """Temporary mock for Visual Director Agent"""
    
    def __init__(self):
        super().__init__("AGENT_2")
    
    async def process_task(self, task_input):
        from database.models import TaskOutput
        
        # Get creative brief from artifacts
        artifacts = await self.get_artifacts(task_input.artifacts)
        creative_brief = artifacts.get("creative_brief", {})
        
        logger.info("Processing visual concepts based on creative brief",
                   agent_id=self.agent_id)
        
        # Mock visual concepts
        visual_concepts = {
            "style_direction": "Modern and professional",
            "color_palette": ["#2563eb", "#1f2937", "#f3f4f6", "#ffffff"],
            "typography": {
                "primary_font": "Inter",
                "secondary_font": "Source Sans Pro",
                "font_scale": "1.25 (Major Third)"
            },
            "layout_principles": [
                "Clean grid system",
                "Generous white space",
                "Clear visual hierarchy"
            ],
            "visual_elements": {
                "iconography": "Minimal line icons",
                "imagery": "Professional photography with tech focus",
                "graphics": "Subtle geometric patterns"
            },
            "responsive_approach": "Mobile-first design",
            "accessibility_considerations": [
                "High contrast ratios",
                "Focus indicators",
                "Screen reader optimization"
            ]
        }
        
        return TaskOutput(
            schema_id="VisualExplorations_v1.0",
            payload=visual_concepts
        )


class MockFrontendEngineerAgent(BaseAgent):
    """Temporary mock for Frontend Engineer Agent"""
    
    def __init__(self):
        super().__init__("AGENT_3")
    
    async def process_task(self, task_input):
        from database.models import TaskOutput
        
        # Get creative brief and visual concepts from artifacts
        artifacts = await self.get_artifacts(task_input.artifacts)
        
        logger.info("Generating frontend code based on brief and visual concepts",
                   agent_id=self.agent_id)
        
        # Mock HTML/CSS generation
        frontend_code = {
            "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Productivity Tools</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="logo">ProductivityAI</div>
            <ul class="nav-links">
                <li><a href="#features">Features</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section class="hero">
            <div class="container">
                <h1>Boost Your Productivity with AI</h1>
                <p>Professional-grade AI tools designed for business efficiency</p>
                <button class="cta-button">Get Started</button>
            </div>
        </section>
        
        <section id="features" class="features">
            <div class="container">
                <h2>Key Features</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>Intelligent Automation</h3>
                        <p>Streamline workflows with smart automation</p>
                    </div>
                    <div class="feature-card">
                        <h3>Real-time Analytics</h3>
                        <p>Data-driven insights for better decisions</p>
                    </div>
                    <div class="feature-card">
                        <h3>Team Collaboration</h3>
                        <p>Seamless collaboration tools</p>
                    </div>
                </div>
            </div>
        </section>
    </main>
</body>
</html>""",
            "css": """/* Modern Professional Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    color: #1f2937;
    background-color: #ffffff;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

.header {
    background: #ffffff;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
}

.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2563eb;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    text-decoration: none;
    color: #1f2937;
    font-weight: 500;
    transition: color 0.3s;
}

.nav-links a:hover {
    color: #2563eb;
}

.hero {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    color: white;
    padding: 8rem 0 4rem;
    text-align: center;
    margin-top: 80px;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    font-weight: 700;
}

.hero p {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.cta-button {
    background: #ffffff;
    color: #2563eb;
    padding: 1rem 2rem;
    border: none;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s;
}

.cta-button:hover {
    transform: translateY(-2px);
}

.features {
    padding: 4rem 0;
    background: #f3f4f6;
}

.features h2 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: #1f2937;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    text-align: center;
}

.feature-card h3 {
    color: #2563eb;
    margin-bottom: 1rem;
    font-size: 1.5rem;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem;
    }
    
    .nav-links {
        gap: 1rem;
    }
    
    .container {
        padding: 0 1rem;
    }
}""",
            "metadata": {
                "framework": "vanilla_html_css",
                "responsive": True,
                "accessibility_score": 85,
                "performance_optimized": True,
                "browser_compatibility": ["Chrome", "Firefox", "Safari", "Edge"]
            }
        }
        
        return TaskOutput(
            schema_id="FrontendCode_v1.0",
            payload=frontend_code
        )


class MockQAAgent(BaseAgent):
    """Temporary mock for QA Agent"""
    
    def __init__(self):
        super().__init__("AGENT_4")
    
    async def process_task(self, task_input):
        from database.models import TaskOutput
        
        # Get frontend code from artifacts
        artifacts = await self.get_artifacts(task_input.artifacts)
        frontend_code = artifacts.get("frontend_code", {})
        
        logger.info("Validating frontend code quality and compliance",
                   agent_id=self.agent_id)
        
        # Mock QA validation
        validation_report = {
            "validation_passed": True,
            "overall_score": 92,
            "checks_performed": {
                "html_validation": {
                    "passed": True,
                    "score": 95,
                    "issues": []
                },
                "css_validation": {
                    "passed": True,
                    "score": 90,
                    "issues": ["Minor: Consider adding vendor prefixes for older browser support"]
                },
                "accessibility": {
                    "passed": True,
                    "score": 88,
                    "wcag_level": "AA",
                    "issues": ["Consider adding aria-labels to navigation items"]
                },
                "performance": {
                    "passed": True,
                    "score": 94,
                    "metrics": {
                        "estimated_load_time": "1.2s",
                        "css_size": "2.1KB",
                        "html_size": "1.8KB"
                    }
                },
                "responsive_design": {
                    "passed": True,
                    "score": 95,
                    "breakpoints_tested": ["mobile", "tablet", "desktop"]
                }
            },
            "recommendations": [
                "Add favicon and meta description for SEO",
                "Consider implementing lazy loading for images",
                "Add loading states for interactive elements",
                "Include error handling for form submissions"
            ],
            "compliance_status": {
                "wcag_aa": True,
                "html5_standards": True,
                "css3_standards": True,
                "mobile_friendly": True
            }
        }
        
        return TaskOutput(
            schema_id="ValidationReport_v1.0",
            payload=validation_report
        )


async def main():
    """Main entry point for the agent worker"""
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.WriteLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Initialize agents
    agents: Dict[str, BaseAgent] = {
        "AGENT_1": CreativeDirectorAgent(),
        "AGENT_2": MockVisualDirectorAgent(),
        "AGENT_3": MockFrontendEngineerAgent(),
        "AGENT_4": MockQAAgent()
    }
    
    # Create and start worker
    worker = AgentWorker(agents)
    
    try:
        logger.info("Starting HELIX Agent Worker")
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())