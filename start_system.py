"""
HELIX系统启动脚本
同时启动API服务器和Orchestrator
"""

import asyncio
import uvicorn
import sys
import signal
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.orchestrator.main import HelixOrchestrator
from src.database.connection import DatabaseManager
from src.agents.worker import main as worker_main


class SystemManager:
    def __init__(self):
        self.orchestrator = None
        self.running = False
        # 为 Orchestrator 创建独立的数据库管理器，避免事件循环冲突
        self.orchestrator_db = DatabaseManager()
        
    async def start_orchestrator(self):
        """启动Orchestrator"""
        print("🚀 启动 HELIX Orchestrator...")
        self.orchestrator = HelixOrchestrator()
        try:
            await self.orchestrator.start()
        except Exception as e:
            print(f"❌ Orchestrator 启动失败: {e}")
            
    async def start_worker(self):
        """启动Agent Worker"""
        print("🤖 启动 HELIX Agent Worker...")
        try:
            await worker_main()
        except Exception as e:
            print(f"❌ Agent Worker 启动失败: {e}")
            
    def start_api_server(self):
        """启动API服务器"""
        print("🌐 启动 FastAPI 服务器...")
        
        # SOP兼容：优先使用环境变量端口，支持动态端口管理
        port = int(os.getenv("API_PORT", 8000))
        host = os.getenv("API_HOST", "0.0.0.0")
        
        print(f"📍 API服务器配置: {host}:{port}")
        print(f"🔍 健康检查端点: http://localhost:{port}/api/v1/health")
        print(f"📚 API文档: http://localhost:{port}/docs")
        
        # 配置uvicorn
        config = uvicorn.Config(
            "src.api.main:app",
            host=host,
            port=port,
            reload=False,  # 生产环境关闭reload
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        return server.run()
        
    async def start_api_server_async(self):
        """异步启动API服务器"""
        print("🌐 启动 FastAPI 服务器...")
        
        # SOP兼容：优先使用环境变量端口，支持动态端口管理  
        port = int(os.getenv("API_PORT", 8000))
        host = os.getenv("API_HOST", "0.0.0.0")
        
        print(f"📍 API服务器配置: {host}:{port}")
        print(f"🔍 健康检查端点: http://localhost:{port}/api/v1/health")
        print(f"📚 API文档: http://localhost:{port}/docs")
        
        # 配置uvicorn
        config = uvicorn.Config(
            "src.api.main:app",
            host=host,
            port=port,
            reload=False,  # 生产环境关闭reload
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    async def start_system(self):
        """同时启动API服务器和Orchestrator"""
        print("=" * 50)
        print("🔥 HELIX v2.0 系统启动中...")
        print("=" * 50)
        
        self.running = True
        
        try:
            # 启动Orchestrator
            orchestrator_task = asyncio.create_task(
                self.start_orchestrator()
            )
            
            # 启动Agent Worker
            worker_task = asyncio.create_task(
                self.start_worker()
            )
            
            # 给系统核心组件一点时间启动
            await asyncio.sleep(2)
            
            # 启动API服务器
            api_task = asyncio.create_task(
                self.start_api_server_async()
            )
            
            # 等待所有任务完成
            await asyncio.gather(orchestrator_task, worker_task, api_task)
            
        except KeyboardInterrupt:
            print("\n⏹️  收到中断信号，正在关闭系统...")
            await self.shutdown()
        except Exception as e:
            print(f"❌ 系统运行错误: {e}")
            await self.shutdown()
                
    async def shutdown(self):
        """优雅关闭系统"""
        print("🛑 正在关闭 HELIX 系统...")
        self.running = False
        
        if self.orchestrator:
            try:
                await self.orchestrator.stop()
                print("✅ Orchestrator 已关闭")
            except Exception as e:
                print(f"⚠️  Orchestrator 关闭时出现错误: {e}")
        
        print("✅ 系统已完全关闭")


def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n收到信号 {signum}，准备关闭...")
    sys.exit(0)


async def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建系统管理器
    system_manager = SystemManager()
    
    try:
        await system_manager.start_system()
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"系统启动失败: {e}")
    finally:
        await system_manager.shutdown()


if __name__ == "__main__":
    print("""
    ██╗  ██╗███████╗██╗     ██╗██╗  ██╗    ██╗   ██╗██████╗ 
    ██║  ██║██╔════╝██║     ██║╚██╗██╔╝    ██║   ██║╚════██╗
    ███████║█████╗  ██║     ██║ ╚███╔╝     ██║   ██║ █████╔╝
    ██╔══██║██╔══╝  ██║     ██║ ██╔██╗     ╚██╗ ██╔╝██╔═══╝ 
    ██║  ██║███████╗███████╗██║██╔╝ ██╗     ╚████╔╝ ███████╗
    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═╝      ╚═══╝  ╚══════╝
    
    AI驱动的自动化创意生产系统
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见!")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)