// Hand-written mirrors of backend/models/schemas.py — keep both in sync.
export type Status = "publicado" | "rascunho" | "arquivado";
export type ContentType = "video" | "pdf" | "livro" | "artigo" | "resumo" | "questao" | "flashcard" | "mapa" | "material";
export type Difficulty = "" | "facil" | "medio" | "dificil";

export interface Message { message: string }

export interface Me {
  id: string; name: string; email: string; cpf_masked: string; role: string; status: string;
  daily_goal_minutes: number; course_id: string | null; faculty: string; avatar_url: string; ranking_opt_in: boolean;
  created_at: string; trial_started_at?: string | null; trial_ends_at?: string | null; plan: "free" | "premium"; trial_active: boolean; trial_days_left: number;
}

export interface CourseIn { name: string; description: string; icon: string; num_periods: number; status: Status }
export interface Course extends CourseIn { id: string; slug: string }
export interface PeriodIn { course_id: string; number: number; name: string }
export interface Period extends PeriodIn { id: string; slug: string }
export interface DisciplineIn { period_id: string; name: string; description: string; status: Status }
export interface Discipline extends DisciplineIn { id: string; course_id: string; slug: string }
export interface TopicIn { discipline_id: string; name: string; description: string; status: Status }
export interface Topic extends TopicIn { id: string; course_id: string; period_id: string; slug: string }

export interface MindNode { label: string; children: MindNode[] }

export interface ContentData {
  // video
  url?: string; channel?: string; thumbnail?: string; video_id?: string;
  link_status?: "funcionando" | "indisponivel" | "verificar"; checked_at?: string;
  // pdf / livro / artigo
  pdf_url?: string; file_name?: string; authors?: string; year?: string; publisher?: string; isbn?: string;
  journal?: string; doi?: string; abstract?: string; keywords?: string;
  // resumo / material
  body?: string;
  // questao
  options?: string[]; correct_index?: number; explanation?: string;
  // flashcard
  front?: string; back?: string;
  // mapa
  root?: MindNode;
}

export interface ContentIn {
  type: ContentType; title: string; description: string; topic_id: string; tags: string[];
  difficulty: Difficulty; status: Status; data: ContentData;
}
export interface Content extends ContentIn {
  id: string; course_id: string; period_id: string; discipline_id: string;
  course_name: string; period_name: string; discipline_name: string; topic_name: string;
  path: string; views: number; locked: boolean; created_at: string; updated_at: string;
}

export interface PeriodWithDisciplines extends Period { disciplines: Discipline[] }
export interface CourseDetail { course: Course; periods: PeriodWithDisciplines[] }
export interface DisciplineDetail { course: Course; period: Period; discipline: Discipline; topics: Topic[] }
export interface TopicDetail {
  course: Course; period: Period; discipline: Discipline; topic: Topic; contents: Content[];
  completed: boolean; favorite_ids: string[];
}
export interface TopicHit { id: string; name: string; discipline_name: string; course_name: string; path: string }
export interface SearchOut {
  items: Content[]; total: number; page: number; pages: number; counts: Record<string, number>; topics: TopicHit[];
}

export interface HistoryItem { topic_id: string; topic_name: string; discipline_name: string; course_name: string; path: string; at: string }
export interface Achievement { id: string; title: string; description: string; unlocked: boolean }
export interface DayStat { date: string; minutes: number }
export interface ProgressOut {
  points: number; streak_days: number; minutes_total: number; month_minutes: number; month_study_days: number; minutes_today: number; daily_goal_minutes: number;
  topics_completed: number; disciplines_studied: number; questions_answered: number; correct_rate: number;
  exams_taken: number; achievements: Achievement[]; week: DayStat[]; month: DayStat[];
}
export interface ExamPlan {
  id: string; title: string; exam_date: string; discipline_id: string; discipline_name: string;
  days_left: number; progress_pct: number; topics_total: number; topics_completed: number;
  topics_in_progress: number; topics_pending: number; questions_to_practice: number; revisions: number;
  mock_exams: number; daily_minutes: number; today_topic: string; today_discipline: string; created_at: string;
}

export interface ExamTask {
  id: string; exam_plan_id: string; task_date: string; kind: "topic" | "questions" | "review";
  title: string; topic_id: string | null; topic_name: string | null; discipline_name: string;
  minutes: number; completed: boolean; completed_at: string | null;
}

export interface StudySession {
  id: string; task_id: string | null; topic_id: string | null; content_id: string | null; started_at: string; ended_at: string | null;
  last_heartbeat_at?: string | null; seconds: number; status: "em_andamento" | "finalizado";
}

export interface HomeOut {
  continue_studying: HistoryItem[]; courses: Course[]; videos: Content[]; articles: Content[];
  recommended: Content[]; progress: ProgressOut; upcoming_exam?: ExamPlan | null;
}

export type UserItemKind = "flashcards" | "mapa" | "resumo" | "plano" | "pdf" | "questoes";
export interface Flashcard { id: string; front: string; back: string; known: boolean }
export interface QuizQuestion { statement: string; options: string[]; correct_index: number; explanation: string }
export interface UserItemData {
  cards?: Flashcard[]; root?: MindNode; body?: string; filename?: string; chars?: number;
  questions?: QuizQuestion[]; source?: string;
}
export interface UserItemIn { kind: UserItemKind; title: string; topic_id: string | null; data: UserItemData }
export interface UserItem extends UserItemIn { id: string; topic_name: string; created_at: string; updated_at: string }

