#!/bin/bash

# 开发者模式启动脚本 - 同时启动前后端
# 用法: ./dev-start.sh [选项]
# 选项:
#   start   启动前后端服务（默认）
#   stop    停止所有服务
#   restart 重启所有服务
#   status  查看服务状态
#   help    显示帮助信息

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend-fastapi-app"
FRONTEND_DIR="$ROOT_DIR/frontend-vue-app"

# PID文件路径
BACKEND_PID_FILE="$ROOT_DIR/.backend_dev.pid"
FRONTEND_PID_FILE="$ROOT_DIR/.frontend_dev.pid"
LOG_DIR="$ROOT_DIR/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 函数：显示帮助信息
show_help() {
    echo -e "${BLUE}FastAPI + Vue3 栈鱼Admin 开发者模式启动脚本${NC}"
    echo ""
    echo -e "${YELLOW}用法: $0 [命令]${NC}"
    echo ""
    echo -e "${YELLOW}命令:${NC}"
    echo "  start    启动前后端服务（默认）"
    echo "  stop     停止所有服务"
    echo "  restart  重启所有服务"
    echo "  status   查看服务状态"
    echo "  help     显示此帮助信息"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo "  $0              # 启动前后端服务"
    echo "  $0 start        # 启动前后端服务"
    echo "  $0 stop         # 停止所有服务"
    echo "  $0 status       # 查看服务状态"
    echo ""
    echo -e "${YELLOW}访问地址:${NC}"
    echo "  前端应用: http://localhost:5173"
    echo "  后端API:  http://localhost:8000"
    echo "  Swagger文档: http://localhost:8000/docs"
    echo ""
}

# 函数：检查依赖
check_dependencies() {
    echo -e "${BLUE}检查依赖...${NC}"
    
    # 检查后端依赖
    if [ ! -d "$BACKEND_DIR/.venv" ] && [ ! -f "$BACKEND_DIR/requirements.txt" ]; then
        echo -e "${YELLOW}⚠  后端依赖未安装，请先运行后端安装脚本:${NC}"
        echo -e "  cd $BACKEND_DIR && ./install.sh"
        return 1
    fi
    
    # 检查前端依赖
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        echo -e "${YELLOW}⚠  前端依赖未安装，正在安装...${NC}"
        cd "$FRONTEND_DIR" || return 1
        if npm install; then
            echo -e "${GREEN}✓ 前端依赖安装成功${NC}"
        else
            echo -e "${RED}✗ 前端依赖安装失败${NC}"
            return 1
        fi
        cd "$ROOT_DIR" || return 1
    else
        echo -e "${GREEN}✓ 前端依赖已安装${NC}"
    fi
    
    return 0
}

# 函数：启动后端服务
start_backend() {
    echo -e "${BLUE}启动后端服务...${NC}"
    
    # 检查是否已运行
    if [ -f "$BACKEND_PID_FILE" ] && ps -p "$(cat "$BACKEND_PID_FILE")" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠  后端服务已在运行 (PID: $(cat "$BACKEND_PID_FILE"))${NC}"
        return 0
    fi
    
    cd "$BACKEND_DIR" || return 1
    
    # 激活Conda环境
    echo -e "${YELLOW}激活Conda环境: ZayumAdmin-3.13.3${NC}"
    # 注意：在脚本中激活conda环境需要特殊处理
    # 使用conda run来执行命令
    echo -e "${YELLOW}启动 FastAPI 后端 (uvicorn)...${NC}"
    conda run -n ZayumAdmin-3.13.3 uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    
    echo $BACKEND_PID > "$BACKEND_PID_FILE"
    echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    echo -e "${GREEN}  日志文件: $LOG_DIR/backend.log${NC}"
    echo -e "${GREEN}  使用Conda环境: ZayumAdmin-3.13.3${NC}"
    
    cd "$ROOT_DIR" || return 1
    return 0
}

# 函数：启动前端服务
start_frontend() {
    echo -e "${BLUE}启动前端服务...${NC}"
    
    # 检查是否已运行
    if [ -f "$FRONTEND_PID_FILE" ] && ps -p "$(cat "$FRONTEND_PID_FILE")" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠  前端服务已在运行 (PID: $(cat "$FRONTEND_PID_FILE"))${NC}"
        return 0
    fi
    
    cd "$FRONTEND_DIR" || return 1
    
    # 检查环境配置
    if [ ! -f ".env.development" ]; then
        echo -e "${YELLOW}⚠  前端开发环境配置不存在，使用默认配置...${NC}"
        if [ -f ".env.example" ]; then
            cp .env.example .env.development
            echo -e "${GREEN}✓ 已创建 .env.development 文件${NC}"
        fi
    fi
    
    # 启动前端服务
    echo -e "${YELLOW}启动 Vue 前端开发服务器...${NC}"
    npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
    echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
    echo -e "${GREEN}  日志文件: $LOG_DIR/frontend.log${NC}"
    
    cd "$ROOT_DIR" || return 1
    return 0
}

# 函数：停止后端服务
stop_backend() {
    echo -e "${BLUE}停止后端服务...${NC}"
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            kill "$BACKEND_PID" 2>/dev/null
            sleep 2
            if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
                kill -9 "$BACKEND_PID" 2>/dev/null
                echo -e "${YELLOW}⚠  强制停止后端服务 (PID: $BACKEND_PID)${NC}"
            else
                echo -e "${GREEN}✓ 后端服务已停止 (PID: $BACKEND_PID)${NC}"
            fi
        else
            echo -e "${YELLOW}⚠  后端服务未运行 (PID: $BACKEND_PID)${NC}"
        fi
        rm -f "$BACKEND_PID_FILE"
    else
        echo -e "${YELLOW}⚠  后端PID文件不存在${NC}"
    fi
    
    # 额外检查并杀死可能的uvicorn进程
    PIDS=$(ps aux | grep "uvicorn app.main:app" | grep -v grep | awk '{print $2}')
    if [ -n "$PIDS" ]; then
        echo -e "${YELLOW}⚠  发现残留的uvicorn进程，正在清理...${NC}"
        echo "$PIDS" | xargs kill -9 2>/dev/null
    fi
    
    return 0
}

