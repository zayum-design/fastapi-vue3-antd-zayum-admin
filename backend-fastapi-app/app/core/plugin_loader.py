import importlib
import json
import re
import shutil
import zipfile
from pathlib import Path
import os
from fastapi import HTTPException, APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
# from app.router.download import download_service
import logging
from datetime import datetime  # Correct import for datetime

# Set up logging for the PluginLoader class
logger = logging.getLogger(__name__)

class PluginLoader:
    def __init__(self, plugin_dir: Path):
        logger.info(f"初始化插件加载器，插件目录: {plugin_dir}")
        self.plugin_dir = plugin_dir
        self.active_plugins = {}

    async def install_from_url(self, url: str):
        """完整安装流程""" 
        temp_file = None
        try:
            logger.info(f"开始下载插件包: {url}")
            
            # # 1. 下载插件包
            # temp_file = await download_service.download_plugin(url)
            # logger.info(f"插件包下载完成: {temp_file}")
            
            # # 2. 验证插件包
            # if not await self._validate_plugin(temp_file):
            #     raise HTTPException(400, "插件验证失败")
            
            # # 3. 安装插件
            # plugin_id = self._extract_plugin_id(url)
            # logger.info(f"开始安装插件: {plugin_id}")
            # return await self._install_from_file(temp_file, plugin_id)
        
        except Exception as e:
            logger.error(f"安装插件时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"安装失败: {str(e)}")
        
        finally:
            if temp_file:
                # await download_service.cleanup(temp_file)
                logger.info(f"临时文件清理完成: {temp_file}")

    async def _validate_plugin(self, zip_path: Path) -> bool:
        """验证插件包的有效性"""
        try:
            logger.info(f"正在验证插件包: {zip_path}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check if the zip file contains expected files or folders (for example, 'plugin.json' or any required structure)
                required_file = "plugin.json"  # Example: a required file in the plugin structure
                if required_file not in zip_ref.namelist():
                    logger.warning(f"插件包缺少必要的文件: {required_file}")
                    return False
            return True
        except zipfile.BadZipFile:
            logger.error(f"插件包不是有效的ZIP文件: {zip_path}")
            return False

    def _extract_plugin_id(self, url: str) -> str:
        """从插件的 URL 或文件名中提取插件 ID"""
        filename = os.path.basename(url)
        plugin_id, _ = os.path.splitext(filename)  # Extract filename without extension
        logger.info(f"从URL中提取插件ID: {plugin_id}")
        return plugin_id

    async def _install_from_file(self, zip_path: Path, plugin_id: str):
        """从本地文件安装"""
        extract_path = self.plugin_dir / plugin_id
        extract_path.mkdir(exist_ok=True)
        logger.info(f"正在安装插件到: {extract_path}")

        with zipfile.ZipFile(zip_path) as zip_ref:
            zip_ref.extractall(extract_path)
        
        # 安装后端依赖
        req_file = extract_path / "backend" / "requirements.txt"
        if req_file.exists():
            import subprocess
            try:
                result = subprocess.run(
                    ['pip', 'install', '-r', str(req_file)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"后端依赖安装成功: {result.stdout}")
            except subprocess.CalledProcessError as e:
                logger.error(f"后端依赖安装失败: {e.stderr}")
                raise RuntimeError(f"后端依赖安装失败: {e.stderr}")
        
        # 安装前端依赖
        package_json = extract_path / "frontend" / "package.json"
        if package_json.exists():
            import subprocess
            try:
                result = subprocess.run(
                    ['npm', 'install', '--prefix', str(extract_path / "frontend")],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"前端依赖安装成功: {result.stdout}")
            except subprocess.CalledProcessError as e:
                logger.error(f"前端依赖安装失败: {e.stderr}")
                raise RuntimeError(f"前端依赖安装失败: {e.stderr}")

        return {"status": "success", "message": "插件安装成功"}

    def list_plugins(self):
        return [
            {
                **manifest,
                "routes": self._get_plugin_routes(plugin_id, manifest)
            }
            for plugin_id, manifest in self.active_plugins.items()
        ]
    
    def _get_plugin_routes(self, plugin_id, manifest):
        """获取插件路由信息"""
        # 从manifest中获取组件列表
        components = manifest.get("component", [])
        if not components:
            components = manifest.get("components", [])
        
        # 如果manifest中已经定义了routes，直接使用
        if "routes" in manifest and isinstance(manifest["routes"], list):
            return manifest["routes"]
        
        # 根据组件自动生成路由
        routes = []
        for component_name in components:
            # 根据组件名生成路径和标题
            path_segment = component_name
            if component_name.endswith("Records"):
                path_segment = "records"
                title = "记录"
                icon = "list"
            elif component_name.endswith("Settings"):
                path_segment = "settings"
                title = "设置"
                icon = "settings"
            else:
                title = component_name
                icon = "plugin"
            
            # 创建路由配置
            route = {
                "path": f"/plugins/{plugin_id}/{path_segment.lower()}",
                "name": f"{plugin_id}-{path_segment.lower()}",
                "component": component_name,
                "meta": {
                    "title": f"{manifest.get('name', plugin_id)}{title}",
                    "icon": icon
                }
            }
            routes.append(route)
        
        return routes

    async def _load_plugin(self, plugin_path: Path, app: FastAPI):
        """加载插件主逻辑"""
        try:
            logger.info(f"正在加载插件: {plugin_path}")
            
            # 1. 加载并验证manifest文件
            manifest_path = plugin_path / "manifest.json"
            if not manifest_path.exists():
                raise HTTPException(400, "插件缺少manifest文件")
            
            manifest = json.loads(manifest_path.read_text())
            self._validate_manifest(manifest)
            
            plugin_id = manifest["id"]
            logger.info(f"正在加载插件: {plugin_id} ({manifest['version']})")

            # 2. 检查系统依赖
            self._check_dependencies(manifest.get("dependencies", {}))

            # 3. 注册后端路由
            if "backend" in manifest:
                await self._load_backend(plugin_path, manifest["backend"], app, plugin_id)

            # 4. 注册前端资源
            if "frontend" in manifest:
                self._register_frontend_assets(plugin_path, manifest["frontend"], app)

            # 5. 记录激活插件
            self.active_plugins[plugin_id] = {
                **manifest,
                "status": "active",
                "loaded_at": datetime.now().isoformat()
            }

            logger.info(f"插件加载成功: {plugin_id}")
            return {"status": "active", "plugin": manifest}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"插件加载失败: {str(e)}")
            # await self._cleanup_failed_plugin(plugin_path)
            raise HTTPException(500, f"插件加载失败: {str(e)}") from e

    def _validate_manifest(self, manifest: dict):
        """验证manifest文件完整性"""
        required_fields = ["id", "name", "version", "description"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"缺少必要字段: {field}")

        if not re.match(r"^[a-z0-9-]+$", manifest["id"]):
            raise ValueError("插件ID只能包含小写字母、数字和连字符")

    def _check_dependencies(self, dependencies: dict):
        """检查插件依赖"""
        core_version = dependencies.get("core", "1.0.0")
        current_version = "1.2.0"  # 应从系统配置获取实际版本
        
        if not self._version_match(current_version, core_version):
            raise ValueError(f"核心系统版本不兼容 (需要 {core_version}, 当前 {current_version})")

    def _version_match(self, current: str, required: str) -> bool:
        """语义化版本检查"""
        # 实现版本比较逻辑
        return True  # 暂时跳过实际实现

    async def _load_backend(self, plugin_path: Path, backend_config: dict, app: FastAPI, plugin_id: str):
        """加载后端模块"""
        backend_entry = plugin_path / backend_config["entry"]
        if not backend_entry.exists():
            raise FileNotFoundError(f"后端入口文件不存在: {backend_entry}")

        spec = importlib.util.spec_from_file_location(f"{plugin_id}_backend", backend_entry)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)

        # 支持两种插件注册方式
        if hasattr(plugin_module, "get_plugin_app"):
            # 新方式：通过get_plugin_app函数获取子应用
            plugin_app = plugin_module.get_plugin_app()
            api_prefix = backend_config.get("api_prefix", f"/api/{plugin_id}")
            app.mount(api_prefix, plugin_app)
            logger.info(f"API路由注册成功: {api_prefix}")
        elif hasattr(plugin_module, "router") and isinstance(plugin_module.router, APIRouter):
            # 旧方式：直接使用router
            api_prefix = backend_config.get("api_prefix", f"/plugins/{plugin_id}")
            app.include_router(plugin_module.router, prefix=api_prefix)
            logger.info(f"API路由注册成功: {api_prefix}")
        else:
            logger.warning("插件未提供有效路由")

    def _register_frontend_assets(self, plugin_path: Path, frontend_config: dict, app: FastAPI):
        """注册前端静态资源"""
        # 注册静态资源
        assets_dir = plugin_path / frontend_config["assets_dir"]
        if assets_dir.exists():
            app.mount(f"/plugins-assets/{frontend_config['entry']}", StaticFiles(directory=assets_dir))
            logger.info(f"前端资源已挂载: {assets_dir}")

        # 注册模块联邦入口文件
        if "module_federation" in frontend_config:
            mf_config = frontend_config["module_federation"]
            remote_entry = plugin_path / mf_config["remote_entry"]
            if remote_entry.exists():
                app.mount(
                    f"/plugins/{frontend_config['entry']}/remoteEntry.js",
                    StaticFiles(directory=remote_entry.parent)
                )
                logger.info(f"模块联邦入口文件已注册: {remote_entry}")

        # 注册manifest.json访问路由
        manifest_path = plugin_path / "manifest.json"
        if manifest_path.exists():
            app.mount(
                f"/plugins/{frontend_config['entry']}/manifest.json",
                StaticFiles(directory=manifest_path.parent)
            )
            logger.info(f"manifest.json访问路由已注册")

    async def _cleanup_failed_plugin(self, plugin_path: Path):
        """清理加载失败的插件"""
        try:
            if plugin_path.exists():
                # 1. 创建备份目录
                backup_dir = Path("plugin_backups")
                backup_dir.mkdir(exist_ok=True)
                
                # 2. 生成备份路径
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"{plugin_path.name}_{timestamp}"
                
                # 3. 移动而不是直接删除
                # shutil.move(str(plugin_path), str(backup_path))
                logger.warning(f"已将失败插件移动到备份目录: {backup_path}")
                
                # 4. 记录详细日志
                logger.info(
                    f"插件备份详情: \n"
                    f"  - 原始路径: {str(plugin_path)}\n"
                    f"  - 备份路径: {str(backup_path)}\n"
                    f"  - 时间戳: {timestamp}"
                )
        except Exception as e:
            logger.error(f"插件清理失败: {str(e)}", exc_info=True)
            raise HTTPException(500, f"插件清理失败: {str(e)}")
