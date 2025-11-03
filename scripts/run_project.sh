#!/bin/bash

# 프로젝트 실행 스크립트
# Google Cloud VM에서 백엔드와 프론트엔드를 실행합니다.

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# VM 정보
VM_USER="seohyun"
VM_HOST="34.58.143.2"
SSH_KEY="./moonjoshim"

# 프로젝트 디렉토리
PROJECT_DIR="~/"

# 함수: SSH 명령 실행
run_ssh() {
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $VM_USER@$VM_HOST -i $SSH_KEY "$@"
}

# 함수: 프로세스 종료
kill_existing_processes() {
    log_info "기존 프로세스 종료 중..."
    
    # 백엔드 프로세스 종료
    run_ssh "pkill -f 'python.*lecture_api.py' || true"
    
    # 프론트엔드 프로세스 종료
    run_ssh "pkill -f 'serve.*build' || true"
    
    log_success "기존 프로세스 종료 완료"
}

# 함수: MongoDB 시작
start_mongodb() {
    log_info "MongoDB 컨테이너 시작 중..."
    
    if run_ssh "docker ps | grep -q crawller-mongo"; then
        log_info "MongoDB가 이미 실행 중입니다."
    else
        run_ssh "cd $PROJECT_DIR && docker compose up -d"
        log_success "MongoDB 컨테이너 시작 완료"
    fi
}

# 함수: 백엔드 시작
start_backend() {
    log_info "백엔드 API 서버 시작 중..."
    
    # 가상환경 활성화 및 백엔드 실행
    run_ssh "cd $PROJECT_DIR && source venv/bin/activate && nohup python backend/api/lecture_api.py > api.log 2>&1 &"
    
    # 서버 시작 대기
    sleep 3
    
    # 포트 확인
    if run_ssh "ss -tlnp | grep -q ':5002'"; then
        log_success "백엔드 API 서버가 포트 5002에서 실행 중입니다."
    else
        log_error "백엔드 서버 시작에 실패했습니다."
        run_ssh "tail -20 ~/api.log"
        exit 1
    fi
}

# 함수: 프론트엔드 시작
start_frontend() {
    log_info "프론트엔드 서버 시작 중..."
    
    # 프론트엔드 디렉토리로 이동하여 실행
    run_ssh "cd $PROJECT_DIR/frontend/react-app && nohup npx serve -s build -l 3000 > ../frontend.log 2>&1 &"
    
    # 서버 시작 대기
    sleep 3
    
    # 포트 확인
    if run_ssh "ss -tlnp | grep -q ':3000'"; then
        log_success "프론트엔드 서버가 포트 3000에서 실행 중입니다."
    else
        log_error "프론트엔드 서버 시작에 실패했습니다."
        run_ssh "tail -20 ~/frontend.log"
        exit 1
    fi
}

# 함수: 서버 상태 확인
check_status() {
    log_info "서버 상태 확인 중..."
    
    echo ""
    echo "=== 서버 상태 ==="
    
    # 포트 확인
    run_ssh "ss -tlnp | grep -E ':(3000|5002)'"
    
    echo ""
    echo "=== 프로세스 확인 ==="
    run_ssh "ps aux | grep -E '(python.*lecture_api|serve.*build)' | grep -v grep"
    
    echo ""
    echo "=== 접속 정보 ==="
    echo "프론트엔드: http://$VM_HOST:3000"
    echo "백엔드 API: http://$VM_HOST:5002"
}

# 함수: 로그 확인
show_logs() {
    log_info "최근 로그 확인 중..."
    
    echo ""
    echo "=== 백엔드 로그 (최근 10줄) ==="
    run_ssh "tail -10 ~/api.log"
    
    echo ""
    echo "=== 프론트엔드 로그 (최근 10줄) ==="
    run_ssh "tail -10 ~/frontend.log"
}

# 함수: 서버 중지
stop_servers() {
    log_info "서버 중지 중..."
    
    kill_existing_processes
    
    log_success "모든 서버가 중지되었습니다."
}

# 메인 실행 함수
main() {
    case "${1:-start}" in
        "start")
            echo "🚀 프로젝트 시작 중..."
            kill_existing_processes
            start_mongodb
            start_backend
            start_frontend
            check_status
            ;;
        "stop")
            echo "🛑 프로젝트 중지 중..."
            stop_servers
            ;;
        "restart")
            echo "🔄 프로젝트 재시작 중..."
            stop_servers
            sleep 2
            start_mongodb
            start_backend
            start_frontend
            check_status
            ;;
        "status")
            check_status
            ;;
        "logs")
            show_logs
            ;;
        "help"|"-h"|"--help")
            echo "사용법: $0 [명령어]"
            echo ""
            echo "명령어:"
            echo "  start     - 프로젝트 시작 (기본값)"
            echo "  stop      - 프로젝트 중지"
            echo "  restart   - 프로젝트 재시작"
            echo "  status    - 서버 상태 확인"
            echo "  logs      - 로그 확인"
            echo "  help      - 도움말 표시"
            ;;
        *)
            log_error "알 수 없는 명령어: $1"
            echo "사용법: $0 help"
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"
