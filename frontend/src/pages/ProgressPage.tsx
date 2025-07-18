import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';
import { Goal } from '../types/goal';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement);

interface ProgressLog {
  id: string;
  goal_id: string;
  log_type: 'progress' | 'milestone' | 'setback' | 'note';
  value?: number;
  description: string;
  mood_score?: number;
  created_at: string;
}

interface AICoachingMessage {
  message: string;
  type: string;
  created_at: string;
}

const ProgressPage: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [progressLogs, setProgressLogs] = useState<ProgressLog[]>([]);
  const [coachingMessage, setCoachingMessage] = useState<AICoachingMessage | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // 진도 기록 추가 폼
  const [isAddingProgress, setIsAddingProgress] = useState(false);
  const [progressForm, setProgressForm] = useState({
    goal_id: '',
    log_type: 'progress' as 'progress' | 'milestone' | 'setback' | 'note',
    value: '',
    description: '',
    mood_score: '5'
  });

  const fetchGoals = async () => {
    try {
      const response = await axios.get('/api/goals/');
      setGoals(response.data);
      if (response.data.length > 0 && !selectedGoal) {
        setSelectedGoal(response.data[0]);
      }
    } catch (error) {
      console.error('목표 조회 실패:', error);
      setError('목표를 불러오는데 실패했습니다.');
    }
  };

  const fetchProgressLogs = async (goalId: string) => {
    try {
      const response = await axios.get(`/api/progress/goal/${goalId}`);
      setProgressLogs(response.data);
    } catch (error) {
      console.error('진도 기록 조회 실패:', error);
    }
  };

  const fetchCoachingMessage = async (goalId: string) => {
    try {
      const response = await axios.get(`/api/ai/get-coaching/${goalId}?message_type=daily`);
      setCoachingMessage(response.data);
    } catch (error) {
      console.error('AI 코칭 메시지 조회 실패:', error);
      // 실패 시 기본 메시지 설정
      setCoachingMessage({
        message: "오늘도 목표를 향해 한 걸음씩 나아가고 계시는군요! 꾸준히 노력하는 모습이 멋집니다. 💪",
        type: "daily",
        created_at: new Date().toISOString()
      });
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await fetchGoals();
      setIsLoading(false);
    };
    loadData();
  }, []);

  useEffect(() => {
    if (selectedGoal) {
      fetchProgressLogs(selectedGoal.id);
      fetchCoachingMessage(selectedGoal.id);
    }
  }, [selectedGoal]);

  const handleAddProgress = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGoal) return;

    try {
      const requestData = {
        goal_id: selectedGoal.id,
        log_type: progressForm.log_type,
        value: progressForm.value ? parseFloat(progressForm.value) : undefined,
        description: progressForm.description,
        mood_score: progressForm.mood_score ? parseInt(progressForm.mood_score) : undefined
      };

      await axios.post('/api/progress/', requestData);
      
      // 폼 초기화
      setProgressForm({
        goal_id: '',
        log_type: 'progress',
        value: '',
        description: '',
        mood_score: '5'
      });
      setIsAddingProgress(false);
      
      // 데이터 새로고침
      fetchProgressLogs(selectedGoal.id);
      fetchGoals(); // 목표의 current_value가 업데이트될 수 있음
    } catch (error) {
      console.error('진도 기록 추가 실패:', error);
      alert('진도 기록 추가에 실패했습니다.');
    }
  };

  const calculateProgress = (current: number, target: number) => {
    return Math.min((current / target) * 100, 100);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR');
  };

  // 전체 목표 진도율 도넛 차트 데이터
  const overallProgressData = {
    labels: goals.map(goal => goal.title),
    datasets: [
      {
        data: goals.map(goal => calculateProgress(goal.current_value, goal.target_value)),
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
          '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
        ],
        borderWidth: 2,
      },
    ],
  };

  // 선택된 목표의 진도 추이 라인 차트 데이터
  const progressTrendData = {
    labels: progressLogs.map(log => formatDate(log.created_at)),
    datasets: [
      {
        label: '진도값',
        data: progressLogs.filter(log => log.value !== undefined).map(log => log.value),
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '진도 추이',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
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
        <h1 className="text-3xl font-bold text-gray-900">진도 추적</h1>
        {/* <button
          onClick={() => setIsAddingProgress(true)}
          className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg"
          disabled={!selectedGoal}
        >
          진도 기록 추가
        </button> */}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {goals.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">목표가 없습니다</h3>
          <p className="text-gray-500">먼저 목표를 생성하고 진도를 추적해보세요!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 전체 목표 진도율 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">전체 목표 진도율</h2>
            <div className="h-64">
              <Doughnut data={overallProgressData} />
            </div>
          </div>

          {/* AI 코칭 메시지 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">AI 코칭 메시지</h2>
            {coachingMessage ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-bold">AI</span>
                    </div>
                  </div>
                  <div className="ml-3">
                    <p className="text-blue-800">{coachingMessage.message}</p>
                    <p className="text-blue-600 text-sm mt-2">
                      {formatDate(coachingMessage.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">목표를 선택하면 AI 코칭 메시지를 받을 수 있습니다.</p>
            )}
          </div>

          {/* 목표 선택 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">목표 선택</h2>
            <select
              value={selectedGoal?.id || ''}
              onChange={(e) => {
                const goal = goals.find(g => g.id === e.target.value);
                setSelectedGoal(goal || null);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              {goals.map((goal) => (
                <option key={goal.id} value={goal.id}>
                  {goal.title} ({calculateProgress(goal.current_value, goal.target_value).toFixed(1)}%)
                </option>
              ))}
            </select>
            
            {selectedGoal && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium text-gray-900">{selectedGoal.title}</h3>
                <p className="text-sm text-gray-600 mt-1">{selectedGoal.description}</p>
                <div className="mt-3">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>진도</span>
                    <span>{selectedGoal.current_value} / {selectedGoal.target_value} {selectedGoal.unit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${calculateProgress(selectedGoal.current_value, selectedGoal.target_value)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 진도 추이 차트 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">진도 추이</h2>
            {progressLogs.length > 0 ? (
              <div className="h-64">
                <Line data={progressTrendData} options={chartOptions} />
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">아직 진도 기록이 없습니다.</p>
            )}
          </div>

          {/* 최근 진도 기록 */}
          <div className="bg-white p-6 rounded-lg shadow lg:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">최근 진도 기록</h2>
            {progressLogs.length > 0 ? (
              <div className="space-y-4">
                {progressLogs.slice(0, 5).map((log) => (
                  <div key={log.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className={`flex-shrink-0 w-3 h-3 rounded-full mt-2 ${
                      log.log_type === 'progress' ? 'bg-blue-500' :
                      log.log_type === 'milestone' ? 'bg-green-500' :
                      log.log_type === 'setback' ? 'bg-red-500' : 'bg-gray-500'
                    }`}></div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-gray-900">
                          {log.log_type === 'progress' ? '진도 업데이트' :
                           log.log_type === 'milestone' ? '마일스톤 달성' :
                           log.log_type === 'setback' ? '어려움' : '메모'}
                        </h4>
                        <span className="text-sm text-gray-500">{formatDate(log.created_at)}</span>
                      </div>
                      <p className="text-gray-600 mt-1">{log.description}</p>
                      {log.value !== undefined && (
                        <p className="text-sm text-gray-500 mt-1">값: {log.value}</p>
                      )}
                      {log.mood_score && (
                        <p className="text-sm text-gray-500 mt-1">기분: {log.mood_score}/10</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">아직 진도 기록이 없습니다.</p>
            )}
          </div>
        </div>
      )}

      {/* 진도 기록 추가 모달 */}
      {isAddingProgress && selectedGoal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 lg:w-1/3 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">진도 기록 추가</h3>
                <button
                  onClick={() => setIsAddingProgress(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">닫기</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handleAddProgress} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">목표</label>
                  <input
                    type="text"
                    value={selectedGoal.title}
                    disabled
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">기록 유형</label>
                  <select
                    value={progressForm.log_type}
                    onChange={(e) => setProgressForm({ ...progressForm, log_type: e.target.value as any })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="progress">진도 업데이트</option>
                    <option value="milestone">마일스톤 달성</option>
                    <option value="setback">어려움</option>
                    <option value="note">메모</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">값 ({selectedGoal.unit})</label>
                  <input
                    type="number"
                    step="any"
                    value={progressForm.value}
                    onChange={(e) => setProgressForm({ ...progressForm, value: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="선택사항"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">설명</label>
                  <textarea
                    required
                    rows={3}
                    value={progressForm.description}
                    onChange={(e) => setProgressForm({ ...progressForm, description: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="오늘의 진도나 느낀 점을 기록해주세요"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">기분 점수 (1-10)</label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={progressForm.mood_score}
                    onChange={(e) => setProgressForm({ ...progressForm, mood_score: e.target.value })}
                    className="mt-1 block w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-500 mt-1">
                    <span>나쁨</span>
                    <span>{progressForm.mood_score}</span>
                    <span>좋음</span>
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setIsAddingProgress(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    취소
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                  >
                    기록 추가
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressPage; 