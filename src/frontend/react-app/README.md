# AI 강의 검색 플랫폼

React 기반의 스마트 강의 분석 플랫폼입니다.

## 주요 기능

- 🔍 **AI 강의 검색**: 자연어로 강의를 검색하고 AI가 분석한 결과를 확인
- 📊 **강의 상세 분석**: 평점, 난이도, 과제량 등 상세한 강의 정보
- 📈 **트렌드 분석**: 인기 강의 및 검색 트렌드 확인
- 🎯 **맞춤 추천**: 개인 맞춤형 강의 추천 시스템
- 📚 **학점 계산**: GPA 계산 및 졸업 요건 분석

## 설치 방법

### 1. Node.js 설치

먼저 Node.js를 설치해야 합니다.

**macOS (Homebrew 사용):**
```bash
brew install node
```

**macOS (공식 설치 프로그램):**
1. [Node.js 공식 웹사이트](https://nodejs.org/)에서 LTS 버전 다운로드
2. 다운로드한 .pkg 파일 실행하여 설치

### 2. 프로젝트 의존성 설치

```bash
cd /Users/choyejin/Desktop/crawller/src/frontend/react-app
npm install
```

### 3. 개발 서버 실행

```bash
npm start
```

브라우저에서 `http://localhost:3000`으로 접속하면 애플리케이션을 확인할 수 있습니다.

## 프로젝트 구조

```
react-app/
├── public/
│   └── index.html          # HTML 템플릿
├── src/
│   ├── App.js             # 메인 애플리케이션 컴포넌트
│   └── index.js           # React 앱 진입점
├── package.json           # 프로젝트 설정 및 의존성
└── README.md             # 이 파일
```

## 사용된 기술

- **React 18**: UI 라이브러리
- **Tailwind CSS**: 스타일링 (CDN)
- **Lucide React**: 아이콘 라이브러리
- **React Scripts**: 빌드 도구

## 페이지 구성

1. **강의 검색** (`/search`): 메인 검색 페이지
2. **강의 상세** (`/detail`): 선택한 강의의 상세 정보
3. **트렌드 분석** (`/trends`): 강의 트렌드 및 통계
4. **맞춤 추천** (`/recommend`): 개인 맞춤 강의 추천
5. **학점 계산** (`/gpa`): GPA 계산기 및 졸업 요건 분석

## 개발 명령어

```bash
# 개발 서버 실행
npm start

# 프로덕션 빌드
npm run build

# 테스트 실행
npm test
```

## 문제 해결

### Node.js가 설치되지 않은 경우
```bash
# Node.js 버전 확인
node --version
npm --version

# 설치되지 않은 경우 위의 설치 방법 참고
```

### 의존성 설치 오류
```bash
# npm 캐시 정리
npm cache clean --force

# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

## 추가 개발 예정 기능

- [ ] 백엔드 API 연동
- [ ] 사용자 인증 시스템
- [ ] 실시간 강의평 크롤링
- [ ] 모바일 반응형 최적화
- [ ] 다크 모드 지원
