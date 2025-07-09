"""
HTML Renderer for Project HELIX v2.0
Converts PresentationBlueprint to HTML format
"""

import os
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
import structlog

logger = structlog.get_logger(__name__)


class HTMLRenderer:
    """Renders PresentationBlueprint to HTML format using Jinja2 templates"""
    
    def __init__(self, template_dir: str = None):
        """Initialize HTML renderer with template directory"""
        if template_dir is None:
            # Default to templates directory relative to this file
            template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        
        # Create Jinja2 environment with autoescape for security
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        logger.info("HTML Renderer initialized", template_dir=template_dir)
    
    def render_presentation(self, presentation_blueprint: Dict[str, Any]) -> str:
        """
        Render PresentationBlueprint to HTML
        
        Args:
            presentation_blueprint: The presentation blueprint from AGENT_3
            
        Returns:
            HTML string of the rendered presentation
        """
        try:
            # Load the presentation template
            template = self.env.get_template('presentation.html')
            
            # Prepare context for template
            context = {
                'title': self._extract_title(presentation_blueprint),
                'strategic_choice': presentation_blueprint.get('strategic_choice', {}),
                'slides': presentation_blueprint.get('content_sections', []),
                'metadata': presentation_blueprint.get('metadata', {}),
                'total_slides': len(presentation_blueprint.get('content_sections', []))
            }
            
            # Render template with context
            html = template.render(**context)
            
            logger.info("Presentation rendered successfully", 
                       slide_count=context['total_slides'])
            
            return html
            
        except Exception as e:
            logger.error("Failed to render presentation", error=str(e))
            raise
    
    def _extract_title(self, presentation_blueprint: Dict[str, Any]) -> str:
        """Extract presentation title from blueprint"""
        # Try to get title from first section
        sections = presentation_blueprint.get('content_sections', [])
        if sections and 'section_title' in sections[0]:
            return sections[0]['section_title']
        
        # Fallback to metadata title if available
        if 'metadata' in presentation_blueprint and 'title' in presentation_blueprint['metadata']:
            return presentation_blueprint['metadata']['title']
            
        return 'Untitled Presentation'
    
    def render_slide(self, slide: Dict[str, Any]) -> str:
        """
        Render a single slide to HTML
        
        Args:
            slide: Single slide data from presentation blueprint
            
        Returns:
            HTML string for the slide
        """
        try:
            # Determine slide template based on layout type
            layout = slide.get('layout', 'Default')
            template_name = f'slides/{layout.lower()}.html'
            
            # Fall back to default slide template if specific layout not found
            try:
                template = self.env.get_template(template_name)
            except:
                template = self.env.get_template('slides/default.html')
            
            # Render slide
            html = template.render(slide=slide)
            
            return html
            
        except Exception as e:
            logger.error("Failed to render slide", 
                        slide_number=slide.get('slide_number'), 
                        error=str(e))
            raise