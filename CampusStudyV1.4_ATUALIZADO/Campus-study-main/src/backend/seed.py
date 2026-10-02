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
from lib.security import cpf_hash, cpf_masked, hash_password, is_valid_cpf

# course: (num_periods, {period: {discipline: [topics]}})
CURRICULUM: dict[str, tuple[int, dict[int, dict[str, list[str]]]]] = {
    # These are representative reference curricula. Institutions may organize the
    # same degree differently; the Admin panel remains the source of truth.
}

COURSE_PERIODS: dict[str, int] = {
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

def generic_topics(discipline: str) -> list[str]:
    return [f"Fundamentos de {discipline}", f"Conceitos principais de {discipline}", f"Aplicações de {discipline}"]

def build_curriculum() -> dict[str, tuple[int, dict[int, dict[str, list[str]]]]]:
    out = {}
    for course, nper in COURSE_PERIODS.items():
        subjects = COURSE_SUBJECTS.get(course, [])
        if not subjects:
            continue
        periods: dict[int, dict[str, list[str]]] = {i: {} for i in range(1, nper + 1)}
        # Spread the ordered list as evenly as possible across all semesters.
        for idx, discipline in enumerate(subjects):
            number = min(nper, (idx * nper) // len(subjects) + 1)
            topics = TOPIC_MAP.get(discipline, generic_topics(discipline))
            periods[number].setdefault(discipline, topics)
        out[course] = (nper, periods)
    return out

CURRICULUM = build_curriculum()

NOTE = "Grade de referência: a organização de períodos e disciplinas pode variar entre instituições."


def now():
    return datetime.now(timezone.utc)


async def seed_admin():
    cpf, email, pw = os.environ.get("ADMIN_CPF"), os.environ.get("ADMIN_EMAIL"), os.environ.get("ADMIN_PASSWORD")
    if not (cpf and email and pw) or not is_valid_cpf(cpf):
        print("ADMIN_CPF/ADMIN_EMAIL/ADMIN_PASSWORD ausentes ou inválidos — admin não criado.")
        return
    h = cpf_hash(cpf)
    if await db.users.find_one({"cpf_hash": h}):
        await db.users.update_one({"cpf_hash": h}, {"$set": {"role": "admin", "status": "ativo"}})
        return
    t = now()
    await db.users.insert_one({
        "id": str(uuid.uuid4()), "name": os.environ.get("ADMIN_NAME", "Administrador"), "email": email.lower(),
        "cpf_hash": h, "cpf_masked": cpf_masked(cpf), "password_hash": hash_password(pw), "role": "admin",
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
    return known.get(topic, f"Neste conteúdo de {discipline}, o estudante aborda {topic}, seus conceitos fundamentais, principais aplicações e relações com os demais assuntos do curso de {course}.")


async def seed_curriculum():
    for cname, (nper, periods) in CURRICULUM.items():
        slug = slugify(cname)
        course = await db.courses.find_one({"slug": slug})
        if not course:
            course = {"id": str(uuid.uuid4()), "name": cname, "slug": slug, "description": f"Materiais de {cname} organizados por período. {NOTE}",
                      "icon": "GraduationCap", "num_periods": nper, "status": "publicado"}
            await db.courses.insert_one(dict(course))
        else:
            course_updates = {"num_periods": nper}
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
                discipline_description = f"Estudo de {dname}, com fundamentos, conceitos, métodos e aplicações no contexto de {cname}."
                if not disc:
                    disc = {"id": str(uuid.uuid4()), "course_id": course["id"], "period_id": period["id"], "name": dname,
                            "slug": dslug, "description": discipline_description, "status": "publicado"}
                    await db.disciplines.insert_one(dict(disc))
                else:
                    updates = {"description": disc.get("description") or discipline_description}
                    if not disc.get("status"): updates["status"] = "publicado"
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
                        updates = {"description": topic.get("description") or desc}
                        if not topic.get("status"): updates["status"] = "publicado"
                        await db.topics.update_one({"id": topic["id"]}, {"$set": updates})


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
