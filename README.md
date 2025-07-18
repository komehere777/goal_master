# GoalMaster AI - 개인 목표 달성 코치

AI 기반 개인 목표 달성 코칭 플랫폼입니다.

## 🚀 주요 기능

- **AI 목표 분석**: OpenAI를 활용한 목표 분석 및 달성 가능성 평가
- **맞춤형 실행 계획**: 개인화된 단계별 실행 계획 생성
- **실시간 진도 추적**: 목표 달성 과정의 실시간 모니터링
- **AI 코칭**: 개인화된 동기부여 메시지 및 피드백
- **커뮤니티**: 유사한 목표를 가진 사용자들과의 연결

## 🛠 기술 스택

### Backend
- **FastAPI 0.104+** - 고성능 Python 웹 프레임워크
- **MongoDB 7.0+** - NoSQL 데이터베이스
- **OpenAI API** - GPT-4 기반 AI 코칭
- **Redis** - 캐싱 및 세션 관리
- **JWT** - 사용자 인증

### Frontend
- **React 18.2+** - TypeScript 기반
- **Tailwind CSS** - 유틸리티 우선 CSS 프레임워크
- **React Query** - 서버 상태 관리
- **Chart.js** - 데이터 시각화
- **Axios** - HTTP 클라이언트

### Infrastructure
- **Docker & Docker Compose** - 컨테이너 기반 배포
- **MongoDB Express** - 개발용 데이터베이스 GUI

## 📦 설치 및 실행

### 환경 요구사항
- Docker 및 Docker Compose
- OpenAI API 키

### 1. 저장소 클론
```bash
git clone <repository-url>
cd goal_master
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일에서 다음 값들을 설정
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_secure_jwt_secret_key
```

### 3. 애플리케이션 실행
```bash
# 전체 스택 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

### 4. 서비스 접속
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **MongoDB Express**: http://localhost:8081

## 🏗 프로젝트 구조

```
goal_master/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── core/           # 설정, 보안, 데이터베이스
│   │   ├── models/         # Pydantic 모델
│   │   ├── routers/        # API 라우터
│   │   └── __init__.py
│   ├── main.py            # FastAPI 애플리케이션
│   ├── requirements.txt   # Python 의존성
│   └── Dockerfile
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── contexts/      # React 컨텍스트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   └── index.tsx
│   ├── package.json       # Node.js 의존성
│   └── Dockerfile
├── mongodb/
│   └── init/              # MongoDB 초기화 스크립트
├── docker-compose.yml     # Docker Compose 설정
└── .env.example          # 환경 변수 예시
```

## 🔧 개발 환경 설정

### 로그 확인
```bash
# 전체 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 개별 서비스 실행
```bash
# 백엔드만 실행
docker-compose up backend mongodb

# 프론트엔드만 실행
docker-compose up frontend
```

### 데이터베이스 초기화
```bash
# 모든 데이터 삭제 후 재시작
docker-compose down -v
docker-compose up --build
```

## 📚 API 문서

백엔드 서버 실행 후 http://localhost:8000/docs 에서 상세한 API 문서를 확인할 수 있습니다.

### 주요 API 엔드포인트

#### 인증
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/me` - 현재 사용자 정보

#### 목표 관리
- `GET /api/goals` - 목표 목록 조회
- `POST /api/goals` - 새 목표 생성
- `PUT /api/goals/{goal_id}` - 목표 수정

#### AI 코칭
- `POST /api/ai/analyze-goal` - 목표 분석
- `POST /api/ai/generate-plan` - 실행 계획 생성
- `POST /api/ai/get-coaching` - 코칭 메시지 요청

## 🔒 보안

- JWT 토큰 기반 인증
- 비밀번호 bcrypt 해싱
- API 요청 CORS 설정
- 환경 변수를 통한 민감 정보 관리

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 💡 문제 해결

### 일반적인 문제들

1. **포트 충돌 오류**
   ```bash
   # 사용 중인 포트 확인
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   ```

2. **Docker 빌드 오류**
   ```bash
   # 캐시 없이 다시 빌드
   docker-compose build --no-cache
   ```

3. **MongoDB 연결 오류**
   ```bash
   # MongoDB 컨테이너 상태 확인
   docker-compose logs mongodb
   ```

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요. 