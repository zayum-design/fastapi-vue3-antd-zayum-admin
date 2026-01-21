#!/bin/bash

# 后端工具模块 - 后端部署相关函数

# 加载配置
source "$(dirname "$0")/config.sh"

# 部署后端
deploy_backend() {
    echo -e "${BLUE}🚀 开始部署后端系统...${NC}"
    echo -e "${BLUE}==========================================${NC}"
    
    if [ ! -d "$BACKEND_DIR" ]; then
        echo -e "${RED}❌ 后端目录 $BACKEND_DIR 不存在${NC}"
        return 1
    fi
    
    if [ ! -f "$BACKEND_DIR/install.sh" ]; then
        echo -e "${RED}❌ 后端安装脚本 $BACKEND_DIR/install.sh 不存在${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}执行后端安装脚本...${NC}"
    cd "$BACKEND_DIR"
    chmod +x install.sh
    
    # 检查是否已安装
    if [ -f "install.lock" ]; then
        echo -e "${RED}❌ 后端系统已安装，检测到 install.lock 文件${NC}"
        echo -e "${YELLOW}📁 install.lock 文件位置: $(pwd)/install.lock${NC}"
        echo -e "${YELLOW}📄 install.lock 文件内容:${NC}"
        cat install.lock
        echo ""
        echo -e "${RED}如需重新安装，请先删除 install.lock 文件:${NC}"
        echo -e "${YELLOW}  rm -f $(pwd)/install.lock${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
    
    # 执行安装脚本
    ./install.sh
    local backend_result=$?
    
    # 验证安装是否成功
    if [ $backend_result -eq 0 ]; then
        # 检查 install.lock 文件是否已创建
        if [ -f "install.lock" ]; then
            echo -e "${GREEN}✅ 后端部署成功 - install.lock 文件已创建${NC}"
            echo -e "${YELLOW}📁 install.lock 文件位置: $(pwd)/install.lock${NC}"
            
            # 显示 install.lock 文件内容
            echo -e "${BLUE}📄 install.lock 文件内容:${NC}"
            cat install.lock
        else
            echo -e "${YELLOW}⚠️  后端安装脚本执行成功，但未检测到 install.lock 文件${NC}"
            echo -e "${YELLOW}手动创建 install.lock 文件...${NC}"
            echo "Installation completed by deploy script at: $(date)" > install.lock
            echo -e "${GREEN}✅ 已手动创建 install.lock 文件${NC}"
        fi
    else
        echo -e "${RED}❌ 后端部署失败${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
    return 0
}

# 显示后端部署信息
show_backend_info() {
    echo -e "${YELLOW}📊 后端服务信息：${NC}"
    echo "后端 API 地址: http://localhost:8000"
    echo "Swagger 文档: http://localhost:8000/docs"
    echo "后端目录: $BACKEND_DIR"
    echo ""
    echo -e "${YELLOW}🔧 后端管理命令：${NC}"
    echo "停止后端服务: cd $BACKEND_DIR && kill \$(cat .backend_pid)"
    echo "重新启动后端: cd $BACKEND_DIR && ./start.sh"
}
