# Windows 환경에서 개발할 때는 node:18 (alpine이 아닌 일반 버전 사용)
FROM node:18
WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치 (Windows 환경에서는 npm ci 대신 npm install 사용)
RUN npm install

# 소스 코드 복사
COPY . .

# 개발 서버 실행 (빌드하지 않고 개발 모드로 실행)
EXPOSE 3000
CMD ["npm", "start"]