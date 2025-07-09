#!/usr/bin/env python3
"""
修复数据库中错误存储为HTML的PresentationBlueprint数据
"""
import asyncio
import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from datetime import datetime


async def fix_presentation_blueprints():
    """修复所有错误格式的PresentationBlueprint artifacts"""
    # 使用环境变量或默认值
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'helix'),
        'user': os.getenv('POSTGRES_USER', 'helix_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'helix_secure_password_2024')
    }
    
    print(f"Connecting to database at {db_config['host']}:{db_config['port']}")
    
    conn = await asyncpg.connect(**db_config)
    
    try:
        # 查找所有PresentationBlueprint artifacts
        query = """
            SELECT id, task_id, payload, created_at
            FROM artifacts
            WHERE schema_id = 'PresentationBlueprint_v1.0'
            ORDER BY created_at DESC
        """
        
        results = await conn.fetch(query)
        
        print(f"Found {len(results)} PresentationBlueprint artifacts")
        
        fixed_count = 0
        for row in results:
            artifact_id = row['id']
            task_id = row['task_id']
            payload = row['payload']
            
            # 检查是否需要修复
            needs_fix = False
            new_payload = None
            
            if isinstance(payload, str):
                if payload.strip().startswith('<!DOCTYPE html>'):
                    print(f"Artifact {artifact_id} (task {task_id}): HTML string found")
                    needs_fix = True
                    # 创建一个有效的blueprint结构
                    new_payload = {
                        "narrative_structure": {
                            "narrative_arc": "Problem-Solution-Benefit framework",
                            "key_story_beats": ["Introduction", "Problem", "Solution", "Benefits", "Conclusion"],
                            "emotional_journey": "From awareness to action",
                            "conflict_resolution": "Addressing user needs through systematic presentation"
                        },
                        "content_sections": [
                            {
                                "section_title": "Opening & Introduction",
                                "content_type": "Title_Slide",
                                "key_messages": ["Welcome", "Overview"],
                                "visual_treatment": "Professional title layout",
                                "interaction_elements": ["Opening statement"]
                            },
                            {
                                "section_title": "Problem Definition",
                                "content_type": "Problem_Statement",
                                "key_messages": ["Current challenges", "Market needs"],
                                "visual_treatment": "Data visualization",
                                "interaction_elements": ["Audience engagement"]
                            },
                            {
                                "section_title": "Solution Presentation",
                                "content_type": "Solution_Overview",
                                "key_messages": ["Key features", "Benefits"],
                                "visual_treatment": "Feature highlights",
                                "interaction_elements": ["Interactive demo"]
                            },
                            {
                                "section_title": "Implementation & Next Steps",
                                "content_type": "Action_Plan",
                                "key_messages": ["Timeline", "Resources"],
                                "visual_treatment": "Roadmap visualization",
                                "interaction_elements": ["Q&A session"]
                            }
                        ],
                        "storytelling_elements": {
                            "hero_journey_stage": "Call to Adventure",
                            "narrative_devices": ["Problem-solution narrative", "Case studies"],
                            "character_personas": ["Target audience", "Stakeholders"],
                            "story_themes": ["Innovation", "Growth", "Success"]
                        },
                        "engagement_strategy": {
                            "attention_hooks": ["Compelling statistics", "Success stories"],
                            "interactive_moments": ["Polls", "Q&A"],
                            "call_to_action_placement": "Final slide",
                            "retention_techniques": ["Key takeaways", "Visual summaries"]
                        },
                        "metadata": {
                            "created_by": "AGENT_3",
                            "version": "1.0",
                            "fixed": True,
                            "fix_reason": "Original payload was HTML string",
                            "fixed_at": datetime.now().isoformat()
                        }
                    }
                else:
                    try:
                        # 尝试解析为JSON
                        parsed = json.loads(payload)
                        if isinstance(parsed, dict):
                            print(f"Artifact {artifact_id}: String contains valid JSON")
                            new_payload = parsed
                            needs_fix = True
                    except:
                        print(f"Artifact {artifact_id}: Invalid string payload")
                        needs_fix = True
                        new_payload = create_default_blueprint()
            
            elif not isinstance(payload, dict):
                print(f"Artifact {artifact_id}: Invalid type {type(payload).__name__}")
                needs_fix = True
                new_payload = create_default_blueprint()
            
            else:
                # 验证dict结构
                required_keys = ["narrative_structure", "content_sections", "storytelling_elements", "engagement_strategy", "metadata"]
                missing_keys = [k for k in required_keys if k not in payload]
                if missing_keys:
                    print(f"Artifact {artifact_id}: Missing keys: {missing_keys}")
                    needs_fix = True
                    new_payload = payload.copy()
                    # 补充缺失的键
                    for key in missing_keys:
                        if key == "content_sections":
                            new_payload[key] = []
                        else:
                            new_payload[key] = {}
            
            # 执行修复
            if needs_fix and new_payload:
                update_query = """
                    UPDATE artifacts
                    SET payload = $1
                    WHERE id = $2
                """
                
                await conn.execute(update_query, json.dumps(new_payload), artifact_id)
                fixed_count += 1
                print(f"✅ Fixed artifact {artifact_id}")
        
        print(f"\n🎉 修复完成！修复了 {fixed_count}/{len(results)} 个artifacts")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await conn.close()


def create_default_blueprint():
    """创建默认的PresentationBlueprint结构"""
    from datetime import datetime
    return {
        "narrative_structure": {
            "narrative_arc": "Default structure",
            "key_story_beats": [],
            "emotional_journey": "To be defined",
            "conflict_resolution": "To be defined"
        },
        "content_sections": [],
        "storytelling_elements": {
            "hero_journey_stage": "Unknown",
            "narrative_devices": [],
            "character_personas": [],
            "story_themes": []
        },
        "engagement_strategy": {
            "attention_hooks": [],
            "interactive_moments": [],
            "call_to_action_placement": "End",
            "retention_techniques": []
        },
        "metadata": {
            "created_by": "AGENT_3",
            "version": "1.0",
            "fixed": True,
            "fix_reason": "Invalid original format",
            "fixed_at": datetime.now().isoformat()
        }
    }


if __name__ == "__main__":
    print("🔧 开始修复PresentationBlueprint格式问题...")
    asyncio.run(fix_presentation_blueprints())