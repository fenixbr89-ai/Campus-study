"""Pydantic v2 models. Every model here has a hand-written TS twin in frontend/src/lib/types.ts."""

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


def new_id() -> str:
    return str(uuid.uuid4())


Status = Literal["publicado", "rascunho", "arquivado"]
ContentType = Literal["video", "pdf", "livro", "artigo", "resumo", "questao", "material"]
Difficulty = Literal["", "facil", "medio", "dificil"]


class Message(BaseModel):
    message: str


# ---------- auth ----------
class RegisterIn(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    cpf: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str
    accept_terms: bool
    accept_privacy: bool


class LoginIn(BaseModel):
    cpf: str
    password: str


class AdminLoginIn(BaseModel):
    cpf: str
    password: str


class ForgotIn(BaseModel):
    cpf: str


class ResetIn(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str


class ProfileIn(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    daily_goal_minutes: int = Field(ge=0)
    course_id: Optional[str] = None
    faculty: str = Field(default="", max_length=180)
    avatar_url: str = Field(default="", max_length=500)
    ranking_opt_in: bool = True


class Me(BaseModel):
    id: str
    name: str
    email: str
    cpf_masked: str
    role: str
    status: str
    daily_goal_minutes: int = 60
    course_id: Optional[str] = None
    faculty: str = ""
    avatar_url: str = ""
    ranking_opt_in: bool = True
    created_at: datetime
    trial_started_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    plan: Literal["free", "premium"] = "free"
    trial_active: bool = False
    trial_days_left: int = 0


# ---------- academic hierarchy ----------
class CourseIn(BaseModel):
    name: str = Field(min_length=2)
    description: str = ""
    icon: str = "GraduationCap"
    num_periods: int = Field(ge=1, le=16)
    status: Status = "publicado"


class Course(CourseIn):
    id: str = Field(default_factory=new_id)
    slug: str


class PeriodIn(BaseModel):
    course_id: str
    number: int = Field(ge=1, le=16)
    name: str = ""


class Period(PeriodIn):
    id: str = Field(default_factory=new_id)
    slug: str


class DisciplineIn(BaseModel):
    period_id: str
    name: str = Field(min_length=2)
    description: str = ""
    status: Status = "publicado"


class Discipline(DisciplineIn):
    id: str = Field(default_factory=new_id)
    course_id: str
    slug: str


class TopicIn(BaseModel):
    discipline_id: str
    name: str = Field(min_length=2)
    description: str = ""
    status: Status = "publicado"


class Topic(TopicIn):
    id: str = Field(default_factory=new_id)
    course_id: str
    period_id: str
    slug: str


class ContentIn(BaseModel):
    type: ContentType
    title: str = Field(min_length=2)
    description: str = ""
    topic_id: str
    tags: list[str] = []
    difficulty: Difficulty = ""
    status: Status = "publicado"
    data: dict[str, Any] = {}


class Content(ContentIn):
    id: str = Field(default_factory=new_id)
    course_id: str
    period_id: str
    discipline_id: str
    course_name: str = ""
    period_name: str = ""
    discipline_name: str = ""
    topic_name: str = ""
    path: str = ""
    views: int = 0
    locked: bool = False
    created_at: datetime
    updated_at: datetime


class PeriodWithDisciplines(Period):
    disciplines: list[Discipline] = []


class CourseDetail(BaseModel):
    course: Course
    periods: list[PeriodWithDisciplines]


class DisciplineDetail(BaseModel):
    course: Course
    period: Period
    discipline: Discipline
    topics: list[Topic]
    contents: list[Content] = []


class TopicDetail(BaseModel):
    course: Course
    period: Period
    discipline: Discipline
    topic: Topic
    contents: list[Content]
    completed: bool = False
    favorite_ids: list[str] = []


class TopicHit(BaseModel):
    id: str
    name: str
    discipline_name: str
    course_name: str
    path: str


class SearchOut(BaseModel):
    items: list[Content]
    total: int
    page: int
    pages: int
    counts: dict[str, int]
    topics: list[TopicHit]


# ---------- study ----------
class HistoryItem(BaseModel):
    topic_id: str
    topic_name: str
    discipline_name: str
    course_name: str
    path: str
    at: datetime


class Achievement(BaseModel):
    id: str
    title: str
    description: str
    unlocked: bool


class DayStat(BaseModel):
    date: str
    minutes: int


class ProgressOut(BaseModel):
    points: int
    streak_days: int
    minutes_total: int
    month_minutes: int = 0
    month_study_days: int = 0
    minutes_today: int
    daily_goal_minutes: int
    topics_completed: int
    disciplines_studied: int
    questions_answered: int
    correct_rate: float
    exams_taken: int
    achievements: list[Achievement]
    week: list[DayStat]
    month: list[DayStat] = []


class ExamPlanIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    exam_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    discipline_id: str = Field(min_length=1)


class ExamPlanUpdateIn(ExamPlanIn):
    pass


class ExamPlan(BaseModel):
    id: str
    title: str
    exam_date: str
    discipline_id: str
    discipline_name: str
    days_left: int
    progress_pct: int
    topics_total: int
    topics_completed: int
    topics_in_progress: int
    topics_pending: int
    questions_to_practice: int
    revisions: int
    mock_exams: int
    daily_minutes: int
    today_topic: str
    today_discipline: str
    created_at: datetime


class ExamTask(BaseModel):
    id: str
    exam_plan_id: str
    task_date: str
    kind: Literal["topic", "questions", "review"]
    title: str
    topic_id: Optional[str] = None
    topic_name: Optional[str] = None
    discipline_name: str
    minutes: int
    completed: bool
    completed_at: Optional[datetime] = None


class StudySessionStartIn(BaseModel):
    task_id: Optional[str] = None
    topic_id: Optional[str] = None
    content_id: Optional[str] = None


class StudySession(BaseModel):
    id: str
    task_id: Optional[str] = None
    topic_id: Optional[str] = None
    content_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None
    seconds: int
    status: Literal["em_andamento", "finalizado"]


class HomeOut(BaseModel):
    continue_studying: list[HistoryItem]
    courses: list[Course]
    videos: list[Content]
    articles: list[Content]
    recommended: list[Content]
    progress: ProgressOut
    upcoming_exam: Optional[ExamPlan] = None


class FavoriteIn(BaseModel):
    content_id: str


UserItemKind = Literal["resumo", "plano", "pdf", "questoes"]


class UserItemIn(BaseModel):
    kind: UserItemKind
    title: str = Field(min_length=1, max_length=200)
    topic_id: Optional[str] = None
    data: dict[str, Any] = {}


class UserItem(UserItemIn):
    id: str = Field(default_factory=new_id)
    topic_name: str = ""
    created_at: datetime
    updated_at: datetime


class ExamStartIn(BaseModel):
    source: Literal["banco", "item"] = "banco"
    course_id: Optional[str] = None
    discipline_id: Optional[str] = None
    topic_id: Optional[str] = None
    difficulty: Difficulty = ""
    count: int = Field(10, ge=1, le=50)
    item_id: Optional[str] = None
    mode: Literal["estudo", "prova"] = "prova"
    shuffle_questions: bool = True
    shuffle_options: bool = True


class ExamQuestion(BaseModel):
    statement: str
    options: list[str]
    difficulty: str = ""
    correct_index: Optional[int] = None
    explanation: Optional[str] = None
    chosen: Optional[int] = None


class Exam(BaseModel):
    id: str
    title: str
    status: Literal["em_andamento", "finalizado"]
    questions: list[ExamQuestion]
    correct: int = 0
    total: int
    score: Optional[float] = None
    mode: Literal["estudo", "prova"] = "prova"
    duration_seconds: int = 0
    created_at: datetime
    finished_at: Optional[datetime] = None


class ExamSubmitIn(BaseModel):
    answers: list[int]
    duration_seconds: int = Field(default=0, ge=0, le=86400)


class SubmissionIn(BaseModel):
    kind: Literal["resumo", "questao", "material"]
    title: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=10, max_length=20000)
    topic_id: str


class Submission(SubmissionIn):
    id: str = Field(default_factory=new_id)
    user_name: str = ""
    topic_name: str = ""
    status: Literal["pendente", "em_analise", "aprovado", "publicado", "rejeitado"] = "pendente"
    reviewer_note: str = ""
    created_at: datetime


# ---------- admin ----------
class NamedCount(BaseModel):
    label: str
    count: int


class TopContent(BaseModel):
    id: str
    title: str
    type: str
    views: int


class AdminStats(BaseModel):
    users: int
    active_users: int
    courses: int
    periods: int
    disciplines: int
    topics: int
    contents_by_type: dict[str, int]
    pending_submissions: int
    exams: int
    top_searches: list[NamedCount]
    top_contents: list[TopContent]


class AdminUser(BaseModel):
    id: str
    name: str
    email_masked: str
    role: str
    status: str
    plan: Literal["limitado", "ilimitado"] = "limitado"
    created_at: datetime
    last_login_at: Optional[datetime] = None


class AdminUserPatch(BaseModel):
    status: Optional[Literal["ativo", "bloqueado"]] = None
    role: Optional[Literal["student", "admin", "moderator", "editor", "superadmin"]] = None
    plan: Optional[Literal["limitado", "ilimitado"]] = None


AdminPlan = Literal["limitado", "ilimitado"]

class AdminStudent(BaseModel):
    id: str
    name: str
    email: str
    cpf_masked: str
    role: str
    status: str
    created_at: datetime
    last_login_at: Optional[datetime] = None
    ranking_opt_in: bool = False
    access_grants: list[dict[str, Any]] = []
    plan: AdminPlan = "limitado"


class StudentPasswordResetIn(BaseModel):
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class AccessGrantIn(BaseModel):
    feature: str = Field(min_length=1, max_length=120)
    months_free: int = Field(ge=1, le=24)
    note: str = Field(default="", max_length=500)


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=10000)
    content_id: Optional[str] = None
    topic_id: Optional[str] = None


class Note(NoteIn):
    id: str
    created_at: datetime
    updated_at: datetime


class StudyPlanTask(BaseModel):
    id: str
    date: str
    title: str
    discipline_name: str
    topic_name: Optional[str] = None
    minutes: int
    completed: bool
    kind: str


class StudyPlanOut(BaseModel):
    tasks: list[StudyPlanTask]
    pending_minutes: int
    message: str = ""


class PersonalStudyPlanTask(BaseModel):
    id: str
    plan_id: str
    date: str
    title: str
    discipline_name: str = ""
    topic_name: str = ""
    discipline_id: Optional[str] = None
    topic_id: Optional[str] = None
    start_time: str
    minutes: int
    completed: bool = False
    completed_at: Optional[datetime] = None


class PersonalStudyPlanIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    days: list[str] = Field(min_length=1, max_length=7)
    start_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    minutes_per_session: int = Field(default=60, ge=15, le=240)
    discipline_ids: list[str] = Field(default_factory=list, max_length=20)
    topic_ids: list[str] = Field(default_factory=list, max_length=50)


class PersonalStudyPlan(BaseModel):
    id: str
    title: str
    days: list[str]
    start_time: str
    minutes_per_session: int
    discipline_ids: list[str]
    topic_ids: list[str]
    course_id: Optional[str] = None
    period_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PersonalStudyPlanOut(BaseModel):
    plan: PersonalStudyPlan
    tasks: list[PersonalStudyPlanTask] = []


class WeeklyGoalIn(BaseModel):
    week_start: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    minutes: int = Field(default=0, ge=0, le=10080)
    topics: int = Field(default=0, ge=0, le=500)
    questions: int = Field(default=0, ge=0, le=5000)
    tasks: int = Field(default=0, ge=0, le=1000)


class WeeklyGoal(BaseModel):
    id: str
    week_start: str
    minutes: int
    topics: int
    questions: int
    progress_minutes: int = 0
    progress_topics: int = 0
    progress_questions: int = 0
    created_at: datetime
    updated_at: datetime


class CalendarEvent(BaseModel):
    id: str
    date: str
    title: str
    kind: str
    minutes: int = 0
    completed: bool = False
    path: str = ""


class CalendarOut(BaseModel):
    start: str
    end: str
    events: list[CalendarEvent]


class ReviewItem(BaseModel):
    id: str
    topic_id: str
    topic_name: str
    discipline_name: str
    course_name: str
    due_date: str
    interval_days: int
    completed: bool = False
    completed_at: Optional[datetime] = None


class StudyHistoryEvent(BaseModel):
    id: str
    kind: str
    title: str
    subtitle: str = ""
    date: datetime
    path: str = ""


class GlobalSearchItem(BaseModel):
    id: str
    kind: str
    title: str
    subtitle: str = ""
    path: str = ""
    created_at: Optional[datetime] = None


class GlobalSearchOut(BaseModel):
    query: str
    items: list[GlobalSearchItem]
    total: int


class Notification(BaseModel):
    id: str
    title: str
    body: str
    kind: str
    read: bool = False
    created_at: datetime


class RankingEntry(BaseModel):
    position: int
    name: str
    points: int
    minutes: int = 0
    course_name: str = ""
    faculty: str = ""
    avatar_url: str = ""
    is_me: bool = False



class AdminLog(BaseModel):
    id: str
    admin_name: str
    action: str
    entity: str
    entity_id: str
    at: datetime


class ContentPage(BaseModel):
    items: list[Content]
    total: int
    page: int
    pages: int


class StatusPatch(BaseModel):
    status: Status


class SubmissionPatch(BaseModel):
    status: Literal["pendente", "em_analise", "aprovado", "publicado", "rejeitado"]
    reviewer_note: str = ""


class ResourceSyncStartIn(BaseModel):
    course_id: Optional[str] = None
    period_id: Optional[str] = None
    discipline_id: Optional[str] = None
    topic_id: Optional[str] = None
    kind: Literal["todos", "pdf", "video", "artigo", "resumo"] = "todos"

class ResourceSearchIn(BaseModel):
    course: str = ""
    period: str = ""
    discipline: str = ""
    topic: str = ""
    course_id: Optional[str] = None
    period_id: Optional[str] = None
    discipline_id: Optional[str] = None
    topic_id: Optional[str] = None
    kind: Literal["todos", "pdf", "video", "artigo", "resumo"] = "todos"

class ResourceResult(BaseModel):
    title: str
    url: str
    source: str
    kind: str
    language: str = "pt-BR"
    description: str = ""
    verified: bool = False
    open_access: bool = False

class ResourceSearchOut(BaseModel):
    results: list[ResourceResult]
    query: str
    note: str = ""


# ---------- payments / platform feature access ----------
class StripeSettingsIn(BaseModel):
    enabled: bool = False
    mode: Literal["test", "live"] = "test"
    publishable_key: str = ""
    secret_key: str = ""
    monthly_price_id: str = ""
    yearly_price_id: str = ""
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    monthly_price: str = "19.90"
    yearly_price: str = "150.00"
    webhook_secret: str = ""


class StripeSettings(StripeSettingsIn):
    secret_key_configured: bool = False
    webhook_secret_configured: bool = False


class PlanFeatures(BaseModel):
    pdf: bool = True
    videoaulas: bool = True
    materiais: bool = True
    artigos: bool = True
    questoes: bool = False
    simulados: bool = False
    campus_ai: bool = True
    ranking: bool = True
    anotacoes: bool = True
    favoritos: bool = True
    relatorios: bool = True


class FeatureSettings(BaseModel):
    limitado: PlanFeatures = PlanFeatures()
    ilimitado: PlanFeatures = PlanFeatures(questoes=True, simulados=True)


class StripeCheckoutIn(BaseModel):
    plan: Literal["monthly", "yearly"]


class StripeCheckoutOut(BaseModel):
    url: str


class StripeWebhookResult(BaseModel):
    received: bool = True
    event_id: str = ""


class SettingsIn(BaseModel):
    platform_name: str = Field(min_length=1, max_length=80)
    support_email: EmailStr
    default_daily_goal_minutes: int = Field(ge=0)
    allow_registration: bool = True
    stripe: StripeSettingsIn = StripeSettingsIn()
    features: FeatureSettings = FeatureSettings()


class Settings(SettingsIn):
    updated_at: Optional[datetime] = None
    updated_by: str = ""
    stripe: StripeSettings = StripeSettings()


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    new_password_confirm: str


