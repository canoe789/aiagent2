"""
Demo script to show HTML generation from PresentationBlueprint
"""

import asyncio
import json
from agents.creative_director import CreativeDirectorAgent
from agents.visual_director import VisualDirectorAgent
from agents.narrative_architect import ChiefNarrativeArchitectAgent
from agents.html_renderer import HTMLRenderer
from database.models import TaskInput
from unittest.mock import AsyncMock, patch


async def generate_html_demo():
    """Generate a demo HTML presentation"""
    
    print("=== HELIX HTML Generation Demo ===\n")
    
    # Mock database operations
    with patch('sdk.agent_sdk.BaseAgent.log_system_event', new_callable=AsyncMock):
        with patch('sdk.agent_sdk.BaseAgent.get_agent_prompt', new_callable=AsyncMock) as mock_prompt:
            with patch('sdk.agent_sdk.BaseAgent.save_task_output', new_callable=AsyncMock):
                
                # Set default prompts
                mock_prompt.return_value = "Default prompt"
                
                # Step 1: Generate Creative Brief
                print("Step 1: Generating Creative Brief...")
                agent1 = CreativeDirectorAgent()
                task_input1 = TaskInput(
                    artifacts=[],
                    params={
                        "chat_input": "Create a presentation for our new AI-powered productivity suite targeting enterprise customers",
                        "session_id": "demo"
                    }
                )
                
                # Process with template fallback (no AI needed for demo)
                result1 = await agent1.process_task(task_input1)
                print(f"✓ Creative Brief generated: {result1.payload['project_overview']['title'][:50]}...")
                
                # Step 2: Generate Visual Explorations
                print("\nStep 2: Generating Visual Explorations...")
                agent2 = VisualDirectorAgent()
                
                with patch.object(agent2, 'get_artifacts', new_callable=AsyncMock) as mock_get_artifacts:
                    mock_get_artifacts.return_value = {
                        "creative_brief": {
                            "payload": result1.payload,
                            "schema_id": "CreativeBrief_v1.0"
                        }
                    }
                    
                    task_input2 = TaskInput(
                        artifacts=[{"name": "creative_brief", "source_task_id": 1}],
                        params={}
                    )
                    
                    result2 = await agent2.process_task(task_input2)
                    print(f"✓ Visual themes generated: {len(result2.payload['visual_themes'])} themes")
                
                # Step 3: Generate Presentation Blueprint
                print("\nStep 3: Generating Presentation Blueprint...")
                agent3 = ChiefNarrativeArchitectAgent()
                
                with patch.object(agent3, 'get_artifacts', new_callable=AsyncMock) as mock_get_artifacts:
                    mock_get_artifacts.return_value = {
                        "creative_brief": {"payload": result1.payload, "schema_id": "CreativeBrief_v1.0"},
                        "visual_explorations": {"payload": result2.payload, "schema_id": "VisualExplorations_v1.0"}
                    }
                    
                    task_input3 = TaskInput(
                        artifacts=[
                            {"name": "creative_brief", "source_task_id": 1},
                            {"name": "visual_explorations", "source_task_id": 2}
                        ],
                        params={}
                    )
                    
                    result3 = await agent3.process_task(task_input3)
                    print(f"✓ Presentation blueprint generated: {len(result3.payload['presentation_blueprint'])} slides")
                
                # Step 4: Render to HTML
                print("\nStep 4: Rendering to HTML...")
                renderer = HTMLRenderer()
                html = renderer.render_presentation(result3.payload)
                
                # Save HTML to file
                output_file = "demo_presentation.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                print(f"✓ HTML generated successfully!")
                print(f"\n📄 Output saved to: {output_file}")
                print(f"📊 Total size: {len(html):,} bytes")
                
                # Display summary
                print("\n=== Generation Summary ===")
                print(f"Theme: {result3.payload['strategic_choice']['chosen_theme_name']}")
                print(f"Framework: {result3.payload['strategic_choice']['chosen_narrative_framework']}")
                print(f"Slides: {len(result3.payload['presentation_blueprint'])}")
                print(f"Confidence: {result3.payload['metadata']['confidence_score']:.2f}")
                
                return output_file


if __name__ == "__main__":
    # Run the demo
    output = asyncio.run(generate_html_demo())
    print(f"\n✅ Demo complete! Open {output} in your browser to view the presentation.")