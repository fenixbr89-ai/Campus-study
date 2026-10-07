import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Course, Discipline, Period, Topic } from "@/lib/types";
import { NativeSelect } from "./SelectField";

export interface TopicSel { course_id: string; period_id: string; discipline_id: string; topic_id: string }
export const EMPTY_SEL: TopicSel = { course_id: "", period_id: "", discipline_id: "", topic_id: "" };

// Cascading Curso → Período → Disciplina → Assunto selector (public catalog endpoints).
export function TopicPicker({
  value, onChange, prefix, requireTopic = true, admin = false,
}: { value: TopicSel; onChange: (v: TopicSel) => void; prefix: string; requireTopic?: boolean; admin?: boolean }) {
  const courses = useQuery({ queryKey: [admin ? "admin-courses" : "courses"], queryFn: () => apiGet<Course[]>(admin ? "/admin/courses" : "/courses") });
  const periods = useQuery({
    queryKey: ["f-periods", value.course_id], enabled: !!value.course_id,
    queryFn: () => apiGet<Period[]>(`/filters/periods?course_id=${value.course_id}`),
  });
  const discs = useQuery({
    queryKey: [admin ? "a-discs" : "f-discs", value.period_id], enabled: !!value.period_id,
    queryFn: () => apiGet<Discipline[]>(admin ? `/admin/disciplines?period_id=${value.period_id}` : `/filters/disciplines?period_id=${value.period_id}`),
  });
  const topics = useQuery({
    queryKey: [admin ? "a-topics" : "f-topics", value.discipline_id], enabled: !!value.discipline_id,
    queryFn: () => apiGet<Topic[]>(admin ? `/admin/topics?discipline_id=${value.discipline_id}` : `/filters/topics?discipline_id=${value.discipline_id}`),
  });
  return (
    <div className="grid gap-2 sm:grid-cols-2">
      <NativeSelect testId={`${prefix}-course-select`} value={value.course_id} onChange={(v) => onChange({ ...EMPTY_SEL, course_id: v })}>
        <option value="">Curso</option>
        {courses.data?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
      </NativeSelect>
      <NativeSelect testId={`${prefix}-period-select`} disabled={!value.course_id} value={value.period_id}
        onChange={(v) => onChange({ ...value, period_id: v, discipline_id: "", topic_id: "" })}>
        <option value="">Período</option>
        {periods.data?.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
      </NativeSelect>
      <NativeSelect testId={`${prefix}-discipline-select`} disabled={!value.period_id} value={value.discipline_id}
        onChange={(v) => onChange({ ...value, discipline_id: v, topic_id: "" })}>
        <option value="">Disciplina</option>
        {discs.data?.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
      </NativeSelect>
      <NativeSelect testId={`${prefix}-topic-select`} disabled={!value.discipline_id} value={value.topic_id}
        onChange={(v) => onChange({ ...value, topic_id: v })}>
        <option value="">{requireTopic ? "Assunto" : "Assunto (opcional)"}</option>
        {topics.data?.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
      </NativeSelect>
    </div>
  );
}
