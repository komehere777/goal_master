export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string;
  category: 'health' | 'education' | 'career' | 'personal' | 'finance';
  target_value: number;
  current_value: number;
  unit: string;
  deadline: string;
  priority: 'high' | 'medium' | 'low';
  status: 'active' | 'completed' | 'paused' | 'cancelled';
  ai_analysis?: {
    difficulty_score: number;
    estimated_duration: number;
    success_probability: number;
  };
  created_at: string;
  updated_at: string;
} 