"""Idempotent seed: admin account (from env) and the course/period/discipline/topic catalog.

No study materials are pre-published. Content is added manually or through the administrator AI after review.

Run: cd /app/backend && python seed.py
No YouTube links or scientific articles are created here — those must be real and are added via /admin.
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone

from lib.content import denormalize_content, period_name, period_slug, slugify
from lib.db import db, ensure_indexes
from lib.security import hash_password

# course: (num_periods, {period: {discipline: [topics]}})
CURRICULUM: dict[str, tuple[int, dict[int, dict[str, list[str]]]]] = {
    # These are representative reference curricula. Institutions may organize the
    # same degree differently; the Admin panel remains the source of truth.
}

COURSE_PERIODS: dict[str, int] = {
    "ENEM": 1,
    "Odontologia": 10, "Medicina": 12, "Enfermagem": 10, "Farmácia": 10,
    "Fisioterapia": 10, "Medicina Veterinária": 10, "Agronomia": 10, "Direito": 10,
    "Administração": 8, "Engenharia Civil": 10, "Engenharia Mecânica": 10,
    "Engenharia Elétrica": 10, "Psicologia": 10, "Biomedicina": 8, "Nutrição": 8,
    "Arquitetura e Urbanismo": 10, "Ciências Contábeis": 8, "Sistemas de Informação": 8,
    "Ciência da Computação": 8, "Pedagogia": 8, "Educação Física": 8, "Marketing": 8, "Jornalismo": 8,
}

# Ordered reference subject lists. They are intentionally broad and editable rather than
# pretending that one university's PPC is universal. Distribution across periods preserves
# the common foundation-to-professional progression of each degree.
COURSE_SUBJECTS: dict[str, list[str]] = {
    "ENEM": ["Redação", "Matemática", "Português e Linguagens", "História", "Geografia", "Filosofia", "Sociologia", "Física", "Química", "Biologia", "Inglês", "Espanhol", "Artes"],
    "Odontologia": [
        "Anatomia Humana", "Histologia e Embriologia", "Bioquímica", "Biologia Celular",
        "Fisiologia Humana", "Microbiologia", "Imunologia", "Patologia Geral",
        "Genética", "Saúde Coletiva", "Anatomia Dental", "Cariologia", "Materiais Dentários",
        "Farmacologia", "Anestesiologia Odontológica", "Radiologia Odontológica", "Periodontia",
        "Dentística", "Prótese Dentária", "Endodontia", "Cirurgia Odontológica", "Odontopediatria",
        "Ortodontia", "Estomatologia", "Odontologia Legal", "Implantodontia", "Clínica Integrada",
        "Urgências Odontológicas", "Prótese sobre Implantes", "TCC e Metodologia Científica",
        "Estágio Supervisionado em Odontologia", "Internato Odontológico", "Atividades Complementares",
    ],
    "Medicina": [
        "Anatomia Humana", "Histologia e Embriologia", "Biologia Celular", "Bioquímica", "Genética Médica",
        "Fisiologia", "Imunologia", "Microbiologia", "Parasitologia", "Patologia Geral", "Farmacologia",
        "Epidemiologia", "Saúde Coletiva", "Semiologia Médica", "Propedêutica Médica", "Genética Clínica",
        "Patologia Médica", "Pediatria", "Clínica Médica", "Cirurgia Geral", "Ginecologia", "Obstetrícia",
        "Cardiologia", "Pneumologia", "Gastroenterologia", "Nefrologia", "Neurologia", "Psiquiatria",
        "Endocrinologia", "Infectologia", "Dermatologia", "Ortopedia", "Urgência e Emergência",
        "Medicina de Família e Comunidade", "Bioética e Humanidades Médicas", "Internato Médico",
    ],
    "Enfermagem": [
        "Anatomia", "Histologia", "Biologia Celular", "Bioquímica", "Fisiologia", "Microbiologia",
        "Imunologia", "Parasitologia", "Genética", "Epidemiologia", "Saúde Coletiva", "Sociologia da Saúde",
        "Fundamentos de Enfermagem", "Semiologia e Semiotécnica", "Farmacologia", "Biossegurança",
        "Saúde do Adulto", "Enfermagem Médico-Cirúrgica", "Saúde da Mulher", "Saúde da Criança",
        "Saúde do Adolescente", "Saúde do Idoso", "Saúde Mental", "Enfermagem em Centro Cirúrgico",
        "Enfermagem em UTI", "Urgência e Emergência", "Gestão em Enfermagem", "Educação em Saúde",
        "Enfermagem Obstétrica", "Enfermagem Pediátrica", "Estágio Supervisionado", "TCC e Pesquisa",
    ],
    "Farmácia": [
        "Química Geral", "Química Orgânica", "Química Analítica", "Biologia Celular", "Anatomia", "Fisiologia",
        "Bioquímica", "Genética", "Microbiologia", "Imunologia", "Parasitologia", "Farmacobotânica",
        "Físico-Química", "Farmacologia", "Farmacotécnica", "Biofarmácia", "Farmacocinética", "Farmacodinâmica",
        "Controle de Qualidade", "Tecnologia Farmacêutica", "Cosmetologia", "Toxicologia", "Farmácia Hospitalar",
        "Farmácia Clínica", "Atenção Farmacêutica", "Análises Clínicas", "Hematologia", "Imunodiagnóstico",
        "Microbiologia Clínica", "Gestão Farmacêutica", "Estágio em Farmácia", "TCC e Metodologia Científica",
        "Saúde Coletiva", "Legislação Farmacêutica",
    ],
    "Fisioterapia": [
        "Anatomia Geral", "Biofísica", "Bioquímica", "Microbiologia", "Informática em Saúde", "Introdução à Fisioterapia",
        "Histologia e Embriologia", "Anatomia do Sistema Locomotor", "Fisiologia Humana", "Genética Humana",
        "Imunologia", "Parasitologia e Micologia", "Semiologia Fisioterapêutica", "Cinesiologia", "Biomecânica",
        "Fisiologia do Exercício", "Recursos Terapêuticos Manuais", "Eletrotermofototerapia", "Fisioterapia Ortopédica",
        "Fisioterapia Neurológica", "Fisioterapia Respiratória", "Fisioterapia Cardiovascular", "Fisioterapia Pediátrica",
        "Fisioterapia Geriátrica", "Fisioterapia Esportiva", "Fisioterapia em UTI", "Saúde Coletiva",
        "Fisioterapia Traumato-Ortopédica", "Fisioterapia na Saúde da Mulher", "Fisioterapia do Trabalho",
        "Estágio Supervisionado", "TCC e Pesquisa", "Gestão em Saúde", "Ética Profissional",
    ],
    "Medicina Veterinária": [
        "Anatomia Veterinária", "Histologia Veterinária", "Biologia Celular", "Bioquímica", "Genética", "Embriologia",
        "Fisiologia Veterinária", "Microbiologia Veterinária", "Imunologia", "Parasitologia Veterinária", "Patologia Geral",
        "Farmacologia Veterinária", "Epidemiologia Veterinária", "Zoologia", "Nutrição Animal", "Forragicultura",
        "Clínica Médica de Pequenos Animais", "Clínica Médica de Grandes Animais", "Cirurgia Veterinária", "Anestesiologia Veterinária",
        "Diagnóstico por Imagem", "Patologia Clínica Veterinária", "Reprodução Animal", "Obstetrícia Veterinária",
        "Inspeção de Produtos de Origem Animal", "Saúde Pública Veterinária", "Doenças Infecciosas", "Doenças Parasitárias",
        "Clínica de Equinos", "Clínica de Ruminantes", "Medicina de Animais Silvestres", "Odontologia Veterinária",
        "Gestão e Empreendedorismo", "Estágio Supervisionado", "TCC e Metodologia Científica",
    ],
    "Agronomia": [
        "Biologia Celular", "Matemática Aplicada à Agronomia", "Química", "Zoologia", "Botânica", "Física",
        "Geologia e Mineralogia", "Desenho Técnico", "Topografia", "Meteorologia e Climatologia", "Estatística",
        "Mecânica e Máquinas Agrícolas", "Fertilidade do Solo", "Edafologia", "Manejo e Conservação do Solo",
        "Fisiologia Vegetal", "Fitopatologia", "Entomologia Agrícola", "Genética e Melhoramento Vegetal", "Biotecnologia Agrícola",
        "Irrigação e Drenagem", "Manejo de Plantas Daninhas", "Olericultura", "Fruticultura", "Grandes Culturas",
        "Forragicultura", "Zootecnia Geral", "Nutrição Animal", "Economia Rural", "Administração Rural",
        "Extensão Rural", "Agroecologia", "Agricultura de Precisão", "Gestão Ambiental", "Estágio e TCC",
    ],
    "Direito": [
        "Ciência Política e Teoria Geral do Estado", "Filosofia, Ética e Cidadania", "Fundamentos da Economia", "Língua Portuguesa",
        "Introdução ao Estudo do Direito", "Teoria Geral do Direito", "Sociologia Jurídica", "História do Direito",
        "Direito Constitucional", "Direito Civil - Parte Geral", "Direito das Obrigações", "Direito dos Contratos",
        "Direito das Coisas", "Direito de Família", "Direito das Sucessões", "Direito Penal - Parte Geral",
        "Direito Penal - Parte Especial", "Processo Penal", "Processo Civil", "Direito Administrativo", "Direito Tributário",
        "Direito Empresarial", "Direito do Trabalho", "Processo do Trabalho", "Direito Internacional", "Direito do Consumidor",
        "Direito Ambiental", "Direito Digital", "Direitos Humanos", "Criminologia", "Medicina Legal", "Prática Jurídica",
        "Ética Profissional e Estatuto da OAB", "TCC e Metodologia Jurídica", "Estágio Supervisionado",
    ],
    "Administração": [
        "Teoria Geral da Administração", "Matemática", "Contabilidade Geral", "Economia", "Comunicação Empresarial", "Sociologia das Organizações",
        "Filosofia e Ética", "Estatística", "Comportamento Organizacional", "Gestão de Pessoas", "Direito Empresarial", "Marketing",
        "Administração Financeira", "Gestão de Custos", "Gestão de Operações", "Logística", "Gestão da Qualidade", "Pesquisa de Mercado",
        "Gestão de Projetos", "Planejamento Estratégico", "Gestão da Tecnologia da Informação", "Empreendedorismo", "Gestão de Processos",
        "Comércio Exterior", "Gestão de Suprimentos", "Finanças Corporativas", "Controladoria", "Gestão Pública", "Negociação",
        "Gestão de Serviços", "Responsabilidade Socioambiental", "Consultoria Organizacional", "Estágio e TCC",
    ],
    "Engenharia Civil": [
        "Cálculo I", "Geometria Analítica", "Álgebra Linear", "Desenho Técnico", "Física I", "Química", "Introdução à Engenharia",
        "Cálculo II", "Física II", "Estatística", "Programação", "Geologia de Engenharia", "Mecânica Geral", "Resistência dos Materiais I",
        "Materiais de Construção", "Topografia", "Mecânica dos Solos I", "Mecânica dos Solos II", "Hidráulica", "Hidrologia",
        "Estruturas de Concreto", "Estruturas Metálicas", "Estruturas de Madeira", "Fundações", "Instalações Hidrossanitárias",
        "Instalações Elétricas", "Pavimentação", "Transportes", "Planejamento de Obras", "Orçamento de Obras", "Gestão de Obras",
        "Saneamento", "Construção Civil", "Segurança do Trabalho", "Geoprocessamento", "Estágio Supervisionado", "TCC",
    ],
    "Engenharia Mecânica": [
        "Cálculo I", "Desenho Técnico", "Introdução à Engenharia Mecânica", "Física I", "Química Geral", "Cálculo II", "Álgebra Linear",
        "Física II", "Estatística", "Programação", "Mecânica Geral", "Resistência dos Materiais", "Materiais de Engenharia", "Termodinâmica I",
        "Termodinâmica II", "Mecânica dos Fluidos", "Transferência de Calor", "Metrologia", "Processos de Fabricação", "Elementos de Máquinas",
        "Mecânica dos Sólidos", "Vibrações Mecânicas", "Máquinas Térmicas", "Máquinas de Fluxo", "Automação Industrial", "Controle de Sistemas",
        "Projeto Mecânico", "CAD e Modelagem", "Manutenção Industrial", "Gestão da Produção", "Engenharia de Segurança", "Empreendedorismo",
        "Estágio Supervisionado", "TCC",
    ],
    "Engenharia Elétrica": [
        "Cálculo I", "Geometria Analítica", "Física I", "Química", "Introdução à Engenharia Elétrica", "Álgebra Linear", "Cálculo II",
        "Física II", "Programação", "Eletricidade e Magnetismo", "Circuitos Elétricos I", "Eletrônica Analógica", "Circuitos Elétricos II",
        "Eletrônica Digital", "Sinais e Sistemas", "Sistemas de Controle", "Máquinas Elétricas", "Instalações Elétricas", "Sistemas de Potência",
        "Conversão de Energia", "Microcontroladores", "Automação Industrial", "Instrumentação", "Telecomunicações", "Processamento Digital de Sinais",
        "Eletrônica de Potência", "Proteção de Sistemas Elétricos", "Energias Renováveis", "Eficiência Energética", "Projeto de Sistemas Elétricos",
        "Gestão e Segurança", "Estágio Supervisionado", "TCC",
    ],
    "Psicologia": [
        "História da Psicologia", "Filosofia", "Sociologia", "Antropologia", "Metodologia Científica", "Neuroanatomia", "Fisiologia Humana",
        "Psicologia do Desenvolvimento", "Teorias da Personalidade", "Processos Psicológicos Básicos", "Psicologia Social", "Psicologia da Aprendizagem",
        "Psicopatologia", "Psicologia da Saúde", "Psicologia Escolar", "Psicologia Organizacional e do Trabalho", "Avaliação Psicológica",
        "Psicometria", "Entrevista Psicológica", "Técnicas de Exame Psicológico", "Psicologia Jurídica", "Psicologia Comunitária",
        "Psicologia Hospitalar", "Aconselhamento Psicológico", "Processos Clínicos", "Psicanálise", "Terapia Cognitivo-Comportamental",
        "Abordagens Humanistas", "Psicoterapia Sistêmica", "Ética Profissional", "Políticas Públicas", "Estágio Básico", "Estágio Supervisionado", "TCC",
    ],
    "Biomedicina": [
        "Complementos de Matemática Aplicada", "Biologia Celular e Molecular", "Fundamentos de Física para Biologia", "Química Geral", "Iniciação à Pesquisa", "Morfologia",
        "Anatomia", "Bioquímica", "Histologia e Embriologia", "Genética", "Microbiologia", "Imunologia", "Parasitologia", "Fisiologia",
        "Patologia Geral", "Farmacologia", "Hematologia", "Imunohematologia", "Bioquímica Clínica", "Microbiologia Clínica", "Parasitologia Clínica",
        "Citopatologia", "Histotecnologia", "Biologia Molecular", "Genética Molecular", "Análises Clínicas", "Diagnóstico por Imagem", "Radiologia",
        "Banco de Sangue", "Toxicologia", "Estética e Saúde", "Gestão de Laboratórios", "Biossegurança", "Estágio Supervisionado", "TCC",
    ],
    "Nutrição": [
        "Anatomia", "Biologia Celular", "Bioquímica", "Química de Alimentos", "Fisiologia", "Microbiologia", "Genética", "Histologia",
        "Avaliação Nutricional", "Nutrição e Metabolismo", "Técnica Dietética", "Composição dos Alimentos", "Nutrição Humana", "Educação Alimentar",
        "Higiene e Controle de Alimentos", "Tecnologia de Alimentos", "Nutrição Clínica", "Dietoterapia", "Nutrição Materno-Infantil", "Nutrição do Adulto",
        "Nutrição do Idoso", "Nutrição Esportiva", "Nutrição Coletiva", "Saúde Pública", "Planejamento de Refeições", "Unidades de Alimentação e Nutrição",
        "Gestão em Alimentação", "Segurança Alimentar", "Estágio em Nutrição Clínica", "Estágio em Saúde Coletiva", "Estágio em UAN", "TCC",
    ],
    "Arquitetura e Urbanismo": [
        "Desenho Arquitetônico", "História da Arquitetura", "Geometria e Representação", "Materiais de Construção", "Tecnologia da Construção", "Conforto Ambiental",
        "Projeto Arquitetônico I", "Projeto Arquitetônico II", "Desenho Digital", "Topografia", "Sistemas Estruturais", "Instalações Prediais",
        "Paisagismo", "Urbanismo", "Planejamento Urbano", "Mobilidade Urbana", "Patrimônio Histórico", "Arquitetura Brasileira", "Arquitetura Contemporânea",
        "Representação 3D", "BIM", "Iluminação", "Acústica", "Sustentabilidade", "Infraestrutura Urbana", "Habitação Social", "Projeto de Interiores",
        "Paisagismo Avançado", "Legislação Urbanística", "Gestão de Obras", "Orçamento e Planejamento", "Estágio", "TCC",
    ],
    "Ciências Contábeis": [
        "Contabilidade Introdutória", "Matemática", "Economia", "Administração", "Direito Empresarial", "Comunicação Empresarial", "Estatística",
        "Contabilidade Intermediária", "Contabilidade de Custos", "Matemática Financeira", "Legislação Tributária", "Contabilidade Societária", "Auditoria",
        "Análise das Demonstrações Contábeis", "Controladoria", "Contabilidade Gerencial", "Contabilidade Pública", "Perícia Contábil", "Finanças Corporativas",
        "Sistemas de Informação Contábil", "Planejamento Tributário", "Contabilidade Internacional", "Mercado Financeiro", "Governança Corporativa", "Ética Profissional",
        "Empreendedorismo", "Gestão de Riscos", "Laboratório Contábil", "Estágio Supervisionado", "TCC", "Prática Profissional", "Atividades Complementares",
    ],
    "Sistemas de Informação": [
        "Algoritmos e Programação", "Matemática Discreta", "Fundamentos de Sistemas de Informação", "Comunicação e Expressão", "Introdução à Computação", "Arquitetura de Computadores",
        "Programação Orientada a Objetos", "Banco de Dados", "Sistemas Operacionais", "Engenharia de Software", "Estruturas de Dados", "Redes de Computadores",
        "Interação Humano-Computador", "Análise de Sistemas", "Desenvolvimento Web", "Programação para Dispositivos Móveis", "Segurança da Informação", "Computação em Nuvem",
        "Sistemas Distribuídos", "Inteligência Artificial", "Ciência de Dados", "Business Intelligence", "Gestão de Projetos de TI", "Governança de TI",
        "Auditoria de Sistemas", "DevOps", "Arquitetura de Software", "UX e Design de Produtos", "Empreendedorismo em TI", "Estágio", "TCC", "Projeto Integrador",
    ],
    "Ciência da Computação": [
        "Algoritmos e Programação", "Matemática Discreta", "Lógica Matemática", "Fundamentos de Computação", "Arquitetura de Computadores", "Cálculo", "Álgebra Linear",
        "Estruturas de Dados", "Programação Orientada a Objetos", "Banco de Dados", "Sistemas Operacionais", "Redes de Computadores", "Engenharia de Software",
        "Linguagens de Programação", "Teoria da Computação", "Compiladores", "Inteligência Artificial", "Aprendizado de Máquina", "Computação Gráfica", "Interação Humano-Computador",
        "Sistemas Distribuídos", "Segurança da Informação", "Criptografia", "Sistemas Embarcados", "Processamento de Imagens", "Ciência de Dados", "Computação em Nuvem",
        "Desenvolvimento Web", "Computação Paralela", "Robótica", "Empreendedorismo", "Projeto de Software", "Estágio", "TCC",
    ],
    "Pedagogia": [
        "Fundamentos da Educação", "História da Educação", "Filosofia da Educação", "Sociologia da Educação", "Psicologia da Educação", "Antropologia da Educação",
        "Didática", "Currículo", "Planejamento Educacional", "Políticas Públicas em Educação", "Alfabetização e Letramento", "Educação Infantil",
        "Ensino Fundamental", "Educação de Jovens e Adultos", "Educação Inclusiva", "Educação Especial", "Tecnologias Educacionais", "Avaliação da Aprendizagem",
        "Gestão Escolar", "Coordenação Pedagógica", "Metodologia do Ensino de Matemática", "Metodologia do Ensino de Língua Portuguesa", "Metodologia das Ciências",
        "Metodologia das Ciências Humanas", "Literatura Infantil", "Educação e Diversidade", "Educação Indígena", "Educação Ambiental", "Pesquisa em Educação",
        "Estágio em Educação Infantil", "Estágio em Ensino Fundamental", "Gestão Educacional", "TCC",
    ],
    "Educação Física": [
        "Anatomia", "Biologia", "História da Educação Física", "Fundamentos da Educação Física", "Fisiologia", "Psicologia", "Sociologia", "Bioquímica",
        "Cinesiologia", "Biomecânica", "Fisiologia do Exercício", "Aprendizagem Motora", "Desenvolvimento Motor", "Atletismo", "Ginástica",
        "Natação", "Esportes Coletivos", "Esportes Individuais", "Lutas", "Dança", "Recreação e Lazer", "Treinamento Esportivo", "Musculação",
        "Avaliação Física", "Prescrição de Exercícios", "Educação Física Escolar", "Inclusão e Atividade Física Adaptada", "Saúde Coletiva", "Gestão Esportiva",
        "Estágio Escolar", "Estágio em Academias", "Pesquisa e TCC", "Ética Profissional",
    ],
    "Marketing": [
        "Fundamentos de Marketing", "Administração", "Economia", "Comunicação Empresarial", "Matemática", "Estatística", "Comportamento do Consumidor",
        "Pesquisa de Mercado", "Segmentação de Mercado", "Branding", "Gestão de Marcas", "Marketing Digital", "Mídias Sociais", "SEO e SEM",
        "Marketing de Conteúdo", "Publicidade e Propaganda", "Planejamento de Campanhas", "CRM e Relacionamento", "Vendas e Negociação", "Marketing de Serviços",
        "Marketing B2B", "Marketing Internacional", "Trade Marketing", "E-commerce", "Analytics e Métricas", "Neuromarketing", "Experiência do Cliente",
        "Gestão de Produtos", "Pricing", "Estratégia de Marketing", "Empreendedorismo", "Pesquisa Aplicada", "Estágio", "TCC",
    ],
    "Jornalismo": [
        "Teorias da Comunicação", "História do Jornalismo", "Sociologia", "Filosofia", "Língua Portuguesa", "Redação Jornalística", "Fotojornalismo",
        "Radiojornalismo", "Telejornalismo", "Jornalismo Impresso", "Jornalismo Digital", "Apuração e Entrevista", "Técnicas de Reportagem",
        "Ética Jornalística", "Legislação da Comunicação", "Assessoria de Imprensa", "Jornalismo Investigativo", "Jornalismo de Dados", "Infografia",
        "Edição de Texto", "Edição de Áudio", "Edição de Vídeo", "Multimídia", "Produção para Redes Sociais", "Fact-checking", "Podcasting",
        "Comunicação Organizacional", "Empreendedorismo em Comunicação", "Projeto Experimental", "Estágio", "TCC", "Metodologia da Pesquisa",
    ],
}

TOPIC_MAP: dict[str, list[str]] = {
    "Matemática": ["Operações básicas", "Divisão", "Frações e razões", "Porcentagem", "Equações", "Funções"],
    "Teoria Geral da Administração": ["Escola Clássica", "Abordagem Humanística", "Teorias da Administração", "Estruturas organizacionais"],
    "Contabilidade Geral": ["Partidas dobradas", "Balanço patrimonial", "Demonstração do resultado", "Princípios contábeis"],
    "Direito Penal - Parte Geral": ["Princípios penais", "Teoria do crime", "Tipicidade e ilicitude", "Culpabilidade"],
    "Introdução ao Estudo do Direito": ["Fontes do Direito", "Norma jurídica", "Relações jurídicas", "Interpretação jurídica"],
    "Direito Constitucional": ["Constituição", "Direitos fundamentais", "Organização do Estado", "Controle de constitucionalidade"],
    "Algoritmos e Programação": ["Variáveis e tipos", "Estruturas condicionais", "Estruturas de repetição", "Funções e modularização"],
    "Banco de Dados": ["Modelo relacional", "SQL básico", "Normalização", "Consultas e relacionamentos"],
    "Anatomia": ["Planos anatômicos", "Sistema locomotor", "Sistema cardiovascular", "Sistema nervoso"],
    "Fisiologia": ["Homeostase", "Sistema cardiovascular", "Sistema respiratório", "Sistema renal"],
    "Bioquímica": ["Proteínas e enzimas", "Carboidratos", "Lipídios", "Metabolismo energético"],
    "Farmacologia": ["Farmacocinética", "Farmacodinâmica", "Interações medicamentosas", "Segurança medicamentosa"],
    "Marketing Digital": ["Estratégia digital", "Conteúdo", "Mídias sociais", "Métricas e conversão"],
    "Fundamentos de Marketing": ["Conceito de marketing", "Mix de marketing", "Segmentação", "Posicionamento"],
    "Redação Jornalística": ["Lide", "Pirâmide invertida", "Apuração", "Texto jornalístico"],
}

ENEM_TOPIC_MAP: dict[str, list[str]] = {
    "Redação": ["Competências da redação do ENEM", "Tese e projeto de texto", "Argumentação e repertório sociocultural", "Coesão e coerência", "Proposta de intervenção", "Temas sociais e direitos humanos"],
    "Português e Linguagens": ["Interpretação de textos", "Gêneros textuais", "Funções da linguagem", "Variação linguística", "Literatura brasileira", "Figuras de linguagem", "Coesão e coerência textual"],
    "Matemática": ["Razão, proporção e regra de três", "Porcentagem e matemática financeira", "Funções e gráficos", "Geometria plana", "Geometria espacial", "Estatística e probabilidade", "Análise combinatória", "Equações e sistemas", "Escalas e unidades de medida"],
    "História": ["Brasil Colônia", "Brasil Império", "República brasileira", "Ditadura militar e redemocratização", "Antiguidade e Idade Média", "Revoluções modernas", "Revolução Industrial", "Guerras Mundiais e Guerra Fria"],
    "Geografia": ["Cartografia e escalas", "Clima e relevo", "Biomas brasileiros", "População e migrações", "Urbanização", "Agropecuária e estrutura fundiária", "Globalização e economia", "Geopolítica e conflitos", "Energia e meio ambiente"],
    "Filosofia": ["Ética e moral", "Filosofia política", "Conhecimento e verdade", "Filosofia antiga", "Filosofia moderna", "Filosofia contemporânea"],
    "Sociologia": ["Cultura e identidade", "Trabalho e sociedade", "Desigualdade social", "Poder e política", "Movimentos sociais", "Cidadania e direitos", "Pensadores clássicos da sociologia"],
    "Física": ["Cinemática e dinâmica", "Trabalho e energia", "Hidrostática", "Termologia e calorimetria", "Ondulatória e acústica", "Óptica", "Eletricidade e circuitos", "Magnetismo"],
    "Química": ["Estrutura atômica e tabela periódica", "Ligações químicas", "Estequiometria", "Soluções e concentração", "Termoquímica", "Cinética e equilíbrio químico", "Eletroquímica", "Química orgânica", "Química ambiental"],
    "Biologia": ["Citologia", "Genética", "Evolução", "Ecologia", "Fisiologia humana", "Microbiologia e doenças", "Botânica", "Zoologia", "Biotecnologia"],
    "Inglês": ["Interpretação de textos em inglês", "Vocabulário pelo contexto", "Gêneros textuais e finalidade", "Conectores e referência textual"],
    "Espanhol": ["Interpretação de textos em espanhol", "Vocabulário pelo contexto", "Gêneros textuais e finalidade", "Conectores e referência textual"],
    "Artes": ["Arte brasileira", "Movimentos artísticos", "Arte contemporânea", "Música, teatro e dança", "Patrimônio cultural"],
}

def generic_topics(discipline: str, course: str = "") -> list[str]:
    """Build discipline-specific study headings when no curated map exists.

    These are study outlines, not official syllabus transcriptions. The discipline is
    named in each heading so unrelated subjects do not display the same generic topic list.
    """
    d = discipline.casefold()
    if any(k in d for k in ("direito", "jurídica", "jurídico", "processo penal", "processo civil", "constitucional", "tributário", "trabalho", "contratos", "criminologia", "oab")):
        aspects = ["princípios, conceitos e fontes normativas", "institutos, requisitos e classificações", "legislação aplicável e interpretação", "casos práticos e resolução de questões"]
    elif any(k in d for k in ("programação", "computação", "software", "dados", "sistemas", "redes", "algoritmos", "banco de dados", "inteligência artificial", "segurança da informação", "devops", "computadores")):
        aspects = ["conceitos e arquitetura", "métodos, ferramentas e implementação", "testes, análise de falhas e segurança", "projeto prático e avaliação de resultados"]
    elif any(k in d for k in ("engenharia", "cálculo", "física", "mecânica", "circuitos", "estruturas", "materiais", "hidráulica", "termodinâmica", "eletrônica", "topografia", "construção")):
        aspects = ["fundamentos científicos e modelos", "métodos de cálculo, projeto ou ensaio", "normas, dimensionamento e segurança", "aplicações práticas e análise de problemas"]
    elif any(k in d for k in ("agronomia", "solo", "vegetal", "agrícola", "agricultura", "zootecnia", "animal", "fitopatologia", "irrigação", "fruticultura", "forragicultura", "entomologia")):
        aspects = ["bases biológicas, ambientais e produtivas", "identificação, manejo e técnicas", "planejamento, sustentabilidade e controle", "aplicações em sistemas produtivos"]
    elif any(k in d for k in ("educação", "pedagogia", "didática", "currículo", "alfabetização", "aprendizagem", "ensino", "escolar", "literatura infantil")):
        aspects = ["fundamentos teóricos e legislação", "planejamento e estratégias de ensino", "avaliação, inclusão e diversidade", "práticas pedagógicas e reflexão"]
    elif any(k in d for k in ("marketing", "administração", "gestão", "contabilidade", "economia", "finanças", "empreendedorismo", "logística", "vendas", "negócios", "comércio", "recursos humanos")):
        aspects = ["conceitos, modelos e terminologia", "ferramentas de análise e planejamento", "decisões, indicadores e legislação", "aplicação em cenários e estudos de caso"]
    elif any(k in d for k in ("jornalismo", "comunicação", "reportagem", "fotojornalismo", "radiojornalismo", "telejornalismo", "redação", "mídias", "audiovisual", "infografia")):
        aspects = ["fundamentos, gêneros e linguagem", "pesquisa, apuração e planejamento", "produção, edição e verificação", "ética, legislação e análise crítica"]
    elif any(k in d for k in ("nutrição", "alimentos", "dietoterapia", "dietética", "alimentação", "saúde pública", "enfermagem", "fisioterapia", "odontologia", "medicina", "clínica", "cirurgia", "saúde", "anatomia", "histologia", "embriologia", "fisiologia", "bioquímica", "microbiologia", "imunologia", "parasitologia", "patologia", "genética", "farmacologia")):
        aspects = ["bases científicas e terminologia profissional", "mecanismos, avaliação e métodos", "prevenção, protocolos e segurança", "aplicações em casos e prática supervisionada"]
    else:
        aspects = ["conceitos e terminologia", "principais teorias e métodos", "aplicações práticas e análise de casos", "revisão crítica e resolução de questões"]
    return [f"{discipline}: {aspect}" for aspect in aspects]

# Matriz oficial do curso de Odontologia da UFG (PPC 2023, tabela curricular).
# Fonte: https://odonto.ufg.br/p/46183-projeto-pedagogico-do-curso-de-odontologia
ODONTOLOGIA_UFG_2023: dict[int, dict[str, list[str]]] = {
    1: {
        "Anatomia Humana Sistêmica e Segmentar": ["Planos e eixos anatômicos", "Sistema esquelético", "Sistema muscular", "Sistemas cardiovascular e respiratório"],
        "Bioquímica A": ["Água e pH", "Aminoácidos e proteínas", "Enzimas", "Carboidratos e lipídios"],
        "Histologia e Embriologia Geral A": ["Microscopia", "Biologia celular", "Tecidos básicos", "Desenvolvimento embrionário inicial"],
        "Genética A": ["DNA e RNA", "Herança genética", "Expressão gênica", "Genética humana"],
        "Introdução à Clínica Odontológica I": ["Profissão odontológica", "Ética e acolhimento", "Campos de atuação"],
        "Sociologia e Saúde": ["Determinantes sociais da saúde", "Sociedade e saúde", "Desigualdades em saúde"],
    },
    2: {
        "Histologia e Desenvolvimento Buco-Dental": ["Desenvolvimento craniofacial", "Odontogênese", "Tecidos dentários"],
        "Anatomia de Cabeça e Pescoço": ["Ossos do crânio", "Músculos da cabeça e pescoço", "Nervos cranianos", "Vascularização regional"],
        "Anatomia e Escultura Dental": ["Morfologia dos dentes", "Dentição decídua e permanente", "Escultura dental", "Oclusão básica"],
        "Microbiologia": ["Bactérias", "Vírus", "Fungos", "Microbiota oral"],
        "Biossegurança em Odontologia": ["Controle de infecção", "EPI e barreiras", "Esterilização e desinfecção"],
        "Saúde Bucal Coletiva": ["SUS e saúde bucal", "Promoção da saúde", "Políticas públicas de saúde bucal"],
        "Metodologia Científica": ["Pesquisa científica", "Busca bibliográfica", "Leitura crítica", "Ética em pesquisa"],
    },
    3: {
        "Fisiologia Humana A": ["Homeostase", "Fisiologia cardiovascular", "Fisiologia respiratória", "Fisiologia renal"],
        "Imunologia": ["Imunidade inata", "Imunidade adaptativa", "Antígenos e anticorpos", "Inflamação"],
        "Patologia Geral": ["Lesão celular", "Inflamação e reparo", "Distúrbios hemodinâmicos", "Neoplasias"],
        "Dentística I": ["Cariologia clínica", "Materiais restauradores", "Preparo cavitário", "Restaurações diretas"],
        "Controle de Infecção": ["Cadeia de transmissão", "Processamento de artigos", "Protocolos clínicos"],
        "Prevenção em Saúde Bucal": ["Flúor", "Controle do biofilme", "Educação em saúde bucal"],
        "Bioética": ["Princípios bioéticos", "Consentimento informado", "Relação profissional-paciente"],
        "Diagnóstico Bucal I": ["Anamnese odontológica", "Exame clínico", "Documentação e prontuário"],
    },
    4: {
        "Farmacologia Aplicada à Odontologia": ["Farmacocinética", "Farmacodinâmica", "Analgésicos e anti-inflamatórios", "Interações medicamentosas"],
        "Psicologia Aplicada à Odontologia": ["Comportamento do paciente", "Ansiedade odontológica", "Comunicação clínica"],
        "Patologia Bucal": ["Lesões fundamentais", "Doenças da mucosa oral", "Patologia óssea dos maxilares"],
        "Dentística II": ["Restaurações estéticas", "Adesão dentária", "Reabilitação direta"],
        "Periodontia": ["Anatomia periodontal", "Gengivite", "Periodontite", "Instrumentação periodontal"],
        "Promoção da Saúde": ["Planejamento de ações", "Educação em saúde", "Indicadores de promoção"],
        "Diagnóstico Bucal II": ["Diagnóstico diferencial", "Exames complementares", "Interpretação de imagens"],
    },
    5: {
        "Endodontia": ["Anatomia endodôntica", "Diagnóstico pulpar", "Preparo químico-mecânico", "Obturação dos canais"],
        "Clínica de Atenção Básica IA": ["Plano de tratamento integrado", "Atendimento clínico supervisionado", "Prevenção e tratamento restaurador"],
        "Prótese Dentária I": ["Princípios de prótese", "Prótese parcial removível", "Prótese fixa", "Moldagem"],
        "Cirurgia": ["Avaliação pré-operatória", "Exodontia", "Instrumentais cirúrgicos", "Cuidados pós-operatórios"],
        "Diagnóstico Bucal III": ["Diagnóstico de lesões orais", "Biópsia", "Laudos e encaminhamentos"],
    },
    6: {
        "Endodontia Clínica": ["Tratamento endodôntico", "Retratamento", "Urgências endodônticas"],
        "Odontopediatria": ["Desenvolvimento infantil", "Manejo comportamental", "Prevenção em odontopediatria"],
        "Ortodontia Infantil": ["Crescimento craniofacial", "Oclusão em dentição mista", "Maloclusões"],
        "Clínica de Atenção Básica IIA": ["Tratamento integrado de casos", "Plano clínico e acompanhamento"],
        "Prótese Dentária II": ["Reabilitação protética", "Prótese sobre implantes: fundamentos", "Ajustes e manutenção"],
        "Cirurgia Clínica": ["Cirurgia dentoalveolar", "Complicações cirúrgicas", "Manejo de pacientes sistemicamente comprometidos"],
        "Diagnóstico Bucal IV": ["Diagnóstico avançado", "Planejamento terapêutico", "Correlação clínico-radiográfica"],
    },
    7: {
        "Clínica Infantil I": ["Atendimento clínico infantil", "Dentição decídua", "Tratamento restaurador atraumático"],
        "Estágio em Clínica Integrada IA": ["Atendimento integrado supervisionado", "Planejamento de casos", "Registro clínico"],
        "Cirurgia e Traumatologia Buco-Maxilo-Facial I": ["Traumatismos faciais", "Cirurgia bucomaxilofacial", "Urgências traumáticas"],
        "Estágio na Atenção Primária em Saúde": ["Atenção primária", "Territorialização", "Atendimento odontológico no SUS"],
        "Odontologia Legal": ["Responsabilidade profissional", "Documentação odontolegal", "Identificação humana"],
    },
    8: {
        "Clínica Infantil II": ["Casos complexos em odontopediatria", "Traumatismo dentário infantil", "Atendimento de necessidades especiais"],
        "Estágio em Clínica Integrada II": ["Reabilitação integrada", "Discussão de casos", "Acompanhamento longitudinal"],
        "Orientação Profissional": ["Gestão de consultório", "Planejamento de carreira", "Legislação profissional"],
        "Epidemiologia em Saúde Bucal": ["Indicadores epidemiológicos", "Levantamentos de saúde bucal", "Vigilância em saúde"],
    },
    9: {
        "Estágio em Clínica Integrada IIIA": ["Atendimento clínico avançado", "Casos multidisciplinares", "Avaliação de resultados"],
        "Estágio Comunitário Interprofissional": ["Trabalho interprofissional", "Ações comunitárias", "Cuidado integral"],
        "Estágio em Urgências Odontológicas": ["Urgências odontológicas", "Trauma dentoalveolar", "Controle de dor e infecção"],
        "Estágio em Odontologia Coletiva": ["Planejamento coletivo", "Ações de prevenção", "Avaliação de programas"],
    },
    10: {
        "Estágio em Clínica Integrada IVA": ["Atendimento integral supervisionado", "Conclusão de planos de tratamento", "Responsabilidade clínica"],
        "Trabalho de Conclusão de Curso": ["Projeto de pesquisa", "Análise de dados", "Redação e apresentação científica"],
    },
}

# Cada disciplina tem uma única alocação por curso. Para cursos sem matriz oficial
# transcrita neste pacote, o catálogo usa uma distribuição de referência sem duplicar
# nomes entre períodos e informa a instituição de referência na descrição.
COURSE_REFERENCE_SOURCES = {
    "ENEM": "INEP — Matriz de Referência do ENEM: https://download.inep.gov.br/download/enem/matriz_referencia.pdf",
    "Odontologia": "Matriz usada como referência: UFG — PPC de Odontologia 2023: https://odonto.ufg.br/p/46183-projeto-pedagogico-do-curso-de-odontologia",
    "Medicina": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG — Currículo/PPC https://medicina.ufg.br/p/50469-curriculo-ppc",
    "Agronomia": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG — SIGAA https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/1394551",
    "Direito": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG https://direito.ufg.br/p/matriz-curricular",
    "Sistemas de Informação": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG — SIGAA https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/1394447",
    "Psicologia": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG — SIGAA https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/118142450",
    "Ciências Contábeis": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG — SIGAA https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/2112068",
    "Biomedicina": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG — SIGAA https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/2140399",
    "Jornalismo": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG — SIGAA https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/3820420",
    "Engenharia Mecânica": "Fonte oficial para conferência; matriz não transcrita integralmente neste pacote: UFG — SIGAA https://sigaa.sistemas.ufg.br/sigaa/public/curso/curriculo.jsf?id=69673272&lc=pt_BR",
}

# Alocação por período congelada em dados explícitos. Isso evita que alterações na
# quantidade/ordem das disciplinas redistribuam matérias automaticamente entre semestres.
# ATENÇÃO: exceto ENEM e Odontologia/UFG, estas grades são referências preliminares e
# precisam ser validadas contra o PPC vigente de uma instituição federal antes de serem
# divulgadas como matrizes oficiais.
COURSE_PERIOD_ASSIGNMENTS: dict[str, dict[str, list[str]]] = {
    "ENEM": {
        "1": [
            "Redação",
            "Matemática",
            "Português e Linguagens",
            "História",
            "Geografia",
            "Filosofia",
            "Sociologia",
            "Física",
            "Química",
            "Biologia",
            "Inglês",
            "Espanhol",
            "Artes"
        ]
    },
    "Odontologia": {
        "1": [
            "Anatomia Humana Sistêmica e Segmentar",
            "Bioquímica A",
            "Histologia e Embriologia Geral A",
            "Genética A",
            "Introdução à Clínica Odontológica I",
            "Sociologia e Saúde"
        ],
        "2": [
            "Histologia e Desenvolvimento Buco-Dental",
            "Anatomia de Cabeça e Pescoço",
            "Anatomia e Escultura Dental",
            "Microbiologia",
            "Biossegurança em Odontologia",
            "Saúde Bucal Coletiva",
            "Metodologia Científica"
        ],
        "3": [
            "Fisiologia Humana A",
            "Imunologia",
            "Patologia Geral",
            "Dentística I",
            "Controle de Infecção",
            "Prevenção em Saúde Bucal",
            "Bioética",
            "Diagnóstico Bucal I"
        ],
        "4": [
            "Farmacologia Aplicada à Odontologia",
            "Psicologia Aplicada à Odontologia",
            "Patologia Bucal",
            "Dentística II",
            "Periodontia",
            "Promoção da Saúde",
            "Diagnóstico Bucal II"
        ],
        "5": [
            "Endodontia",
            "Clínica de Atenção Básica IA",
            "Prótese Dentária I",
            "Cirurgia",
            "Diagnóstico Bucal III"
        ],
        "6": [
            "Endodontia Clínica",
            "Odontopediatria",
            "Ortodontia Infantil",
            "Clínica de Atenção Básica IIA",
            "Prótese Dentária II",
            "Cirurgia Clínica",
            "Diagnóstico Bucal IV"
        ],
        "7": [
            "Clínica Infantil I",
            "Estágio em Clínica Integrada IA",
            "Cirurgia e Traumatologia Buco-Maxilo-Facial I",
            "Estágio na Atenção Primária em Saúde",
            "Odontologia Legal"
        ],
        "8": [
            "Clínica Infantil II",
            "Estágio em Clínica Integrada II",
            "Orientação Profissional",
            "Epidemiologia em Saúde Bucal"
        ],
        "9": [
            "Estágio em Clínica Integrada IIIA",
            "Estágio Comunitário Interprofissional",
            "Estágio em Urgências Odontológicas",
            "Estágio em Odontologia Coletiva"
        ],
        "10": [
            "Estágio em Clínica Integrada IVA",
            "Trabalho de Conclusão de Curso"
        ]
    },
    "Medicina": {
        "1": [
            "Anatomia Humana",
            "Histologia e Embriologia",
            "Biologia Celular"
        ],
        "2": [
            "Bioquímica",
            "Genética Médica",
            "Fisiologia"
        ],
        "3": [
            "Imunologia",
            "Microbiologia",
            "Parasitologia"
        ],
        "4": [
            "Patologia Geral",
            "Farmacologia",
            "Epidemiologia"
        ],
        "5": [
            "Saúde Coletiva",
            "Semiologia Médica",
            "Propedêutica Médica"
        ],
        "6": [
            "Genética Clínica",
            "Patologia Médica",
            "Pediatria"
        ],
        "7": [
            "Clínica Médica",
            "Cirurgia Geral",
            "Ginecologia"
        ],
        "8": [
            "Obstetrícia",
            "Cardiologia",
            "Pneumologia"
        ],
        "9": [
            "Gastroenterologia",
            "Nefrologia",
            "Neurologia"
        ],
        "10": [
            "Psiquiatria",
            "Endocrinologia",
            "Infectologia"
        ],
        "11": [
            "Dermatologia",
            "Ortopedia",
            "Urgência e Emergência"
        ],
        "12": [
            "Medicina de Família e Comunidade",
            "Bioética e Humanidades Médicas",
            "Internato Médico"
        ]
    },
    "Enfermagem": {
        "1": [
            "Anatomia",
            "Histologia",
            "Biologia Celular",
            "Bioquímica"
        ],
        "2": [
            "Fisiologia",
            "Microbiologia",
            "Imunologia"
        ],
        "3": [
            "Parasitologia",
            "Genética",
            "Epidemiologia"
        ],
        "4": [
            "Saúde Coletiva",
            "Sociologia da Saúde",
            "Fundamentos de Enfermagem"
        ],
        "5": [
            "Semiologia e Semiotécnica",
            "Farmacologia",
            "Biossegurança"
        ],
        "6": [
            "Saúde do Adulto",
            "Enfermagem Médico-Cirúrgica",
            "Saúde da Mulher",
            "Saúde da Criança"
        ],
        "7": [
            "Saúde do Adolescente",
            "Saúde do Idoso",
            "Saúde Mental"
        ],
        "8": [
            "Enfermagem em Centro Cirúrgico",
            "Enfermagem em UTI",
            "Urgência e Emergência"
        ],
        "9": [
            "Gestão em Enfermagem",
            "Educação em Saúde",
            "Enfermagem Obstétrica"
        ],
        "10": [
            "Enfermagem Pediátrica",
            "Estágio Supervisionado",
            "TCC e Pesquisa"
        ]
    },
    "Farmácia": {
        "1": [
            "Química Geral",
            "Química Orgânica",
            "Química Analítica",
            "Biologia Celular"
        ],
        "2": [
            "Anatomia",
            "Fisiologia",
            "Bioquímica"
        ],
        "3": [
            "Genética",
            "Microbiologia",
            "Imunologia",
            "Parasitologia"
        ],
        "4": [
            "Farmacobotânica",
            "Físico-Química",
            "Farmacologia"
        ],
        "5": [
            "Farmacotécnica",
            "Biofarmácia",
            "Farmacocinética"
        ],
        "6": [
            "Farmacodinâmica",
            "Controle de Qualidade",
            "Tecnologia Farmacêutica",
            "Cosmetologia"
        ],
        "7": [
            "Toxicologia",
            "Farmácia Hospitalar",
            "Farmácia Clínica"
        ],
        "8": [
            "Atenção Farmacêutica",
            "Análises Clínicas",
            "Hematologia",
            "Imunodiagnóstico"
        ],
        "9": [
            "Microbiologia Clínica",
            "Gestão Farmacêutica",
            "Estágio em Farmácia"
        ],
        "10": [
            "TCC e Metodologia Científica",
            "Saúde Coletiva",
            "Legislação Farmacêutica"
        ]
    },
    "Fisioterapia": {
        "1": [
            "Anatomia Geral",
            "Biofísica",
            "Bioquímica",
            "Microbiologia"
        ],
        "2": [
            "Informática em Saúde",
            "Introdução à Fisioterapia",
            "Histologia e Embriologia"
        ],
        "3": [
            "Anatomia do Sistema Locomotor",
            "Fisiologia Humana",
            "Genética Humana",
            "Imunologia"
        ],
        "4": [
            "Parasitologia e Micologia",
            "Semiologia Fisioterapêutica",
            "Cinesiologia"
        ],
        "5": [
            "Biomecânica",
            "Fisiologia do Exercício",
            "Recursos Terapêuticos Manuais"
        ],
        "6": [
            "Eletrotermofototerapia",
            "Fisioterapia Ortopédica",
            "Fisioterapia Neurológica",
            "Fisioterapia Respiratória"
        ],
        "7": [
            "Fisioterapia Cardiovascular",
            "Fisioterapia Pediátrica",
            "Fisioterapia Geriátrica"
        ],
        "8": [
            "Fisioterapia Esportiva",
            "Fisioterapia em UTI",
            "Saúde Coletiva",
            "Fisioterapia Traumato-Ortopédica"
        ],
        "9": [
            "Fisioterapia na Saúde da Mulher",
            "Fisioterapia do Trabalho",
            "Estágio Supervisionado"
        ],
        "10": [
            "TCC e Pesquisa",
            "Gestão em Saúde",
            "Ética Profissional"
        ]
    },
    "Medicina Veterinária": {
        "1": [
            "Anatomia Veterinária",
            "Histologia Veterinária",
            "Biologia Celular",
            "Bioquímica"
        ],
        "2": [
            "Genética",
            "Embriologia",
            "Fisiologia Veterinária"
        ],
        "3": [
            "Microbiologia Veterinária",
            "Imunologia",
            "Parasitologia Veterinária",
            "Patologia Geral"
        ],
        "4": [
            "Farmacologia Veterinária",
            "Epidemiologia Veterinária",
            "Zoologia"
        ],
        "5": [
            "Nutrição Animal",
            "Forragicultura",
            "Clínica Médica de Pequenos Animais",
            "Clínica Médica de Grandes Animais"
        ],
        "6": [
            "Cirurgia Veterinária",
            "Anestesiologia Veterinária",
            "Diagnóstico por Imagem"
        ],
        "7": [
            "Patologia Clínica Veterinária",
            "Reprodução Animal",
            "Obstetrícia Veterinária",
            "Inspeção de Produtos de Origem Animal"
        ],
        "8": [
            "Saúde Pública Veterinária",
            "Doenças Infecciosas",
            "Doenças Parasitárias"
        ],
        "9": [
            "Clínica de Equinos",
            "Clínica de Ruminantes",
            "Medicina de Animais Silvestres",
            "Odontologia Veterinária"
        ],
        "10": [
            "Gestão e Empreendedorismo",
            "Estágio Supervisionado",
            "TCC e Metodologia Científica"
        ]
    },
    "Agronomia": {
        "1": [
            "Biologia Celular",
            "Matemática Aplicada à Agronomia",
            "Química",
            "Zoologia"
        ],
        "2": [
            "Botânica",
            "Física",
            "Geologia e Mineralogia"
        ],
        "3": [
            "Desenho Técnico",
            "Topografia",
            "Meteorologia e Climatologia",
            "Estatística"
        ],
        "4": [
            "Mecânica e Máquinas Agrícolas",
            "Fertilidade do Solo",
            "Edafologia"
        ],
        "5": [
            "Manejo e Conservação do Solo",
            "Fisiologia Vegetal",
            "Fitopatologia",
            "Entomologia Agrícola"
        ],
        "6": [
            "Genética e Melhoramento Vegetal",
            "Biotecnologia Agrícola",
            "Irrigação e Drenagem"
        ],
        "7": [
            "Manejo de Plantas Daninhas",
            "Olericultura",
            "Fruticultura",
            "Grandes Culturas"
        ],
        "8": [
            "Forragicultura",
            "Zootecnia Geral",
            "Nutrição Animal"
        ],
        "9": [
            "Economia Rural",
            "Administração Rural",
            "Extensão Rural",
            "Agroecologia"
        ],
        "10": [
            "Agricultura de Precisão",
            "Gestão Ambiental",
            "Estágio e TCC"
        ]
    },
    "Direito": {
        "1": [
            "Ciência Política e Teoria Geral do Estado",
            "Filosofia, Ética e Cidadania",
            "Fundamentos da Economia",
            "Língua Portuguesa"
        ],
        "2": [
            "Introdução ao Estudo do Direito",
            "Teoria Geral do Direito",
            "Sociologia Jurídica"
        ],
        "3": [
            "História do Direito",
            "Direito Constitucional",
            "Direito Civil - Parte Geral",
            "Direito das Obrigações"
        ],
        "4": [
            "Direito dos Contratos",
            "Direito das Coisas",
            "Direito de Família"
        ],
        "5": [
            "Direito das Sucessões",
            "Direito Penal - Parte Geral",
            "Direito Penal - Parte Especial",
            "Processo Penal"
        ],
        "6": [
            "Processo Civil",
            "Direito Administrativo",
            "Direito Tributário"
        ],
        "7": [
            "Direito Empresarial",
            "Direito do Trabalho",
            "Processo do Trabalho",
            "Direito Internacional"
        ],
        "8": [
            "Direito do Consumidor",
            "Direito Ambiental",
            "Direito Digital"
        ],
        "9": [
            "Direitos Humanos",
            "Criminologia",
            "Medicina Legal",
            "Prática Jurídica"
        ],
        "10": [
            "Ética Profissional e Estatuto da OAB",
            "TCC e Metodologia Jurídica",
            "Estágio Supervisionado"
        ]
    },
    "Administração": {
        "1": [
            "Teoria Geral da Administração",
            "Matemática",
            "Contabilidade Geral",
            "Economia",
            "Comunicação Empresarial"
        ],
        "2": [
            "Sociologia das Organizações",
            "Filosofia e Ética",
            "Estatística",
            "Comportamento Organizacional"
        ],
        "3": [
            "Gestão de Pessoas",
            "Direito Empresarial",
            "Marketing",
            "Administração Financeira"
        ],
        "4": [
            "Gestão de Custos",
            "Gestão de Operações",
            "Logística",
            "Gestão da Qualidade"
        ],
        "5": [
            "Pesquisa de Mercado",
            "Gestão de Projetos",
            "Planejamento Estratégico",
            "Gestão da Tecnologia da Informação"
        ],
        "6": [
            "Empreendedorismo",
            "Gestão de Processos",
            "Comércio Exterior",
            "Gestão de Suprimentos"
        ],
        "7": [
            "Finanças Corporativas",
            "Controladoria",
            "Gestão Pública",
            "Negociação"
        ],
        "8": [
            "Gestão de Serviços",
            "Responsabilidade Socioambiental",
            "Consultoria Organizacional",
            "Estágio e TCC"
        ]
    },
    "Engenharia Civil": {
        "1": [
            "Cálculo I",
            "Geometria Analítica",
            "Álgebra Linear",
            "Desenho Técnico"
        ],
        "2": [
            "Física I",
            "Química",
            "Introdução à Engenharia",
            "Cálculo II"
        ],
        "3": [
            "Física II",
            "Estatística",
            "Programação",
            "Geologia de Engenharia"
        ],
        "4": [
            "Mecânica Geral",
            "Resistência dos Materiais I",
            "Materiais de Construção"
        ],
        "5": [
            "Topografia",
            "Mecânica dos Solos I",
            "Mecânica dos Solos II",
            "Hidráulica"
        ],
        "6": [
            "Hidrologia",
            "Estruturas de Concreto",
            "Estruturas Metálicas",
            "Estruturas de Madeira"
        ],
        "7": [
            "Fundações",
            "Instalações Hidrossanitárias",
            "Instalações Elétricas"
        ],
        "8": [
            "Pavimentação",
            "Transportes",
            "Planejamento de Obras",
            "Orçamento de Obras"
        ],
        "9": [
            "Gestão de Obras",
            "Saneamento",
            "Construção Civil",
            "Segurança do Trabalho"
        ],
        "10": [
            "Geoprocessamento",
            "Estágio Supervisionado",
            "TCC"
        ]
    },
    "Engenharia Mecânica": {
        "1": [
            "Cálculo I",
            "Desenho Técnico",
            "Introdução à Engenharia Mecânica",
            "Física I"
        ],
        "2": [
            "Química Geral",
            "Cálculo II",
            "Álgebra Linear"
        ],
        "3": [
            "Física II",
            "Estatística",
            "Programação",
            "Mecânica Geral"
        ],
        "4": [
            "Resistência dos Materiais",
            "Materiais de Engenharia",
            "Termodinâmica I"
        ],
        "5": [
            "Termodinâmica II",
            "Mecânica dos Fluidos",
            "Transferência de Calor"
        ],
        "6": [
            "Metrologia",
            "Processos de Fabricação",
            "Elementos de Máquinas",
            "Mecânica dos Sólidos"
        ],
        "7": [
            "Vibrações Mecânicas",
            "Máquinas Térmicas",
            "Máquinas de Fluxo"
        ],
        "8": [
            "Automação Industrial",
            "Controle de Sistemas",
            "Projeto Mecânico",
            "CAD e Modelagem"
        ],
        "9": [
            "Manutenção Industrial",
            "Gestão da Produção",
            "Engenharia de Segurança"
        ],
        "10": [
            "Empreendedorismo",
            "Estágio Supervisionado",
            "TCC"
        ]
    },
    "Engenharia Elétrica": {
        "1": [
            "Cálculo I",
            "Geometria Analítica",
            "Física I",
            "Química"
        ],
        "2": [
            "Introdução à Engenharia Elétrica",
            "Álgebra Linear",
            "Cálculo II"
        ],
        "3": [
            "Física II",
            "Programação",
            "Eletricidade e Magnetismo"
        ],
        "4": [
            "Circuitos Elétricos I",
            "Eletrônica Analógica",
            "Circuitos Elétricos II",
            "Eletrônica Digital"
        ],
        "5": [
            "Sinais e Sistemas",
            "Sistemas de Controle",
            "Máquinas Elétricas"
        ],
        "6": [
            "Instalações Elétricas",
            "Sistemas de Potência",
            "Conversão de Energia"
        ],
        "7": [
            "Microcontroladores",
            "Automação Industrial",
            "Instrumentação",
            "Telecomunicações"
        ],
        "8": [
            "Processamento Digital de Sinais",
            "Eletrônica de Potência",
            "Proteção de Sistemas Elétricos"
        ],
        "9": [
            "Energias Renováveis",
            "Eficiência Energética",
            "Projeto de Sistemas Elétricos"
        ],
        "10": [
            "Gestão e Segurança",
            "Estágio Supervisionado",
            "TCC"
        ]
    },
    "Psicologia": {
        "1": [
            "História da Psicologia",
            "Filosofia",
            "Sociologia",
            "Antropologia"
        ],
        "2": [
            "Metodologia Científica",
            "Neuroanatomia",
            "Fisiologia Humana"
        ],
        "3": [
            "Psicologia do Desenvolvimento",
            "Teorias da Personalidade",
            "Processos Psicológicos Básicos",
            "Psicologia Social"
        ],
        "4": [
            "Psicologia da Aprendizagem",
            "Psicopatologia",
            "Psicologia da Saúde"
        ],
        "5": [
            "Psicologia Escolar",
            "Psicologia Organizacional e do Trabalho",
            "Avaliação Psicológica"
        ],
        "6": [
            "Psicometria",
            "Entrevista Psicológica",
            "Técnicas de Exame Psicológico",
            "Psicologia Jurídica"
        ],
        "7": [
            "Psicologia Comunitária",
            "Psicologia Hospitalar",
            "Aconselhamento Psicológico"
        ],
        "8": [
            "Processos Clínicos",
            "Psicanálise",
            "Terapia Cognitivo-Comportamental",
            "Abordagens Humanistas"
        ],
        "9": [
            "Psicoterapia Sistêmica",
            "Ética Profissional",
            "Políticas Públicas"
        ],
        "10": [
            "Estágio Básico",
            "Estágio Supervisionado",
            "TCC"
        ]
    },
    "Biomedicina": {
        "1": [
            "Complementos de Matemática Aplicada",
            "Biologia Celular e Molecular",
            "Fundamentos de Física para Biologia",
            "Química Geral",
            "Iniciação à Pesquisa"
        ],
        "2": [
            "Morfologia",
            "Anatomia",
            "Bioquímica",
            "Histologia e Embriologia"
        ],
        "3": [
            "Genética",
            "Microbiologia",
            "Imunologia",
            "Parasitologia",
            "Fisiologia"
        ],
        "4": [
            "Patologia Geral",
            "Farmacologia",
            "Hematologia",
            "Imunohematologia"
        ],
        "5": [
            "Bioquímica Clínica",
            "Microbiologia Clínica",
            "Parasitologia Clínica",
            "Citopatologia"
        ],
        "6": [
            "Histotecnologia",
            "Biologia Molecular",
            "Genética Molecular",
            "Análises Clínicas",
            "Diagnóstico por Imagem"
        ],
        "7": [
            "Radiologia",
            "Banco de Sangue",
            "Toxicologia",
            "Estética e Saúde"
        ],
        "8": [
            "Gestão de Laboratórios",
            "Biossegurança",
            "Estágio Supervisionado",
            "TCC"
        ]
    },
    "Nutrição": {
        "1": [
            "Anatomia",
            "Biologia Celular",
            "Bioquímica",
            "Química de Alimentos"
        ],
        "2": [
            "Fisiologia",
            "Microbiologia",
            "Genética",
            "Histologia"
        ],
        "3": [
            "Avaliação Nutricional",
            "Nutrição e Metabolismo",
            "Técnica Dietética",
            "Composição dos Alimentos"
        ],
        "4": [
            "Nutrição Humana",
            "Educação Alimentar",
            "Higiene e Controle de Alimentos",
            "Tecnologia de Alimentos"
        ],
        "5": [
            "Nutrição Clínica",
            "Dietoterapia",
            "Nutrição Materno-Infantil",
            "Nutrição do Adulto"
        ],
        "6": [
            "Nutrição do Idoso",
            "Nutrição Esportiva",
            "Nutrição Coletiva",
            "Saúde Pública"
        ],
        "7": [
            "Planejamento de Refeições",
            "Unidades de Alimentação e Nutrição",
            "Gestão em Alimentação",
            "Segurança Alimentar"
        ],
        "8": [
            "Estágio em Nutrição Clínica",
            "Estágio em Saúde Coletiva",
            "Estágio em UAN",
            "TCC"
        ]
    },
    "Arquitetura e Urbanismo": {
        "1": [
            "Desenho Arquitetônico",
            "História da Arquitetura",
            "Geometria e Representação",
            "Materiais de Construção"
        ],
        "2": [
            "Tecnologia da Construção",
            "Conforto Ambiental",
            "Projeto Arquitetônico I"
        ],
        "3": [
            "Projeto Arquitetônico II",
            "Desenho Digital",
            "Topografia"
        ],
        "4": [
            "Sistemas Estruturais",
            "Instalações Prediais",
            "Paisagismo",
            "Urbanismo"
        ],
        "5": [
            "Planejamento Urbano",
            "Mobilidade Urbana",
            "Patrimônio Histórico"
        ],
        "6": [
            "Arquitetura Brasileira",
            "Arquitetura Contemporânea",
            "Representação 3D"
        ],
        "7": [
            "BIM",
            "Iluminação",
            "Acústica",
            "Sustentabilidade"
        ],
        "8": [
            "Infraestrutura Urbana",
            "Habitação Social",
            "Projeto de Interiores"
        ],
        "9": [
            "Paisagismo Avançado",
            "Legislação Urbanística",
            "Gestão de Obras"
        ],
        "10": [
            "Orçamento e Planejamento",
            "Estágio",
            "TCC"
        ]
    },
    "Ciências Contábeis": {
        "1": [
            "Contabilidade Introdutória",
            "Matemática",
            "Economia",
            "Administração"
        ],
        "2": [
            "Direito Empresarial",
            "Comunicação Empresarial",
            "Estatística",
            "Contabilidade Intermediária"
        ],
        "3": [
            "Contabilidade de Custos",
            "Matemática Financeira",
            "Legislação Tributária",
            "Contabilidade Societária"
        ],
        "4": [
            "Auditoria",
            "Análise das Demonstrações Contábeis",
            "Controladoria",
            "Contabilidade Gerencial"
        ],
        "5": [
            "Contabilidade Pública",
            "Perícia Contábil",
            "Finanças Corporativas",
            "Sistemas de Informação Contábil"
        ],
        "6": [
            "Planejamento Tributário",
            "Contabilidade Internacional",
            "Mercado Financeiro",
            "Governança Corporativa"
        ],
        "7": [
            "Ética Profissional",
            "Empreendedorismo",
            "Gestão de Riscos",
            "Laboratório Contábil"
        ],
        "8": [
            "Estágio Supervisionado",
            "TCC",
            "Prática Profissional",
            "Atividades Complementares"
        ]
    },
    "Sistemas de Informação": {
        "1": [
            "Algoritmos e Programação",
            "Matemática Discreta",
            "Fundamentos de Sistemas de Informação",
            "Comunicação e Expressão"
        ],
        "2": [
            "Introdução à Computação",
            "Arquitetura de Computadores",
            "Programação Orientada a Objetos",
            "Banco de Dados"
        ],
        "3": [
            "Sistemas Operacionais",
            "Engenharia de Software",
            "Estruturas de Dados",
            "Redes de Computadores"
        ],
        "4": [
            "Interação Humano-Computador",
            "Análise de Sistemas",
            "Desenvolvimento Web",
            "Programação para Dispositivos Móveis"
        ],
        "5": [
            "Segurança da Informação",
            "Computação em Nuvem",
            "Sistemas Distribuídos",
            "Inteligência Artificial"
        ],
        "6": [
            "Ciência de Dados",
            "Business Intelligence",
            "Gestão de Projetos de TI",
            "Governança de TI"
        ],
        "7": [
            "Auditoria de Sistemas",
            "DevOps",
            "Arquitetura de Software",
            "UX e Design de Produtos"
        ],
        "8": [
            "Empreendedorismo em TI",
            "Estágio",
            "TCC",
            "Projeto Integrador"
        ]
    },
    "Ciência da Computação": {
        "1": [
            "Algoritmos e Programação",
            "Matemática Discreta",
            "Lógica Matemática",
            "Fundamentos de Computação",
            "Arquitetura de Computadores"
        ],
        "2": [
            "Cálculo",
            "Álgebra Linear",
            "Estruturas de Dados",
            "Programação Orientada a Objetos"
        ],
        "3": [
            "Banco de Dados",
            "Sistemas Operacionais",
            "Redes de Computadores",
            "Engenharia de Software"
        ],
        "4": [
            "Linguagens de Programação",
            "Teoria da Computação",
            "Compiladores",
            "Inteligência Artificial"
        ],
        "5": [
            "Aprendizado de Máquina",
            "Computação Gráfica",
            "Interação Humano-Computador",
            "Sistemas Distribuídos",
            "Segurança da Informação"
        ],
        "6": [
            "Criptografia",
            "Sistemas Embarcados",
            "Processamento de Imagens",
            "Ciência de Dados"
        ],
        "7": [
            "Computação em Nuvem",
            "Desenvolvimento Web",
            "Computação Paralela",
            "Robótica"
        ],
        "8": [
            "Empreendedorismo",
            "Projeto de Software",
            "Estágio",
            "TCC"
        ]
    },
    "Pedagogia": {
        "1": [
            "Fundamentos da Educação",
            "História da Educação",
            "Filosofia da Educação",
            "Sociologia da Educação",
            "Psicologia da Educação"
        ],
        "2": [
            "Antropologia da Educação",
            "Didática",
            "Currículo",
            "Planejamento Educacional"
        ],
        "3": [
            "Políticas Públicas em Educação",
            "Alfabetização e Letramento",
            "Educação Infantil",
            "Ensino Fundamental"
        ],
        "4": [
            "Educação de Jovens e Adultos",
            "Educação Inclusiva",
            "Educação Especial",
            "Tecnologias Educacionais"
        ],
        "5": [
            "Avaliação da Aprendizagem",
            "Gestão Escolar",
            "Coordenação Pedagógica",
            "Metodologia do Ensino de Matemática"
        ],
        "6": [
            "Metodologia do Ensino de Língua Portuguesa",
            "Metodologia das Ciências",
            "Metodologia das Ciências Humanas",
            "Literatura Infantil"
        ],
        "7": [
            "Educação e Diversidade",
            "Educação Indígena",
            "Educação Ambiental",
            "Pesquisa em Educação"
        ],
        "8": [
            "Estágio em Educação Infantil",
            "Estágio em Ensino Fundamental",
            "Gestão Educacional",
            "TCC"
        ]
    },
    "Educação Física": {
        "1": [
            "Anatomia",
            "Biologia",
            "História da Educação Física",
            "Fundamentos da Educação Física",
            "Fisiologia"
        ],
        "2": [
            "Psicologia",
            "Sociologia",
            "Bioquímica",
            "Cinesiologia"
        ],
        "3": [
            "Biomecânica",
            "Fisiologia do Exercício",
            "Aprendizagem Motora",
            "Desenvolvimento Motor"
        ],
        "4": [
            "Atletismo",
            "Ginástica",
            "Natação",
            "Esportes Coletivos"
        ],
        "5": [
            "Esportes Individuais",
            "Lutas",
            "Dança",
            "Recreação e Lazer"
        ],
        "6": [
            "Treinamento Esportivo",
            "Musculação",
            "Avaliação Física",
            "Prescrição de Exercícios"
        ],
        "7": [
            "Educação Física Escolar",
            "Inclusão e Atividade Física Adaptada",
            "Saúde Coletiva",
            "Gestão Esportiva"
        ],
        "8": [
            "Estágio Escolar",
            "Estágio em Academias",
            "Pesquisa e TCC",
            "Ética Profissional"
        ]
    },
    "Marketing": {
        "1": [
            "Fundamentos de Marketing",
            "Administração",
            "Economia",
            "Comunicação Empresarial",
            "Matemática"
        ],
        "2": [
            "Estatística",
            "Comportamento do Consumidor",
            "Pesquisa de Mercado",
            "Segmentação de Mercado"
        ],
        "3": [
            "Branding",
            "Gestão de Marcas",
            "Marketing Digital",
            "Mídias Sociais"
        ],
        "4": [
            "SEO e SEM",
            "Marketing de Conteúdo",
            "Publicidade e Propaganda",
            "Planejamento de Campanhas"
        ],
        "5": [
            "CRM e Relacionamento",
            "Vendas e Negociação",
            "Marketing de Serviços",
            "Marketing B2B",
            "Marketing Internacional"
        ],
        "6": [
            "Trade Marketing",
            "E-commerce",
            "Analytics e Métricas",
            "Neuromarketing"
        ],
        "7": [
            "Experiência do Cliente",
            "Gestão de Produtos",
            "Pricing",
            "Estratégia de Marketing"
        ],
        "8": [
            "Empreendedorismo",
            "Pesquisa Aplicada",
            "Estágio",
            "TCC"
        ]
    },
    "Jornalismo": {
        "1": [
            "Teorias da Comunicação",
            "História do Jornalismo",
            "Sociologia",
            "Filosofia"
        ],
        "2": [
            "Língua Portuguesa",
            "Redação Jornalística",
            "Fotojornalismo",
            "Radiojornalismo"
        ],
        "3": [
            "Telejornalismo",
            "Jornalismo Impresso",
            "Jornalismo Digital",
            "Apuração e Entrevista"
        ],
        "4": [
            "Técnicas de Reportagem",
            "Ética Jornalística",
            "Legislação da Comunicação",
            "Assessoria de Imprensa"
        ],
        "5": [
            "Jornalismo Investigativo",
            "Jornalismo de Dados",
            "Infografia",
            "Edição de Texto"
        ],
        "6": [
            "Edição de Áudio",
            "Edição de Vídeo",
            "Multimídia",
            "Produção para Redes Sociais"
        ],
        "7": [
            "Fact-checking",
            "Podcasting",
            "Comunicação Organizacional",
            "Empreendedorismo em Comunicação"
        ],
        "8": [
            "Projeto Experimental",
            "Estágio",
            "TCC",
            "Metodologia da Pesquisa"
        ]
    }
}

from curriculum_data import CURRICULA as ACADEMIC_CURRICULA, COURSE_METADATA, study_topics, make_topic_titles_unique

# Fonte única de verdade: a mesma matriz alimenta o seed do banco e o catálogo JSON.
COURSE_PERIODS = {course: max(periods) for course, periods in ACADEMIC_CURRICULA.items()}
COURSE_PERIOD_ASSIGNMENTS = {
    course: {str(period): list(disciplines) for period, disciplines in periods.items()}
    for course, periods in ACADEMIC_CURRICULA.items()
}
COURSE_REFERENCE_SOURCES = {
    course: f"{meta['institution']} — {meta['version']}. Fonte: {meta['url']}"
    for course, meta in COURSE_METADATA.items()
}

def build_curriculum() -> dict[str, tuple[int, dict[int, dict[str, list[str]]]]]:
    out: dict[str, tuple[int, dict[int, dict[str, list[str]]]]] = {}
    for course, period_map in ACADEMIC_CURRICULA.items():
        nper = max(period_map)
        raw_periods: dict[int, dict[str, list[str]]] = {i: {} for i in range(1, nper + 1)}
        for period, disciplines in period_map.items():
            for discipline in disciplines:
                if course == "ENEM":
                    topics = ENEM_TOPIC_MAP.get(discipline, study_topics(course, discipline, period))
                else:
                    topics = study_topics(course, discipline, period)
                raw_periods[period][discipline] = list(dict.fromkeys(topics))
        # Assuntos com o mesmo título em matérias/períodos diferentes recebem um rótulo
        # contextual para não parecerem cópias na navegação do aluno.
        periods = make_topic_titles_unique(raw_periods)
        out[course] = (nper, periods)
    return out

CURRICULUM = build_curriculum()

NOTE = "Grade de referência para estudo; não substitui o PPC vigente da instituição. Confirme a matriz e as ementas oficiais antes de tratar a distribuição como institucional."


def now():
    return datetime.now(timezone.utc)


async def seed_admin():
    email, pw = os.environ.get("ADMIN_EMAIL"), os.environ.get("ADMIN_PASSWORD")
    if not (email and pw):
        print("ADMIN_EMAIL/ADMIN_PASSWORD ausentes — admin não criado.")
        return
    email = email.lower().strip()
    if await db.users.find_one({"email": email}):
        await db.users.update_one({"email": email}, {"$set": {"role": "admin", "status": "ativo"}})
        return
    t = now()
    await db.users.insert_one({
        "id": str(uuid.uuid4()), "name": os.environ.get("ADMIN_NAME", "Administrador"), "email": email.lower(),
        "password_hash": hash_password(pw), "role": "admin",
        "status": "ativo", "token_version": 0, "daily_goal_minutes": 60, "course_id": None, "created_at": t,
        "last_login_at": None, "terms_version": "1.0", "privacy_version": "1.0", "terms_accepted_at": t, "privacy_accepted_at": t,
    })
    print("Admin criado.")


def topic_description(topic: str, discipline: str, course: str) -> str:
    known = {
        "Divisão": "A divisão é a operação usada para repartir uma quantidade em partes iguais e também para descobrir quantas vezes um número cabe em outro. O estudo inclui dividendo, divisor, quociente, resto, estratégias de cálculo e aplicações em problemas.",
        "Frações e razões": "Estudo das frações e razões, incluindo representação, comparação, equivalência, operações e aplicações em situações matemáticas.",
        "Porcentagem": "Estudo de porcentagens, aumentos, descontos, variações, proporções e aplicações financeiras e cotidianas.",
        "Funções": "Estudo das relações entre variáveis por meio de funções, incluindo domínio, imagem, representação gráfica e modelos de primeiro e segundo grau.",
        "Teoria do crime": "Estudo dos elementos do crime, incluindo fato típico, ilicitude e culpabilidade, com análise das principais teorias aplicadas ao Direito Penal.",
        "Fontes do Direito": "Estudo das fontes formais e materiais do Direito, sua hierarquia, produção e aplicação no sistema jurídico.",
        "Direitos fundamentais": "Estudo dos direitos e garantias fundamentais, sua proteção constitucional, limites e formas de efetivação.",
        "Modelo relacional": "Estudo da organização de dados em tabelas, chaves, relacionamentos e regras fundamentais do modelo relacional.",
        "SQL básico": "Estudo dos comandos fundamentais de SQL para consultar, inserir, atualizar e organizar dados em bancos relacionais.",
    }
    return known.get(topic, f"Roteiro de estudo de {topic}, no contexto de {discipline} no curso de {course}. Use a fonte curricular vinculada à disciplina para conferir a ementa, a bibliografia e as orientações específicas da instituição.")


async def seed_curriculum():
    for cname, (nper, periods) in CURRICULUM.items():
        slug = slugify(cname)
        course = await db.courses.find_one({"slug": slug})
        meta = COURSE_METADATA.get(cname, {
            "institution": "Referência curricular em revisão", "version": "Não informada",
            "url": "https://prograd.ufg.br/n/16175-ementas-e-matrizes",
            "status": "referencia_parcial", "note": "Conferir a matriz vigente antes de tratar como currículo oficial."
        })
        source = COURSE_REFERENCE_SOURCES.get(cname, "")
        if cname == "ENEM":
            description = ("Preparação para o ENEM organizada por matérias e assuntos, sem períodos universitários. "
                           "Roteiros de revisão alinhados às áreas e competências de referência do INEP. " + source)
        elif meta.get("status") == "trilha_nao_oficial":
            description = ("Trilha formativa independente de Marketing, organizada por módulos de estudo. "
                           "Não é uma matriz curricular oficial de graduação nem representa um PPC universitário. " + source)
        else:
            description = (f"Grade de referência de {cname}, organizada por período. "
                           f"Instituição de referência: {meta['institution']}. Matriz: {meta['version']}. "
                           f"{meta.get('note', '')} Os assuntos cadastrados são roteiros didáticos e não transcrições literais das ementas oficiais. " + source)
        curriculum_fields = {
            "curriculum_institution": meta.get("institution"),
            "curriculum_version": meta.get("version"),
            "curriculum_source_url": meta.get("url"),
            "curriculum_status": meta.get("status"),
            "curriculum_note": meta.get("note", ""),
        }
        if not course:
            course = {"id": str(uuid.uuid4()), "name": cname, "slug": slug, "description": description,
                      "icon": "GraduationCap", "num_periods": nper, "status": "publicado", **curriculum_fields}
            await db.courses.insert_one(dict(course))
        else:
            course_updates = {"num_periods": nper, "description": description, **curriculum_fields}
            if not course.get("status"): course_updates["status"] = "publicado"
            await db.courses.update_one({"id": course["id"]}, {"$set": course_updates})
        for n in range(1, nper + 1):
            if not await db.periods.find_one({"course_id": course["id"], "number": n}):
                await db.periods.insert_one({"id": str(uuid.uuid4()), "course_id": course["id"], "number": n,
                                             "name": period_name(n), "slug": period_slug(n)})
        for n, discs in periods.items():
            period = await db.periods.find_one({"course_id": course["id"], "number": n})
            for dname, topics in discs.items():
                dslug = slugify(dname)
                disc = await db.disciplines.find_one({"period_id": period["id"], "slug": dslug})
                discipline_description = (f"{dname}: roteiro de estudo específico do curso {cname}. "
                                          f"Referência: {meta.get('institution')} — {meta.get('version')}. "
                                          "Consultar a fonte curricular da disciplina para a ementa oficial.")
                discipline_meta = {"curriculum_source_url": meta.get("url"), "curriculum_version": meta.get("version"),
                                   "curriculum_institution": meta.get("institution")}
                if not disc:
                    disc = {"id": str(uuid.uuid4()), "course_id": course["id"], "period_id": period["id"], "name": dname,
                            "slug": dslug, "description": discipline_description, "status": "publicado", **discipline_meta}
                    await db.disciplines.insert_one(dict(disc))
                else:
                    updates = {"description": discipline_description, "status": "publicado", **discipline_meta}
                    await db.disciplines.update_one({"id": disc["id"]}, {"$set": updates})
                for tname in topics:
                    tslug = slugify(tname)
                    topic = await db.topics.find_one({"discipline_id": disc["id"], "slug": tslug})
                    desc = topic_description(tname, dname, cname)
                    if not topic:
                        await db.topics.insert_one({"id": str(uuid.uuid4()), "course_id": course["id"], "period_id": period["id"],
                                                    "discipline_id": disc["id"], "name": tname, "slug": tslug,
                                                    "description": desc, "status": "publicado"})
                    else:
                        updates = {"description": desc, "status": "publicado"}
                        await db.topics.update_one({"id": topic["id"]}, {"$set": updates})
    # Reconcilia o catálogo já existente: disciplina fora da matriz planejada ou
    # cadastrada em período diferente não continua publicada como duplicata.
    # Os registros são arquivados, não apagados, para preservar histórico e conteúdo.
    import unicodedata
    def norm_name(value: str) -> str:
        value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().casefold()
        return " ".join(value.replace("-", " ").split())

    for cname, (nper, planned_periods) in CURRICULUM.items():
        course = await db.courses.find_one({"slug": slugify(cname)})
        if not course:
            continue
        expected = {norm_name(dname): (number, dname) for number, entries in planned_periods.items() for dname in entries}
        all_periods = await db.periods.find({"course_id": course["id"]}, {"_id": 0}).to_list(100)
        period_numbers = {period["id"]: period["number"] for period in all_periods}
        existing = await db.disciplines.find({"course_id": course["id"]}, {"_id": 0}).to_list(5000)
        seen: set[tuple[str, int]] = set()
        for disc in existing:
            key = norm_name(disc.get("name", ""))
            actual_period = period_numbers.get(disc.get("period_id"))
            wanted = expected.get(key)
            wanted_period = wanted[0] if wanted else None
            wanted_name = wanted[1] if wanted else None
            identity = (key, actual_period or 0)
            keep = wanted_period is not None and actual_period == wanted_period and disc.get("name") == wanted_name and identity not in seen
            if keep:
                seen.add(identity)
            elif disc.get("status") != "arquivado":
                await db.disciplines.update_one({"id": disc["id"]}, {"$set": {"status": "arquivado"}})
        # Arquiva assuntos antigos que não pertencem à lista planejada da disciplina ativa.
        # Nada é apagado: os materiais associados continuam preservados para recuperação.
        for number, planned_discs in planned_periods.items():
            period = await db.periods.find_one({"course_id": course["id"], "number": number}, {"_id": 0})
            if not period:
                continue
            for dname, planned_topics in planned_discs.items():
                disc = await db.disciplines.find_one({"course_id": course["id"], "period_id": period["id"], "slug": slugify(dname)}, {"_id": 0})
                if not disc:
                    continue
                expected_topics = {norm_name(t) for t in planned_topics}
                old_topics = await db.topics.find({"discipline_id": disc["id"]}, {"_id": 0}).to_list(2000)
                for topic in old_topics:
                    if norm_name(topic.get("name", "")) not in expected_topics and topic.get("status") != "arquivado":
                        await db.topics.update_one({"id": topic["id"]}, {"$set": {"status": "arquivado"}})


async def topic_id(course: str, period: int, disc: str, topic: str) -> str:
    c = await db.courses.find_one({"slug": slugify(course)})
    p = await db.periods.find_one({"course_id": c["id"], "number": period})
    d = await db.disciplines.find_one({"period_id": p["id"], "slug": slugify(disc)})
    t = await db.topics.find_one({"discipline_id": d["id"], "slug": slugify(topic)})
    return t["id"]


async def add(content: dict):
    if await db.contents.find_one({"title": content["title"], "topic_id": content["topic_id"]}):
        return
    doc = {"description": "", "tags": [], "difficulty": "", "status": "publicado", "views": 0, "locked": False,
           "id": str(uuid.uuid4()), "created_at": now(), **content}
    await db.contents.insert_one(await denormalize_content(doc))



async def seed_content():
    """Intentionally empty: course content is created manually by administrators/AI."""
    return



async def seed_discipline_pdfs():
    """Intentionally empty: no pre-published discipline PDFs are seeded."""
    return


async def seed_resource_queries():
    """Prepare one Portuguese web-search query for every curricular topic without deleting existing content."""
    for cname, (_nper, periods) in CURRICULUM.items():
        course = await db.courses.find_one({"slug": slugify(cname)})
        if not course: continue
        for number, disciplines in periods.items():
            period = await db.periods.find_one({"course_id": course["id"], "number": number})
            if not period: continue
            for dname, topics in disciplines.items():
                disc = await db.disciplines.find_one({"period_id": period["id"], "slug": slugify(dname)})
                if not disc: continue
                for tname in topics:
                    topic = await db.topics.find_one({"discipline_id": disc["id"], "slug": slugify(tname)})
                    if not topic: continue
                    await db.resource_queries.update_one({"topic_id": topic["id"]},{"$set":{"topic_id":topic["id"],"course":cname,"period":period["name"],"discipline":dname,"topic":tname,"query":f"{cname} {period['name']} {dname} {tname} português Brasil"}},upsert=True)



async def seed_curated_resources():
    """Intentionally empty: external resources are added manually/by the admin AI."""
    return


async def main():
    await ensure_indexes()
    await seed_admin()
    await seed_curriculum()
    # The catalog structure is seeded, but its study materials remain empty.
    # Resources are created manually/by the administrator AI after review.
    await seed_resource_queries()
    print("Seed concluído:", await db.courses.count_documents({}), "cursos,", await db.topics.count_documents({}), "assuntos,",
          await db.contents.count_documents({}), "conteúdos.")

if __name__ == "__main__":
    asyncio.run(main())
