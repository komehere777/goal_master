// MongoDB 초기화 스크립트
// GoalMaster 데이터베이스 생성 및 기본 인덱스 설정

// 데이터베이스 선택
db = db.getSiblingDB('goalmaster');

// 컬렉션 생성 및 인덱스 설정

// Users 컬렉션
db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": 1 });

// Goals 컬렉션
db.createCollection('goals');
db.goals.createIndex({ "user_id": 1 });
db.goals.createIndex({ "status": 1 });
db.goals.createIndex({ "category": 1 });
db.goals.createIndex({ "deadline": 1 });
db.goals.createIndex({ "created_at": -1 });

// Action_Plans 컬렉션
db.createCollection('action_plans');
db.action_plans.createIndex({ "goal_id": 1 });
db.action_plans.createIndex({ "user_id": 1 });
db.action_plans.createIndex({ "created_at": -1 });

// Progress_Logs 컬렉션
db.createCollection('progress_logs');
db.progress_logs.createIndex({ "goal_id": 1 });
db.progress_logs.createIndex({ "user_id": 1 });
db.progress_logs.createIndex({ "created_at": -1 });
db.progress_logs.createIndex({ "log_type": 1 });

// AI_Interactions 컬렉션
db.createCollection('ai_interactions');
db.ai_interactions.createIndex({ "user_id": 1 });
db.ai_interactions.createIndex({ "goal_id": 1 });
db.ai_interactions.createIndex({ "interaction_type": 1 });
db.ai_interactions.createIndex({ "created_at": -1 });

// 샘플 데이터 생성 (개발 환경용)
const sampleUser = {
    email: "demo@goalmaster.com",
    password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfKPbYl0rqB8NGu", // password: demo123
    profile: {
        name: "데모 사용자",
        timezone: "Asia/Seoul",
        preferences: {
            notification_time: "09:00",
            coaching_style: "motivational"
        }
    },
    created_at: new Date(),
    updated_at: new Date()
};

// 샘플 사용자 삽입 (이미 존재하지 않는 경우)
const existingUser = db.users.findOne({ email: "demo@goalmaster.com" });
if (!existingUser) {
    const userResult = db.users.insertOne(sampleUser);
    print("샘플 사용자 생성됨: " + userResult.insertedId);
    
    // 샘플 목표 데이터
    const sampleGoals = [
        {
            user_id: userResult.insertedId,
            title: "운동 습관 만들기",
            description: "매일 30분 이상 운동하여 건강한 생활 습관을 만들고 싶습니다.",
            category: "health",
            target_value: 30,
            current_value: 0,
            unit: "일",
            deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000), // 90일 후
            priority: "high",
            status: "active",
            created_at: new Date(),
            updated_at: new Date()
        },
        {
            user_id: userResult.insertedId,
            title: "책 읽기 목표",
            description: "올해 12권의 책을 읽어 자기계발을 하고 싶습니다.",
            category: "education",
            target_value: 12,
            current_value: 2,
            unit: "권",
            deadline: new Date(new Date().getFullYear(), 11, 31), // 올해 말
            priority: "medium",
            status: "active",
            created_at: new Date(),
            updated_at: new Date()
        }
    ];
    
    const goalResult = db.goals.insertMany(sampleGoals);
    print("샘플 목표 생성됨: " + goalResult.insertedIds.length + "개");
}

print("GoalMaster 데이터베이스 초기화 완료!"); 