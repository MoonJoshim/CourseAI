#!/bin/bash

# 간단한 프로젝트 시작 스크립트
# Google Cloud VM에서 백엔드와 프론트엔드를 실행합니다.

echo "🚀 프로젝트 시작 중..."

# VM 정보
VM_USER="seohyun"
VM_HOST="34.58.143.2"
SSH_KEY="./moonjoshim"

echo "📡 VM에 연결 중..."

# 백엔드 시작
echo "🔧 백엔드 API 서버 시작 중..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $VM_USER@$VM_HOST -i $SSH_KEY "
    cd ~ && 
    source venv/bin/activate && 
    pkill -f 'python.*lecture_api.py' || true &&
    nohup python backend/api/lecture_api.py > api.log 2>&1 &
"

# 잠시 대기
sleep 3

# 프론트엔드 시작
echo "🎨 프론트엔드 서버 시작 중..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $VM_USER@$VM_HOST -i $SSH_KEY "
    cd ~/frontend/react-app && 
    pkill -f 'serve.*build' || true &&
    nohup npx serve -s build -l 3000 > ../frontend.log 2>&1 &
"

# 잠시 대기
sleep 3

# 상태 확인
echo "📊 서버 상태 확인 중..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $VM_USER@$VM_HOST -i $SSH_KEY "
    echo '=== 포트 상태 ==='
    ss -tlnp | grep -E ':(3000|5002)' || echo '포트가 열리지 않았습니다.'
    echo ''
    echo '=== 프로세스 상태 ==='
    ps aux | grep -E '(python.*lecture_api|serve.*build)' | grep -v grep || echo '프로세스를 찾을 수 없습니다.'
"

echo ""
echo "✅ 프로젝트 시작 완료!"
echo "🌐 프론트엔드: http://$VM_HOST:3000"
echo "🔧 백엔드 API: http://$VM_HOST:5002"
echo ""
echo "📝 로그 확인:"
echo "   백엔드: ssh $VM_USER@$VM_HOST -i $SSH_KEY 'tail -f ~/api.log'"
echo "   프론트엔드: ssh $VM_USER@$VM_HOST -i $SSH_KEY 'tail -f ~/frontend.log'"
