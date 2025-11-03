#!/bin/bash

# 프로젝트 전체 실행 스크립트
# Google Cloud VM에서 백엔드와 프론트엔드를 실행합니다.

set -e

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

echo -e "${BLUE}🚀 프로젝트 전체 실행 스크립트${NC}"
echo "=================================="

# SSH 연결 테스트
echo -e "${BLUE}📡 SSH 연결 테스트...${NC}"
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 $VM_USER@$VM_HOST -i $SSH_KEY "echo 'SSH 연결 성공'" > /dev/null 2>&1; then
    echo -e "${RED}❌ SSH 연결 실패${NC}"
    echo "VM이 실행 중인지 확인하세요: $VM_HOST"
    exit 1
fi
echo -e "${GREEN}✅ SSH 연결 성공${NC}"

# 기존 프로세스 종료
echo -e "${YELLOW}🛑 기존 프로세스 종료 중...${NC}"
ssh -o StrictHostKeyChecking=no $VM_USER@$VM_HOST -i $SSH_KEY "
    pkill -f 'python.*lecture_api.py' || true
    pkill -f 'serve.*build' || true
    pkill -f 'npx serve' || true
"

# MongoDB 시작
echo -e "${BLUE}🗄️ MongoDB 컨테이너 시작 중...${NC}"
ssh -o StrictHostKeyChecking=no $VM_USER@$VM_HOST -i $SSH_KEY "
    cd ~ && 
    if ! docker ps | grep -q crawller-mongo; then
        docker compose up -d
        echo 'MongoDB 컨테이너 시작됨'
    else
        echo 'MongoDB가 이미 실행 중'
    fi
"

# 백엔드 시작
echo -e "${BLUE}🔧 백엔드 API 서버 시작 중...${NC}"
ssh -o StrictHostKeyChecking=no $VM_USER@$VM_HOST -i $SSH_KEY "
    cd ~ && 
    source venv/bin/activate && 
    nohup python backend/api/lecture_api.py > api.log 2>&1 &
    echo '백엔드 서버 시작됨'
"

# 잠시 대기
sleep 3

# 프론트엔드 시작
echo -e "${BLUE}🎨 프론트엔드 서버 시작 중...${NC}"
ssh -o StrictHostKeyChecking=no $VM_USER@$VM_HOST -i $SSH_KEY "
    cd ~/frontend/react-app && 
    nohup npx serve -s build -l 3000 > ../frontend.log 2>&1 &
    echo '프론트엔드 서버 시작됨'
"

# 잠시 대기
sleep 3

# 상태 확인
echo -e "${BLUE}📊 서버 상태 확인 중...${NC}"
ssh -o StrictHostKeyChecking=no $VM_USER@$VM_HOST -i $SSH_KEY "
    echo '=== 포트 상태 ==='
    ss -tlnp | grep -E ':(3000|5002)' || echo '일부 포트가 열리지 않았습니다.'
    echo ''
    echo '=== 프로세스 상태 ==='
    ps aux | grep -E '(python.*lecture_api|serve.*build|node.*serve)' | grep -v grep || echo '일부 프로세스를 찾을 수 없습니다.'
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
