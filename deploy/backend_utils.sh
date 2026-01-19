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
    ./install.sh
    local backend_result=$?
    cd "$PROJECT_ROOT"
    
    if [ $backend_result -eq 0 ]; then
        echo -e "${GREEN}✅ 后端部署成功${NC}"
        return 0
    else
        echo -e "${RED}❌ 后端部署失败${NC}"
        return 1
    fi
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
