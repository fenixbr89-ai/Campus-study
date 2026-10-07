import { Link } from "react-router-dom";
import { usePageMeta } from "@/lib/hooks";
import { Brand, Footer } from "@/components/Brand";

type Section = [string, string[]];

const TERMS: Section[] = [
  ["1. Aceitação dos Termos", ["Ao criar uma conta ou utilizar o Campus Study (“Plataforma”), você declara ter lido, compreendido e aceitado estes Termos de Uso, bem como a Política de Privacidade. A versão aceita, a data e a hora do aceite ficam registradas em sua conta.", "Estes Termos são regidos pela legislação brasileira, incluindo o Código Civil, o Código de Defesa do Consumidor (Lei nº 8.078/1990), o Marco Civil da Internet (Lei nº 12.965/2014) e a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018 — LGPD)."]],
  ["2. Cadastro", ["Para criar uma conta é obrigatório informar nome completo, e-mail e senha. O e-mail é o identificador de acesso da conta.", "Você se compromete a fornecer informações verdadeiras e atualizadas. Cadastros com dados falsos ou de terceiros poderão ser suspensos."]],
  ["3. Conta e segurança", ["A conta é pessoal e intransferível. Você é responsável por manter a confidencialidade da sua senha e por todas as atividades realizadas em sua conta.", "Em caso de suspeita de uso indevido, altere sua senha imediatamente pela função “Esqueci minha senha” e comunique o suporte."]],
  ["4. Uso da plataforma", ["O Campus Study organiza materiais de estudo por curso, período, disciplina e assunto. As grades curriculares apresentadas são referências e podem variar entre instituições de ensino.", "É proibido: utilizar robôs ou meios automatizados para extrair conteúdo; tentar burlar mecanismos de segurança; compartilhar a conta; publicar conteúdo ilícito, ofensivo ou que viole direitos de terceiros."]],
  ["5. Conteúdos, videoaulas e artigos", ["As videoaulas são incorporadas a partir do YouTube e pertencem aos seus respectivos autores e canais. O Campus Study não hospeda esses vídeos e não se responsabiliza por sua remoção ou alteração pela plataforma de origem.", "Os artigos científicos são indicados com suas referências originais (autores, ano, fonte e DOI, quando disponível). O acesso ao texto integral pode depender da política do editor.", "Resumos, questões, mapas mentais e materiais têm finalidade exclusivamente educacional e não substituem a bibliografia oficial, a orientação docente ou a avaliação de profissionais habilitados."]],
  ["6. Conteúdo enviado por usuários", ["Usuários podem enviar resumos, mapas mentais, questões e materiais. Nenhum envio é publicado automaticamente: todo conteúdo passa por moderação (Pendente → Em análise → Aprovado → Publicado).", "Ao enviar conteúdo, você declara ser o autor ou possuir autorização para compartilhá-lo e concede ao Campus Study licença gratuita, não exclusiva, para exibi-lo na Plataforma. Conteúdos que violem direitos de terceiros serão removidos."]],
  ["7. Plano Limitado e Plano Ilimitado", ["Todo novo cadastro inicia diretamente no Plano Limitado, sem período de teste ou acesso gratuito temporário aos recursos do Plano Ilimitado. O usuário terá acesso apenas aos recursos disponibilizados gratuitamente na Plataforma.", "Para acessar os recursos exclusivos do Plano Ilimitado, o usuário deverá realizar a assinatura correspondente, conforme as condições e valores apresentados na Plataforma.", "O plano Ilimitado é cobrado pelo Stripe conforme o ciclo de cobrança escolhido. Em caso de falha de renovação, o acesso aos recursos exclusivos do plano poderá ser revogado quando a assinatura deixar de estar ativa."]],
  ["8. Exclusão de conta", ["Você pode solicitar a exclusão da sua conta pelos canais de suporte. Os dados serão eliminados, ressalvadas as hipóteses de guarda obrigatória previstas em lei (como registros de acesso, art. 15 do Marco Civil da Internet)."]],
  ["9. Propriedade intelectual", ["A marca Campus Study, o layout, o código e os conteúdos originais produzidos pela Plataforma são protegidos pela legislação de propriedade intelectual. Conteúdos de terceiros pertencem aos seus titulares."]],
  ["10. Responsabilidades", ["O Campus Study empenha-se para manter a Plataforma disponível e segura, mas não garante funcionamento ininterrupto. Não nos responsabilizamos por resultados acadêmicos, por conteúdos de sites de terceiros ou por indisponibilidades causadas por fatores externos."]],
  ["11. Suporte e alterações", ["Dúvidas e solicitações podem ser enviadas aos canais de suporte informados na Plataforma. Estes Termos podem ser atualizados; alterações relevantes serão comunicadas e poderão exigir novo aceite.", "Fica eleito o foro do domicílio do consumidor para dirimir eventuais controvérsias."]],
];

