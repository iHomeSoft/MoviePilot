import uvicorn as uvicorn
from fastapi import FastAPI
from uvicorn import Config

from app.api.apiv1 import api_router
from app.command import Command
from app.core.config import settings
from app.core.module import ModuleManager
from app.core.plugin import PluginManager
from app.db.init import init_db, update_db
from app.helper.display import DisplayHelper
from app.helper.sites import SitesHelper
from app.scheduler import Scheduler

# App
App = FastAPI(title=settings.PROJECT_NAME,
              openapi_url=f"{settings.API_V1_STR}/openapi.json")

# API路由
App.include_router(api_router, prefix=settings.API_V1_STR)

# uvicorn服务
Server = uvicorn.Server(Config(App, host=settings.HOST, port=settings.PORT, reload=settings.RELOAD))


@App.on_event("shutdown")
def shutdown_server():
    """
    服务关闭
    """
    # 停止定时服务
    Scheduler().stop()
    # 停止插件
    PluginManager().stop()
    # 停止模块
    ModuleManager().stop()
    # 停止事件消费
    Command().stop()
    # 停止虚拟显示
    DisplayHelper().stop()


@App.on_event("startup")
def start_module():
    """
    启动模块
    """
    # 虚伪显示
    DisplayHelper()
    # 加载模块
    ModuleManager()
    # 加载插件
    PluginManager()
    # 启动定时服务
    Scheduler()
    # 启动事件消费
    Command()
    # 站点管理
    SitesHelper()


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    # 更新数据库
    update_db()
    # 启动服务
    Server.run()
