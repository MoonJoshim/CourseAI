#!/bin/bash

# 프로젝트 전체 실행 스크립트
# Google Cloud VM에서 백엔드와 프론트엔드를 실행합니다.

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# VM 정보
VM_USER="seohyun"
VM_HOST="34.58.143.2"
SSH_KEY="./moonjoshim"
PROJECT_DIR="~"

# SSH 명령 실행 헬퍼 함수
run_ssh() {
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $VM_USER@$VM_HOST -i $SSH_KEY "$1"
}

# 서버 시작 확인 함수
check_port() {
    local port=$1
    local service=$2
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if run_ssh "ss -tlnp | grep -q ':$port'"; then
            echo -e "${GREEN}✅ $service가 포트 $port에서 실행 중입니다.${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}❌ $service 시작 실패 (포트 $port 확인 실패)${NC}"
    return 1
}

echo -e "${BLUE}🚀 프로젝트 전체 실행 스크립트${NC}"
echo "=================================="

# SSH 연결 테스트
echo -e "${BLUE}📡 SSH 연결 테스트...${NC}"
if ! run_ssh "echo 'SSH 연결 성공'" > /dev/null 2>&1; then
    echo -e "${RED}❌ SSH 연결 실패${NC}"
    echo "VM이 실행 중인지 확인하세요: $VM_HOST"
    exit 1
fi
echo -e "${GREEN}✅ SSH 연결 성공${NC}"

# 기존 프로세스 종료
echo -e "${YELLOW}🛑 기존 프로세스 종료 중...${NC}"
run_ssh "
    pkill -f 'python.*lecture_api.py' || true
    pkill -f 'serve.*build' || true
    pkill -f 'npx serve' || true
    sleep 2
"
echo -e "${GREEN}✅ 기존 프로세스 종료 완료${NC}"

# MongoDB 시작
echo -e "${BLUE}🗄️ MongoDB 컨테이너 시작 중...${NC}"
if run_ssh "docker ps | grep -q crawller-mongo"; then
    echo -e "${GREEN}✅ MongoDB가 이미 실행 중입니다.${NC}"
else
    if run_ssh "cd $PROJECT_DIR && docker compose up -d"; then
        echo -e "${GREEN}✅ MongoDB 컨테이너 시작됨${NC}"
        sleep 2
    else
        echo -e "${YELLOW}⚠️  MongoDB 시작 중 오류가 발생했습니다. 계속 진행합니다.${NC}"
    fi
fi

# 백엔드 시작
echo -e "${BLUE}🔧 백엔드 API 서버 시작 중...${NC}"
run_ssh "
    cd $PROJECT_DIR && 
    source venv/bin/activate && 
    nohup python backend/api/lecture_api.py > api.log 2>&1 &
    sleep 1
    echo '백엔드 프로세스 시작됨'
"

# 백엔드 시작 확인
if check_port 5002 "백엔드 API 서버"; then
    echo -e "${GREEN}✅ 백엔드 서버가 성공적으로 시작되었습니다.${NC}"
else
    echo -e "${YELLOW}⚠️  백엔드 로그 확인 중...${NC}"
    run_ssh "tail -20 ~/api.log"
    echo -e "${RED}❌ 백엔드 시작 실패${NC}"
    exit 1
fi

# 프론트엔드 시작
echo -e "${BLUE}🎨 프론트엔드 서버 시작 중...${NC}"
run_ssh "
    cd ~/frontend/react-app && 
    nohup npx serve -s build -l 3000 > ~/frontend.log 2>&1 &
    sleep 1
    echo '프론트엔드 프로세스 시작됨'
"

# 프론트엔드 시작 확인
if check_port 3000 "프론트엔드 서버"; then
    echo -e "${GREEN}✅ 프론트엔드 서버가 성공적으로 시작되었습니다.${NC}"
else
    echo -e "${YELLOW}⚠️  프론트엔드 로그 확인 중...${NC}"
    run_ssh "tail -20 ~/frontend.log 2>&1 || echo '로그 파일 없음'"
    echo -e "${RED}❌ 프론트엔드 시작 실패${NC}"
    exit 1
fi

# 최종 상태 확인
echo ""
echo -e "${BLUE}📊 최종 서버 상태 확인 중...${NC}"
echo "=================================="
run_ssh "
    echo '=== 포트 상태 ==='
    ss -tlnp | grep -E ':(3000|5002)' || echo '포트 정보를 찾을 수 없습니다.'
    echo ''
    echo '=== 프로세스 상태 ==='
    ps aux | grep -E '(python.*lecture_api|serve.*build|node.*serve)' | grep -v grep || echo '프로세스를 찾을 수 없습니다.'
    echo ''
    echo '=== 최근 로그 (백엔드) ==='
    tail -5 ~/api.log 2>&1 || echo '백엔드 로그 없음'
    echo ''
    echo '=== 최근 로그 (프론트엔드) ==='
    tail -5 ~/frontend.log 2>&1 || echo '프론트엔드 로그 없음'
"

echo ""
echo -e "${GREEN}✅ 프로젝트 실행 완료!${NC}"
echo "=================================="
echo -e "${GREEN}🌐 프론트엔드: http://$VM_HOST:3000${NC}"
echo -e "${GREEN}🔧 백엔드 API: http://$VM_HOST:5002${NC}"
echo ""
echo -e "${BLUE}📝 유용한 명령어:${NC}"
echo "  상태 확인: ./scripts/check_status.sh"
echo "  백엔드 로그: ssh $VM_USER@$VM_HOST -i $SSH_KEY 'tail -f ~/api.log'"
echo "  프론트엔드 로그: ssh $VM_USER@$VM_HOST -i $SSH_KEY 'tail -f ~/frontend.log'"
echo "  서버 중지: ssh $VM_USER@$VM_HOST -i $SSH_KEY 'pkill -f \"python.*lecture_api\|serve.*build\"'"
