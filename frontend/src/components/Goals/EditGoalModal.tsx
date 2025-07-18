import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Goal } from '../../types/goal';

interface EditGoalModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGoalUpdated: () => void;
  goal: Goal | null;
}

const EditGoalModal: React.FC<EditGoalModalProps> = ({ isOpen, onClose, onGoalUpdated, goal }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'personal' as 'health' | 'education' | 'career' | 'personal' | 'finance',
    target_value: '',
    current_value: '',
    unit: '',
    deadline: '',
    priority: 'medium' as 'high' | 'medium' | 'low'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const categories = [
    { value: 'health', label: '건강' },
    { value: 'education', label: '교육' },
    { value: 'career', label: '커리어' },
    { value: 'personal', label: '개인' },
    { value: 'finance', label: '재정' }
  ];

  const priorities = [
    { value: 'high', label: '높음' },
    { value: 'medium', label: '보통' },
    { value: 'low', label: '낮음' }
  ];

  useEffect(() => {
    if (goal) {
      setFormData({
        title: goal.title,
        description: goal.description,
        category: goal.category,
        target_value: goal.target_value.toString(),
        current_value: goal.current_value.toString(),
        unit: goal.unit,
        deadline: goal.deadline.split('T')[0], // ISO date를 YYYY-MM-DD 형식으로 변환
        priority: goal.priority
      });
    }
  }, [goal]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal) return;

    setIsLoading(true);
    setError('');

    try {
      const requestData = {
        title: formData.title,
        description: formData.description,
        category: formData.category,
        target_value: parseFloat(formData.target_value),
        current_value: parseFloat(formData.current_value),
        unit: formData.unit,
        deadline: new Date(formData.deadline).toISOString(),
        priority: formData.priority
      };

      await axios.put(`/api/goals/${goal.id}`, requestData);
      
      onGoalUpdated();
      onClose();
    } catch (error: any) {
      console.error('목표 수정 실패:', error);
      setError('목표 수정에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen || !goal) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 xl:w-1/3 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">목표 수정</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <span className="sr-only">닫기</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">제목</label>
              <input
                type="text"
                name="title"
                required
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                value={formData.title}
                onChange={handleChange}
                placeholder="목표 제목을 입력하세요"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">설명</label>
              <textarea
                name="description"
                required
                rows={3}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                value={formData.description}
                onChange={handleChange}
                placeholder="목표에 대한 자세한 설명을 입력하세요"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">카테고리</label>
                <select
                  name="category"
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  value={formData.category}
                  onChange={handleChange}
                >
                  {categories.map((category) => (
                    <option key={category.value} value={category.value}>
                      {category.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">우선순위</label>
                <select
                  name="priority"
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  value={formData.priority}
                  onChange={handleChange}
                >
                  {priorities.map((priority) => (
                    <option key={priority.value} value={priority.value}>
                      {priority.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">목표값</label>
                <input
                  type="number"
                  name="target_value"
                  required
                  min="0"
                  step="any"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  value={formData.target_value}
                  onChange={handleChange}
                  placeholder="목표값"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">현재값</label>
                <input
                  type="number"
                  name="current_value"
                  required
                  min="0"
                  step="any"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  value={formData.current_value}
                  onChange={handleChange}
                  placeholder="현재값"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">단위</label>
                <input
                  type="text"
                  name="unit"
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  value={formData.unit}
                  onChange={handleChange}
                  placeholder="kg, 개, 시간 등"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">목표 달성 기한</label>
              <input
                type="date"
                name="deadline"
                required
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                value={formData.deadline}
                onChange={handleChange}
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                취소
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '수정 중...' : '목표 수정'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditGoalModal; 