export interface ExamStartIn {
  source: "banco" | "item"; course_id: string | null; discipline_id: string | null; topic_id: string | null;
  difficulty: Difficulty; count: number; item_id: string | null; mode?: "estudo" | "prova"; shuffle_questions?: boolean; shuffle_options?: boolean;
}
export interface ExamQuestion {
  statement: string; options: string[]; difficulty: string;
  correct_index: number | null; explanation: string | null; chosen: number | null;
}
export interface Exam {
  id: string; title: string; status: "em_andamento" | "finalizado"; questions: ExamQuestion[];
  correct: number; total: number; score: number | null; mode?: "estudo" | "prova"; duration_seconds?: number; created_at: string; finished_at: string | null;
}

export type SubmissionStatus = "pendente" | "em_analise" | "aprovado" | "publicado" | "rejeitado";
export interface SubmissionIn { kind: "resumo" | "mapa" | "questao" | "material"; title: string; body: string; topic_id: string }
export interface Submission extends SubmissionIn {
  id: string; user_name: string; topic_name: string; status: SubmissionStatus; reviewer_note: string; created_at: string;
}


export interface NamedCount { label: string; count: number }
export interface TopContent { id: string; title: string; type: string; views: number }
export interface AdminStats {
  users: number; active_users: number; courses: number; periods: number;
  disciplines: number; topics: number; contents_by_type: Record<string, number>; pending_submissions: number;
  exams: number; top_searches: NamedCount[]; top_contents: TopContent[];
}
export interface AdminUser {
  id: string; name: string; email_masked: string; role: string; status: string; plan: "free" | "mensal" | "ilimitado" | "limitado"; created_at: string; last_login_at: string | null;
}
export interface AdminLog { id: string; admin_name: string; action: string; entity: string; entity_id: string; at: string }
export interface ContentPage { items: Content[]; total: number; page: number; pages: number }
export interface StripeSettings {
  enabled: boolean; mode: "test" | "live"; publishable_key: string; secret_key: string;
  secret_key_configured: boolean; monthly_price_id: string; yearly_price_id: string;
  currency: string; monthly_price: string; yearly_price: string; webhook_secret: string; webhook_secret_configured: boolean;
}
export interface PlanFeatures {
  pdf: boolean; videoaulas: boolean; materiais: boolean; artigos: boolean; flashcards: boolean; mapas: boolean;
  questoes: boolean; simulados: boolean; campus_ai: boolean; ranking: boolean; anotacoes: boolean; favoritos: boolean; relatorios: boolean;
}
export interface Settings {
  platform_name: string; support_email: string; default_daily_goal_minutes: number; allow_registration: boolean;
  stripe: StripeSettings; features: { limitado: PlanFeatures; ilimitado: PlanFeatures };
  updated_at: string | null; updated_by: string;
}
export interface StripeCheckoutOut { url: string }
export interface StripePublicConfig { enabled: boolean; mode: "test" | "live"; publishable_key: string; monthly_price_id: string; yearly_price_id: string; currency: string; monthly_price: string; yearly_price: string; configured: boolean }
export interface StripeSubscriptionAdmin { subscription_id: string; user_id: string; plan: string; status: string; current_period_end?: number | null; created_at: string; updated_at: string; }
export interface SmartSearchResult { type: "course" | "discipline" | "topic" | "ai" | "search"; path: string; query: string; course: string; period: string; discipline: string; topic: string }
export interface AdminStudent { id:string; name:string; email:string; cpf_masked:string; role:string; status:string; plan:"limitado"|"ilimitado"; created_at:string; last_login_at:string|null; ranking_opt_in:boolean; access_grants:any[] }
export interface Note { id:string; title:string; body:string; content_id:string|null; topic_id:string|null; created_at:string; updated_at:string }
export interface StudyPlanTask { id:string; date:string; title:string; discipline_name:string; topic_name:string|null; minutes:number; completed:boolean; kind:string }
export interface StudyPlan { tasks:StudyPlanTask[]; pending_minutes:number; message:string }
export interface Notification { id:string; title:string; body:string; kind:string; read:boolean; created_at:string }
export interface RankingEntry { position:number; id:string; name:string; points:number; minutes:number; course_name:string; faculty:string; avatar_url:string; is_me:boolean }

export interface ResourceResult { title:string; url:string; source:string; kind:string; language:string; description:string; verified?: boolean; open_access?: boolean }
export interface ResourceSearchOut { results:ResourceResult[]; query:string; note:string }

export interface PersonalStudyPlan { id:string; title:string; days:string[]; start_time:string; minutes_per_session:number; discipline_ids:string[]; topic_ids:string[]; course_id:string|null; period_id:string|null; created_at:string; updated_at:string }
export interface PersonalStudyPlanTask { id:string; plan_id:string; date:string; title:string; discipline_name:string; topic_name:string; discipline_id:string|null; topic_id:string|null; start_time:string; minutes:number; completed:boolean; completed_at:string|null }
export interface PersonalStudyPlanOut { plan:PersonalStudyPlan; tasks:PersonalStudyPlanTask[] }
export interface WeeklyGoal { id:string; week_start:string; minutes:number; topics:number; questions:number; tasks:number; progress_minutes:number; progress_topics:number; progress_questions:number; progress_tasks:number; created_at:string; updated_at:string }
export interface CalendarEvent { id:string; date:string; title:string; kind:string; minutes:number; completed:boolean; path:string }
export interface ReviewItem { id:string; topic_id:string; topic_name:string; discipline_name:string; course_name:string; due_date:string; interval_days:number; completed:boolean; completed_at:string|null }
export interface StudyHistoryEvent { id:string; kind:string; title:string; subtitle:string; date:string; path:string }
export interface GlobalSearchItem { id:string; kind:string; title:string; subtitle:string; path:string; created_at?:string|null }
