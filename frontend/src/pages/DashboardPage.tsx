import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import CreateGoalModal from '../components/Goals/CreateGoalModal';
import axios from 'axios';

interface Goal {
  _id: string;
  title: string;
  description: string;
  category: string;
  target_value: number;
  current_value: number;
  unit: string;
  deadline: string;
  priority: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface DashboardStats {
  activeGoals: number;
  completedGoals: number;
  averageProgress: number;
}

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [stats, setStats] = useState<DashboardStats>({
    activeGoals: 0,
    completedGoals: 0,
    averageProgress: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/goals/', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      const goals: Goal[] = response.data;
      
      // 통계 계산
      const activeGoals = goals.filter(goal => goal.status === 'active').length;
      const completedGoals = goals.filter(goal => goal.status === 'completed').length;
      
      // 평균 진도율 계산 (활성 목표만 대상)
      const activeGoalsList = goals.filter(goal => goal.status === 'active');
      let averageProgress = 0;
      if (activeGoalsList.length > 0) {
        const totalProgress = activeGoalsList.reduce((sum, goal) => {
          const progress = (goal.current_value / goal.target_value) * 100;
          return sum + Math.min(progress, 100); // 100%를 초과하지 않도록 제한
        }, 0);
        averageProgress = Math.round(totalProgress / activeGoalsList.length);
      }

      setStats({
        activeGoals,
        completedGoals,
        averageProgress
      });

    } catch (error) {
      console.error('대시보드 데이터 조회 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleGoalCreated = () => {
    // 목표가 생성되면 대시보드 데이터를 새로고침
    console.log('새 목표가 생성되었습니다!');
    fetchDashboardData();
  };

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            안녕하세요, {user?.profile.name}님! 👋
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            GoalMaster AI와 함께 목표를 달성해보세요
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-primary-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">🎯</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        활성 목표
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {isLoading ? '로딩 중...' : `${stats.activeGoals}개`}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-success-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">✅</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        완료된 목표
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {isLoading ? '로딩 중...' : `${stats.completedGoals}개`}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-warning-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">📈</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        평균 진도율
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {isLoading ? '로딩 중...' : `${stats.averageProgress}%`}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                시작하기
              </h2>
              <p className="text-gray-600 mb-6">
                {stats.activeGoals === 0 
                  ? "첫 번째 목표를 설정하고 AI 코치와 함께 달성 계획을 세워보세요!"
                  : "새로운 목표를 추가하거나 기존 목표의 진도를 업데이트해보세요!"
                }
              </p>
              <button 
                onClick={() => setIsCreateModalOpen(true)}
                className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded"
              >
                목표 생성하기
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 목표 생성 모달 */}
      <CreateGoalModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onGoalCreated={handleGoalCreated}
      />
    </div>
  );
};

export default DashboardPage; 