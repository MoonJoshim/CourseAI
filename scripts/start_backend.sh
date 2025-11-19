#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/venv"
LOG_DIR="${PROJECT_ROOT}/logs"

LECTURE_LOG="${LOG_DIR}/lecture_api.log"
AI_LOG="${LOG_DIR}/ai_api.log"

function ensure_mongo_running() {
  echo "[정보] MongoDB 상태를 확인합니다."

  if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-active --quiet mongod; then
      echo "[완료] MongoDB 서비스가 이미 실행 중입니다."
      return 0
    fi

    echo "[동작] systemctl을 사용해 MongoDB를 시작합니다."
    sudo systemctl start mongod

    if systemctl is-active --quiet mongod; then
      echo "[완료] MongoDB 서비스가 정상적으로 시작되었습니다."
      return 0
    fi

    echo "[경고] systemctl로 MongoDB를 시작하지 못했습니다."
  fi

  if pgrep -f "mongod" >/dev/null 2>&1; then
    echo "[완료] MongoDB 프로세스가 이미 실행 중입니다."
    return 0
  fi

  if ! command -v mongod >/dev/null 2>&1; then
    echo "[오류] mongod 명령을 찾을 수 없습니다. MongoDB가 설치되어 있는지 확인하세요." >&2
    return 1
  fi

  mkdir -p "${LOG_DIR}"
  DATA_DIR="${PROJECT_ROOT}/mongodb-data"
  mkdir -p "${DATA_DIR}"

  echo "[동작] 독립 실행으로 MongoDB를 시작합니다."
  nohup mongod --dbpath "${DATA_DIR}" --bind_ip 127.0.0.1 --port 27017 \
    > "${LOG_DIR}/mongod.log" 2>&1 &

  sleep 3

  if pgrep -f "mongod" >/dev/null 2>&1; then
    echo "[완료] MongoDB가 독립 실행 모드로 시작되었습니다."
    return 0
  fi

  echo "[오류] MongoDB를 자동으로 시작하지 못했습니다." >&2
  return 1
}

function ensure_venv() {
  if [[ ! -d "${VENV_DIR}" ]]; then
    echo "[동작] Python 가상환경을 생성합니다."
    python3 -m venv "${VENV_DIR}"
  fi
  # shellcheck source=/dev/null
  source "${VENV_DIR}/bin/activate"
  pip install --upgrade pip >/dev/null
  pip install -r "${PROJECT_ROOT}/backend/requirements.txt"
}

function start_backends() {
  mkdir -p "${LOG_DIR}"

  echo "[동작] lecture_api 서버를 백그라운드에서 실행합니다."
  nohup python "${PROJECT_ROOT}/backend/api/lecture_api.py" \
    > "${LECTURE_LOG}" 2>&1 &

  echo "[동작] ai_api 서버를 백그라운드에서 실행합니다."
  nohup python "${PROJECT_ROOT}/backend/api/ai_api.py" \
    > "${AI_LOG}" 2>&1 &

  sleep 2
  echo "[완료] 백엔드 서버가 시작되었습니다."
}

function stop_backends() {
  echo "[동작] 백엔드 서버를 종료합니다."
  pkill -f "python.*backend/api/lecture_api.py" >/dev/null 2>&1 || true
  pkill -f "python.*backend/api/ai_api.py" >/dev/null 2>&1 || true
  echo "[완료] 백엔드 서버를 종료했습니다."
}

function show_status() {
  if pgrep -f "backend/api/lecture_api.py" >/dev/null 2>&1; then
    echo "[상태] lecture_api: 실행 중"
  else
    echo "[상태] lecture_api: 정지"
  fi

  if pgrep -f "backend/api/ai_api.py" >/dev/null 2>&1; then
    echo "[상태] ai_api: 실행 중"
  else
    echo "[상태] ai_api: 정지"
  fi

  if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-active --quiet mongod; then
      echo "[상태] MongoDB(systemd): 실행 중"
    else
      echo "[상태] MongoDB(systemd): 정지"
    fi
  elif pgrep -f "mongod" >/dev/null 2>&1; then
    echo "[상태] MongoDB(프로세스): 실행 중"
  else
    echo "[상태] MongoDB: 정지"
  fi
}

function show_logs() {
  mkdir -p "${LOG_DIR}"
  tail -n 30 "${LOG_DIR}/mongod.log" 2>/dev/null || echo "MongoDB 로그가 없습니다."
  echo "-----"
  tail -n 30 "${LECTURE_LOG}" 2>/dev/null || echo "lecture_api 로그가 없습니다."
  echo "-----"
  tail -n 30 "${AI_LOG}" 2>/dev/null || echo "ai_api 로그가 없습니다."
}

case "${1:-start}" in
  start)
    ensure_mongo_running
    ensure_venv
    start_backends
    ;;
  stop)
    stop_backends
    ;;
  restart)
    stop_backends
    ensure_mongo_running
    ensure_venv
    start_backends
    ;;
  status)
    show_status
    ;;
  logs)
    show_logs
    ;;
  *)
    echo "사용법: $0 {start|stop|restart|status|logs}" >&2
    exit 1
    ;;
esac


