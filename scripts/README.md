# scripts

## start_backend.sh

백엔드(lecture_api, ai_api)를 실행하기 전에 MongoDB가 기동되어 있는지 확인하고, 없으면 자동으로 시작합니다. VM(Ubuntu)에서는 `systemctl`을 이용해 `mongod` 서비스를 올라오게 하며, 로컬 환경에서는 `mongod` 바이너리가 있을 경우 독립 실행 모드로 띄웁니다.

### 사용법

```bash
cd /Users/choyejin/Desktop/crawller
./scripts/start_backend.sh start   # MongoDB + 백엔드 실행
./scripts/start_backend.sh stop    # 백엔드 종료
./scripts/start_backend.sh status  # 상태 확인
./scripts/start_backend.sh logs    # 최근 로그 확인
```

> **주의**
> - VM에서 MongoDB는 systemd 서비스(`mongod`)로 운영됩니다.
> - 최초 실행 시 sudo 권한이 필요할 수 있습니다.
> - 백엔드 가상환경이 없으면 스크립트가 자동 생성하고 의존성을 설치합니다.