const PRIVACY: Section[] = [
  ["1. Quem somos", ["Esta Política explica como o Campus Study (“Controlador”) trata dados pessoais, em conformidade com a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018 — LGPD)."]],
  ["2. Dados coletados", ["Dados de cadastro: nome completo, e-mail e senha (armazenada apenas como hash criptográfico, nunca em texto puro).", "Dados da conta: versões e datas de aceite dos Termos e da Política, data de criação e último acesso.", "Dados de uso: cursos e assuntos acessados, materiais salvos, progresso, simulados, tempo de estudo e pesquisas realizadas.", "Arquivos enviados: PDFs enviados para análise e conteúdos submetidos à moderação."]],
  
  ["3. Finalidades e bases legais", ["Execução de contrato (art. 7º, V): criar e manter sua conta e fornecer as funcionalidades da Plataforma.", "Legítimo interesse (art. 7º, IX): segurança, prevenção de abuso, melhoria da Plataforma e estatísticas agregadas.", "Cumprimento de obrigação legal (art. 7º, II): guarda de registros de acesso e obrigações fiscais."]],
  ["4. Armazenamento e segurança", ["Os dados são armazenados em banco de dados protegido, com acesso restrito. Adotamos senhas com hash bcrypt, sessões em cookies httpOnly e seguros, tokens de redefinição de uso único com expiração, validação de dados, limitação de tentativas e chaves secretas mantidas apenas no servidor."]],
  ["5. Compartilhamento", ["Compartilhamos dados somente quando necessário: com o provedor de envio de e-mails transacionais (redefinição de senha), com autoridades, mediante obrigação legal. Não vendemos dados pessoais."]],
  ["6. Cookies", ["Utilizamos um cookie essencial de sessão (httpOnly) para manter você conectado. Não utilizamos cookies de publicidade."]],
  ["7. Direitos do titular", ["Você pode, a qualquer momento: confirmar a existência de tratamento; acessar seus dados; corrigir dados incompletos ou desatualizados; solicitar anonimização, bloqueio ou eliminação; solicitar portabilidade; obter informações sobre compartilhamento; revogar consentimentos; e peticionar à ANPD."]],
  ["8. Retenção e exclusão", ["Mantemos os dados enquanto a conta estiver ativa. Após pedido de exclusão, os dados são eliminados, salvo guarda obrigatória por lei (ex.: registros de acesso por 6 meses, art. 15 do Marco Civil da Internet)."]],
  ["9. Contato", ["Para exercer seus direitos ou esclarecer dúvidas sobre privacidade, entre em contato pelo e-mail campusstudyV@gmail.com. Este canal recebe solicitações relacionadas ao tratamento de dados pessoais. Esta Política pode ser atualizada, e a versão vigente estará sempre disponível nesta página."]],
];

function LegalPage({ title, version, sections, testId }: { title: string; version: string; sections: Section[]; testId: string }) {
  usePageMeta(title, `${title} do Campus Study, estruturado conforme a legislação brasileira.`);
  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-slate-200 px-5 py-4"><div className="mx-auto max-w-3xl"><Brand /></div></header>
      <article data-testid={testId} className="mx-auto max-w-3xl px-5 py-10">
        <p className="text-sm font-semibold text-brand-dark">Versão {version} · Documento preparado para revisão jurídica profissional antes do lançamento</p>
        <h1 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">{title}</h1>
        <nav className="mt-6 rounded-2xl bg-slate-50 p-4 text-sm">
          <p className="mb-2 font-semibold">Sumário</p>
          <ol className="grid gap-1 sm:grid-cols-2">{sections.map(([h]) => <li key={h}><a href={`#${h.split(".")[0]}`} className="text-slate-600 hover:text-brand-dark">{h}</a></li>)}</ol>
        </nav>
        {sections.map(([h, ps]) => (
          <section key={h} id={h.split(".")[0]} className="mt-8 scroll-mt-6">
            <h2 className="text-xl font-bold">{h}</h2>
            {ps.map((p, i) => <p key={i} className="mt-3 leading-relaxed text-slate-700">{p}</p>)}
          </section>
        ))}
        <p className="mt-10 text-sm text-slate-500"><Link to="/" className="font-semibold text-brand-dark">← Voltar ao Campus Study</Link></p>
        <Footer />
      </article>
    </div>
  );
}

export function TermsPage() {
  return <LegalPage title="Termos de Uso" version="1.1" sections={TERMS} testId="terms-page" />;
}

export function PrivacyPage() {
  return <LegalPage title="Política de Privacidade" version="1.1" sections={PRIVACY} testId="privacy-page" />;
}
