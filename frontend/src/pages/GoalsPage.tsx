import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CreateGoalModal from '../components/Goals/CreateGoalModal';
import EditGoalModal from '../components/Goals/EditGoalModal';
import { Goal } from '../types/goal';

const GoalsPage: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterCategory, setFilterCategory] = useState<string>('');

  const statusLabels = {
    active: '진행중',
    completed: '완료',
    paused: '일시정지',
    cancelled: '취소'
  };

  const categoryLabels = {
    health: '건강',
    education: '교육',
    career: '커리어',
    personal: '개인',
    finance: '재정'
  };

  const priorityLabels = {
    high: '높음',
    medium: '보통',
    low: '낮음'
  };

  const priorityColors = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800'
  };

  const statusColors = {
    active: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    paused: 'bg-yellow-100 text-yellow-800',
    cancelled: 'bg-red-100 text-red-800'
  };

  const fetchGoals = async () => {
    setIsLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.append('status', filterStatus);
      if (filterCategory) params.append('category', filterCategory);
      
      console.log('API 요청:', `/api/goals/?${params.toString()}`);
      const response = await axios.get(`/api/goals/?${params.toString()}`);
      console.log('API 응답 데이터:', response.data);
      console.log('데이터 타입:', typeof response.data);
      console.log('데이터 길이:', response.data.length);
      
      setGoals(response.data);
    } catch (error) {
      console.error('목표 조회 실패:', error);
      setError('목표를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, [filterStatus, filterCategory]);

  useEffect(() => {
    console.log('goals 상태가 업데이트되었습니다:', goals);
    console.log('목표 개수:', goals.length);
  }, [goals]);

  const handleStatusChange = async (goalId: string, newStatus: string) => {
    try {
      await axios.put(`/api/goals/${goalId}`, { status: newStatus });
      fetchGoals(); // 목표 리스트 새로고침
    } catch (error) {
      console.error('상태 변경 실패:', error);
      alert('상태 변경에 실패했습니다.');
    }
  };

  const handleDelete = async (goalId: string) => {
    if (!window.confirm('정말로 이 목표를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await axios.delete(`/api/goals/${goalId}`);
      fetchGoals(); // 목표 리스트 새로고침
    } catch (error) {
      console.error('목표 삭제 실패:', error);
      alert('목표 삭제에 실패했습니다.');
    }
  };

  const calculateProgress = (current: number, target: number) => {
    return Math.min((current / target) * 100, 100);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR');
  };

  const handleGoalCreated = () => {
    console.log('목표가 생성되었습니다. 목표 리스트를 새로고침합니다.');
    fetchGoals(); // 새 목표가 생성되면 목표 리스트 새로고침
  };

  const handleGoalUpdated = () => {
    fetchGoals(); // 목표가 수정되면 목표 리스트 새로고침
  };

  const handleEditClick = (goal: Goal) => {
    setSelectedGoal(goal);
    setIsEditModalOpen(true);
  };

  const handleDebugCheck = async () => {
    try {
      console.log('디버깅 API 호출 중...');
      const response = await axios.get('/api/goals/debug/all');
      console.log('디버깅 API 응답:', response.data);
      alert('디버깅 정보가 콘솔에 출력되었습니다. F12를 눌러 확인하세요.');
    } catch (error) {
      console.error('디버깅 API 호출 실패:', error);
      alert('디버깅 API 호출에 실패했습니다.');
    }
  };

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">목표 관리</h1>
        <div className="flex space-x-2">
          {/* <button
            onClick={handleDebugCheck}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg text-sm"
          >
            디버깅 확인
          </button> */}
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg"
          >
            새 목표 생성
          </button>
        </div>
      </div>

      {/* 필터 */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">상태</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">모든 상태</option>
              <option value="active">진행중</option>
              <option value="completed">완료</option>
              <option value="paused">일시정지</option>
              <option value="cancelled">취소</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">카테고리</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">모든 카테고리</option>
              <option value="health">건강</option>
              <option value="education">교육</option>
              <option value="career">커리어</option>
              <option value="personal">개인</option>
              <option value="finance">재정</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* 목표 리스트 */}
      {(() => {
        console.log('렌더링 시점 - goals.length:', goals.length, 'isLoading:', isLoading);
        return null;
      })()}
      {!isLoading && goals.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">목표가 없습니다</h3>
          <p className="text-gray-500 mb-4">첫 번째 목표를 생성해보세요!</p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg"
          >
            목표 생성하기
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {goals.map((goal) => (
            <div key={goal.id} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900 truncate">{goal.title}</h3>
                  <div className="flex space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[goal.status]}`}>
                      {statusLabels[goal.status]}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityColors[goal.priority]}`}>
                      {priorityLabels[goal.priority]}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-2">{goal.description}</p>

                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>진도</span>
                    <span>{goal.current_value} / {goal.target_value} {goal.unit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${calculateProgress(goal.current_value, goal.target_value)}%` }}
                    ></div>
                  </div>
                  <div className="text-right text-xs text-gray-500 mt-1">
                    {calculateProgress(goal.current_value, goal.target_value).toFixed(1)}%
                  </div>
                </div>

                <div className="text-sm text-gray-600 mb-4">
                  <div className="flex justify-between">
                    <span>카테고리:</span>
                    <span>{categoryLabels[goal.category]}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>마감일:</span>
                    <span>{formatDate(goal.deadline)}</span>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <select
                    value={goal.status}
                    onChange={(e) => handleStatusChange(goal.id, e.target.value)}
                    className="text-sm border border-gray-300 rounded px-2 py-1"
                  >
                    <option value="active">진행중</option>
                    <option value="completed">완료</option>
                    <option value="paused">일시정지</option>
                    <option value="cancelled">취소</option>
                  </select>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEditClick(goal)}
                      className="text-primary-600 hover:text-primary-800 text-sm font-medium"
                    >
                      편집
                    </button>
                    <button
                      onClick={() => handleDelete(goal.id)}
                      className="text-red-600 hover:text-red-800 text-sm font-medium"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 목표 생성 모달 */}
      <CreateGoalModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onGoalCreated={handleGoalCreated}
      />

      {/* 목표 편집 모달 */}
      <EditGoalModal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedGoal(null);
        }}
        onGoalUpdated={handleGoalUpdated}
        goal={selectedGoal}
      />
    </div>
  );
};

export default GoalsPage; 