# 函数：停止前端服务
stop_frontend() {
    echo -e "${BLUE}停止前端服务...${NC}"
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            kill "$FRONTEND_PID" 2>/dev/null
            sleep 2
            if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
                kill -9 "$FRONTEND_PID" 2>/dev/null
                echo -e "${YELLOW}⚠  强制停止前端服务 (PID: $FRONTEND_PID)${NC}"
            else
                echo -e "${GREEN}✓ 前端服务已停止 (PID: $FRONTEND_PID)${NC}"
            fi
        else
            echo -e "${YELLOW}⚠  前端服务未运行 (PID: $FRONTEND_PID)${NC}"
        fi
        rm -f "$FRONTEND_PID_FILE"
    else
        echo -e "${YELLOW}⚠  前端PID文件不存在${NC}"
    fi
    
    # 额外检查并杀死可能的npm/vite进程
    PIDS=$(ps aux | grep -E "(npm run dev|vite)" | grep -v grep | awk '{print $2}')
    if [ -n "$PIDS" ]; then
        echo -e "${YELLOW}⚠  发现残留的前端进程，正在清理...${NC}"
        echo "$PIDS" | xargs kill -9 2>/dev/null
    fi
    
    return 0
}

# 函数：检查服务状态
check_status() {
    echo -e "${BLUE}服务状态检查...${NC}"
    
    # 检查后端
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 后端服务运行中 (PID: $BACKEND_PID)${NC}"
            echo -e "  访问地址: http://localhost:8000"
            echo -e "  Swagger文档: http://localhost:8000/docs"
        else
            echo -e "${RED}✗ 后端服务已停止 (PID: $BACKEND_PID)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠  后端服务未启动${NC}"
    fi
    
    # 检查前端
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 前端服务运行中 (PID: $FRONTEND_PID)${NC}"
            echo -e "  访问地址: http://localhost:5173"
        else
            echo -e "${RED}✗ 前端服务已停止 (PID: $FRONTEND_PID)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠  前端服务未启动${NC}"
    fi
    
    # 显示日志文件信息
    echo ""
    echo -e "${BLUE}日志文件:${NC}"
    if [ -f "$LOG_DIR/backend.log" ]; then
        echo -e "  后端日志: $LOG_DIR/backend.log ($(wc -l < "$LOG_DIR/backend.log") 行)"
    else
        echo -e "  后端日志: 不存在"
    fi
    
    if [ -f "$LOG_DIR/frontend.log" ]; then
        echo -e "  前端日志: $LOG_DIR/frontend.log ($(wc -l < "$LOG_DIR/frontend.log") 行)"
    else
        echo -e "  前端日志: 不存在"
    fi
    
    return 0
}

# 函数：启动所有服务
start_all() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   FastAPI + Vue3 开发者模式启动${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # 检查依赖
    if ! check_dependencies; then
        echo -e "${RED}✗ 依赖检查失败，无法启动服务${NC}"
        exit 1
    fi
    
    # 启动后端
    if ! start_backend; then
        echo -e "${RED}✗ 后端服务启动失败${NC}"
        exit 1
    fi
    
    # 等待后端启动
    echo -e "${YELLOW}等待后端服务启动...${NC}"
    sleep 3
    
    # 启动前端
    if ! start_frontend; then
        echo -e "${RED}✗ 前端服务启动失败${NC}"
        # 停止已启动的后端
        stop_backend
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}       所有服务已成功启动！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}访问地址:${NC}"
    echo -e "  前端应用: ${GREEN}http://localhost:5173${NC}"
    echo -e "  后端API:  ${GREEN}http://localhost:8000${NC}"
    echo -e "  Swagger文档: ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}默认管理员账号:${NC}"
    echo -e "  用户名: ${GREEN}admin${NC}"
    echo -e "  密码:   ${GREEN}Admin@888${NC}"
    echo ""
    echo -e "${YELLOW}日志文件:${NC}"
    echo -e "  后端: $LOG_DIR/backend.log"
    echo -e "  前端: $LOG_DIR/frontend.log"
    echo ""
    echo -e "${YELLOW}停止服务:${NC}"
    echo -e "  使用命令: ${GREEN}./dev-start.sh stop${NC}"
    echo ""
    
    # 显示实时日志提示
    echo -e "${BLUE}提示:${NC}"
    echo -e "  查看后端日志: ${GREEN}tail -f $LOG_DIR/backend.log${NC}"
    echo -e "  查看前端日志: ${GREEN}tail -f $LOG_DIR/frontend.log${NC}"
    
    return 0
}

# 函数：停止所有服务
stop_all() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}       停止所有服务${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    stop_frontend
    stop_backend
    
    echo ""
    echo -e "${GREEN}✓ 所有服务已停止${NC}"
    
    return 0
}

# 函数：重启所有服务
restart_all() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}       重启所有服务${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    stop_all
    sleep 2
    start_all
    
    return 0
}

# 主程序
COMMAND=${1:-start}

case $COMMAND in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        check_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}错误: 未知命令 '$COMMAND'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

exit 0
