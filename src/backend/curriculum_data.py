"""Revisão curricular do Campus Study.

Disciplinas: baseadas em matrizes publicadas por instituições federais sempre que
há uma referência específica registrada. Os roteiros de assuntos são didáticos e
não substituem as ementas/plano de ensino da turma. Marketing é mantido como trilha
formativa, não como matriz oficial de bacharelado.
"""
from __future__ import annotations

# Matérias agrupadas explicitamente por período. Não existe redistribuição automática.
CURRICULA: dict[str, dict[int, list[str]]] = {
    "ENEM": {1: ["Redação", "Matemática", "Português e Linguagens", "História", "Geografia", "Filosofia", "Sociologia", "Física", "Química", "Biologia", "Inglês", "Espanhol", "Artes"]},
    "Odontologia": {
        1: ["Introdução à Clínica Odontológica I", "Sociologia e Saúde", "Anatomia Humana Sistêmica e Segmentar", "Genética A", "Histologia e Embriologia Geral A", "Bioquímica A"],
        2: ["Anatomia e Escultura Dental", "Biossegurança em Odontologia", "Saúde Bucal Coletiva", "Metodologia Científica", "Histologia e Desenvolvimento Buco-Dental", "Anatomia de Cabeça e Pescoço", "Microbiologia"],
        3: ["Controle de Infecção", "Prevenção em Saúde Bucal", "Patologia Geral", "Bioética", "Dentística I", "Diagnóstico Bucal I", "Fisiologia Humana A", "Imunologia"],
        4: ["Patologia Bucal", "Dentística II", "Periodontia", "Promoção da Saúde", "Diagnóstico Bucal II", "Psicologia Aplicada à Odontologia", "Farmacologia Aplicada à Odontologia"],
        5: ["Endodontia", "Clínica de Atenção Básica IA", "Prótese Dentária I", "Cirurgia", "Estágio na Atenção Primária em Saúde", "Diagnóstico Bucal III"],
        6: ["Endodontia Clínica", "Odontopediatria", "Ortodontia Infantil", "Clínica de Atenção Básica IIA", "Prótese Dentária II", "Cirurgia Clínica", "Diagnóstico Bucal IV"],
        7: ["Clínica Infantil I", "Cirurgia e Traumatologia Buco-Maxilo-Facial I", "Epidemiologia em Saúde Bucal", "Odontologia Legal", "Estágio em Clínica Integrada IA"],
        8: ["Clínica Infantil II", "Orientação Profissional", "Estágio em Clínica Integrada II"],
        9: ["Estágio em Clínica Integrada IIIA", "Estágio Comunitário Interprofissional", "Estágio em Urgências Odontológicas", "Estágio em Odontologia Coletiva"],
        10: ["Estágio em Clínica Integrada IVA", "Trabalho de Conclusão de Curso"],
    },
    "Medicina": {
        1: ["Método Clínico I", "Módulo Integrador I", "Corpo Humano Saudável I", "Saúde, Família e Comunidade I"],
        2: ["Método Clínico II", "Módulo Integrador II", "Corpo Humano Saudável II", "Saúde, Família e Comunidade II"],
        3: ["Método Clínico III", "Módulo Integrador III", "Humanidades I", "Introdução ao Cuidar I", "Trabalho de Curso I — Elaboração do Projeto", "Saúde, Família e Comunidade III", "Determinantes Biológicos no Processo Saúde-Doença I"],
        4: ["Método Clínico IV", "Módulo Integrador IV", "Humanidades II", "Introdução ao Cuidar II", "Trabalho de Curso II — Submissão do Projeto", "Saúde, Família e Comunidade IV", "Determinantes Biológicos no Processo Saúde-Doença II"],
        5: ["Saúde do Adulto e do Idoso — Sistema Digestivo", "Cirurgia Geral, Cirurgia Oncológica e Nutrologia", "Clínica Médica, Anestesiologia e Dor", "Emergência e Trauma", "Trabalho de Curso III — Coleta de Dados"],
        6: ["Saúde do Adulto e do Idoso — Sistema Cardiovascular", "Saúde do Adulto e do Idoso — Sistema Respiratório", "Onco-hematologia, Hematologia, Oncologia e Genética Clínica", "Atenção Integral à Saúde da Mulher e da Criança I", "Trabalho de Curso IV — Apresentação do Trabalho"],
        7: ["Saúde do Adulto e do Idoso — Sistema Locomotor, Cirurgia Plástica, Geriatria e Cuidados Paliativos", "Saúde do Adulto e do Idoso — Sistema Urinário", "Psiquiatria, Medicina Legal, Doenças Infecciosas e Parasitárias, Dermatologia e Epidemiologia", "Psiquiatria, Medicina Legal e Saúde Mental Coletiva", "Trabalho de Curso V — Finalização e Defesa"],
        8: ["Saúde do Adulto e do Idoso — Sistema Nervoso e Ocular", "Endocrinologia, Otorrinolaringologia e Cirurgia de Cabeça e Pescoço", "Atenção Integral à Saúde da Mulher e da Criança II", "Saúde da Criança, do Adolescente e Saúde Coletiva Infantil"],
        9: ["Estágio Curricular em Atenção Básica I", "Estágio Curricular em Especialidades Médicas I", "Estágio Curricular em Saúde Mental"],
        10: ["Estágio Curricular em Atenção Básica II", "Estágio Curricular Livre", "Estágio Curricular em Saúde Coletiva", "Estágio Curricular em Urgência e Emergência"],
        11: ["Estágio Curricular em Saúde da Criança", "Estágio Curricular em Saúde da Mulher"],
        12: ["Estágio Curricular em Saúde do Adulto e do Idoso I", "Estágio Curricular em Saúde do Adulto e do Idoso II"],
    },
    "Enfermagem": {
        1: ["Saúde Coletiva", "Introdução à Enfermagem", "Metodologia Científica", "Anatomia Humana Sistêmica e Segmentar", "Biofísica A"],
        2: ["Promoção da Saúde", "Risco Biológico e Biossegurança", "Tecnologia da Educação em Saúde", "Genética A", "Histologia e Embriologia Geral A", "Bioquímica A"],
        3: ["Epidemiologia e Bioestatística", "Bases para o Cuidar do Indivíduo e da Família I", "Fisiologia Humana B", "Imunologia", "Microbiologia"],
        4: ["Psicologia Aplicada à Enfermagem", "Bases para o Cuidar do Indivíduo e da Família II", "Processamento de Produtos para a Saúde", "Farmacologia Básica", "Parasitologia", "Patologia Geral"],
        5: ["Enfermagem Clínica", "Enfermagem em Doenças Infecciosas", "Saúde Mental", "Vigilância à Saúde", "Farmacologia Aplicada à Enfermagem"],
        6: ["Nutrição", "Sociologia e Saúde", "Enfermagem Cirúrgica e Centro Cirúrgico", "Enfermagem Psiquiátrica", "Enfermagem em Cuidado Crítico"],
        7: ["Antropologia da Saúde", "Enfermagem Ginecológica e Obstétrica I", "Enfermagem Pediátrica e Neonatológica I", "Práticas de Enfermagem em Saúde Coletiva", "Administração em Enfermagem I", "Ética e Exercício da Enfermagem", "Trabalho de Conclusão de Curso I"],
        8: ["Enfermagem Ginecológica e Obstétrica II", "Enfermagem Pediátrica e Neonatológica II", "Enfermagem Hebiátrica", "Administração em Enfermagem II", "Filosofia e Enfermagem", "Trabalho de Conclusão de Curso II"],
        9: ["Estágio Supervisionado em Enfermagem I", "Estágio Supervisionado em Enfermagem II"],
        10: ["Estágio Supervisionado em Enfermagem III", "Estágio Supervisionado em Enfermagem IV"],
    },
    "Farmácia": {
        1: ["Introdução às Ciências Farmacêuticas", "Anatomia Humana Sistêmica e Segmentar", "Cálculo 1C", "Química Geral", "Química Geral Experimental", "Química Orgânica", "Química Orgânica Experimental"],
        2: ["Histologia Geral", "Genética A", "Biofísica A", "Bioquímica A", "Física Aplicada à Biologia", "Química Orgânica II", "Química Analítica", "Química Analítica Experimental"],
        3: ["Estágio I — Atenção à Saúde I", "Farmacobotânica", "Fisiologia Humana A", "Farmacologia Básica", "Bioestatística", "Físico-Química", "Físico-Química Experimental", "Parasitologia", "Epidemiologia"],
        4: ["Farmacoepidemiologia e Farmacovigilância", "Introdução à Metodologia Científica", "Análise Instrumental", "Farmacognosia", "Farmacologia I", "Química Orgânica Aplicada às Ciências Farmacêuticas", "Operações Unitárias", "Toxicologia Geral", "Imunologia"],
        5: ["Deontologia Farmacêutica", "Farmácia Social e Saúde Pública", "Farmacocinética Aplicada", "Farmacologia II", "Farmacotécnica e Cosmetologia", "Toxicologia Aplicada", "Microbiologia Geral", "Patologia Geral"],
        6: ["Fundamentos da Administração", "Práticas Terapêuticas Integrativas e Complementares", "Bromatologia", "Semiologia e Farmacoterapia", "Tecnologia Farmacêutica", "Introdução à Química Farmacêutica Medicinal", "Trabalho de Conclusão de Curso I", "Assistência Farmacêutica em Serviços de Saúde"],
        7: ["Farmácia Hospitalar", "Bromatologia Experimental", "Farmácia Clínica", "Química Farmacêutica Medicinal", "Bioquímica Clínica", "Citologia Clínica", "Hematologia Clínica"],
        8: ["Química e Bioquímica de Alimentos", "Estágio II — Fármacos, Cosméticos e Medicamentos", "Assistência Farmacêutica no SUS", "Controle de Qualidade Físico-Químico de Medicamentos", "Controle de Qualidade Microbiológico de Medicamentos", "Diagnóstico Laboratorial"],
        9: ["Estágio Curricular em Farmácia Clínica", "Estágio Curricular em Análises Clínicas", "Gestão de Serviços Farmacêuticos"],
        10: ["Estágio Curricular Supervisionado em Farmácia", "Trabalho de Conclusão de Curso II"],
    },
    "Fisioterapia": {
        1: ["Sociologia e Saúde", "Antropologia da Saúde", "Anatomia Humana I", "Introdução à Fisioterapia", "Biologia Celular e Histologia", "Bioquímica Básica"],
        2: ["Anatomia Humana II", "Fisiologia Humana I", "Cinesiologia", "Biofísica", "Metodologia Científica em Saúde"],
        3: ["Fisiologia Humana II", "Neuroanatomia", "Biomecânica", "Genética Humana", "Epidemiologia e Saúde Coletiva"],
        4: ["Cinesioterapia", "Recursos Terapêuticos Manuais", "Fisiologia do Exercício", "Patologia Geral", "Farmacologia Aplicada à Fisioterapia"],
        5: ["Avaliação Fisioterapêutica", "Eletrotermofototerapia", "Fisioterapia Musculoesquelética I", "Fisioterapia Respiratória I", "Controle Motor e Aprendizagem Motora"],
        6: ["Fisioterapia Musculoesquelética II", "Fisioterapia Cardiovascular", "Fisioterapia Neurológica I", "Fisioterapia na Saúde da Mulher", "Prática Baseada em Evidências"],
        7: ["Fisioterapia Neurológica II", "Fisioterapia Pediátrica", "Fisioterapia Geriátrica", "Fisioterapia em Terapia Intensiva", "Gestão em Saúde"],
        8: ["Fisioterapia Esportiva", "Fisioterapia Dermatofuncional", "Fisioterapia do Trabalho", "Fisioterapia em Saúde Coletiva", "Trabalho de Conclusão de Curso I"],
        9: ["Estágio Supervisionado em Fisioterapia I", "Estágio Supervisionado em Fisioterapia II", "Trabalho de Conclusão de Curso II"],
        10: ["Estágio Supervisionado em Fisioterapia III", "Estágio Supervisionado em Fisioterapia IV"],
    },
    "Medicina Veterinária": {
        1: ["Introdução à Medicina Veterinária", "Anatomia dos Animais Domésticos I", "Biologia Celular", "Histologia Veterinária I", "Química Geral", "Bioestatística"],
        2: ["Anatomia dos Animais Domésticos II", "Histologia Veterinária II", "Embriologia Veterinária", "Bioquímica", "Genética Animal", "Zoologia Aplicada"],
        3: ["Fisiologia Animal I", "Microbiologia Veterinária", "Imunologia Veterinária", "Parasitologia Veterinária I", "Nutrição Animal", "Agrostologia e Forragicultura"],
        4: ["Fisiologia Animal II", "Parasitologia Veterinária II", "Patologia Geral Veterinária", "Farmacologia Veterinária I", "Epidemiologia Veterinária", "Produção de Ruminantes"],
        5: ["Patologia Especial Veterinária", "Farmacologia Veterinária II", "Doenças Infecciosas dos Animais", "Semiologia Veterinária", "Anestesiologia Veterinária", "Produção de Aves e Suínos"],
        6: ["Patologia Clínica Veterinária", "Diagnóstico por Imagem Veterinário", "Clínica Médica de Pequenos Animais I", "Clínica Médica de Grandes Animais I", "Reprodução Animal", "Inspeção de Produtos de Origem Animal I"],
        7: ["Clínica Médica de Pequenos Animais II", "Clínica Médica de Grandes Animais II", "Cirurgia Veterinária I", "Obstetrícia Veterinária", "Doenças Parasitárias dos Animais", "Saúde Pública Veterinária"],
        8: ["Cirurgia Veterinária II", "Clínica de Equinos", "Clínica de Ruminantes", "Inspeção de Produtos de Origem Animal II", "Medicina de Animais Silvestres", "Tecnologia de Produtos de Origem Animal"],
        9: ["Estágio Curricular em Clínica e Cirurgia de Pequenos Animais", "Estágio Curricular em Grandes Animais", "Toxicologia Veterinária", "Ética e Legislação Veterinária"],
        10: ["Estágio Curricular Supervisionado em Medicina Veterinária", "Saúde Única e Vigilância em Saúde", "Trabalho de Conclusão de Curso"],
    },
    "Agronomia": {
        1: ["Desenho Técnico", "Introdução à Agronomia", "Metodologia Científica", "Biologia e Zoologia", "Morfologia e Taxonomia Vegetal", "Cálculo 1B", "Química Geral", "Química Orgânica"],
        2: ["Introdução à Ciência do Solo", "Anatomia e Fisiologia dos Animais Domésticos", "Anatomia Vegetal", "Física I", "Cálculo 2B", "Introdução à Computação", "Química Analítica Prática"],
        3: ["Fisiologia Vegetal", "Microbiologia Agrícola", "Climatologia Agrícola", "Topografia e Geodésia", "Estatística Experimental", "Máquinas e Mecanização Agrícola"],
        4: ["Fertilidade do Solo", "Genética e Melhoramento Vegetal I", "Entomologia Agrícola I", "Fitopatologia Geral", "Hidráulica e Irrigação", "Economia Rural"],
        5: ["Manejo e Conservação do Solo e da Água", "Nutrição Mineral de Plantas", "Entomologia Agrícola II", "Fitopatologia Aplicada", "Forragicultura", "Zootecnia Geral"],
        6: ["Irrigação e Drenagem", "Plantas Daninhas e seu Manejo", "Olericultura", "Fruticultura", "Extensão Rural", "Agroecologia"],
        7: ["Grandes Culturas I", "Tecnologia de Sementes", "Produção de Mudas", "Manejo Integrado de Pragas", "Construções Rurais"],
        8: ["Grandes Culturas II", "Pós-Colheita e Armazenamento", "Agricultura de Precisão", "Gestão de Propriedades Rurais", "Legislação Agrária e Ambiental"],
        9: ["Fitotecnia de Culturas Regionais", "Planejamento Agrícola", "Sistemas Integrados de Produção", "Estágio Supervisionado em Agronomia"],
        10: ["Projeto de Trabalho de Conclusão de Curso", "Trabalho de Conclusão de Curso", "Gestão Ambiental Rural"],
    },
    "Direito": {
        1: ["Teoria do Direito", "Ciência Política e Teoria Geral do Estado", "Relações de Gênero e Direito", "Direito Civil I (Parte Geral)", "Atividade de Extensão 1", "Filosofia Moral", "Sociologia Geral e Jurídica"],
        2: ["Direito Civil II (Obrigações)", "Direito Penal I", "Teoria da Constituição", "Teoria Geral do Processo", "História do Direito e do Pensamento Jurídico", "Filosofia do Direito", "Direito Digital e Tecnologias"],
        3: ["Pesquisa e Direito I (Metodologia)", "Direito Civil III (Contratos)", "Direito Penal II", "Direito Constitucional I", "Direito Processual Civil I", "Hermenêutica Jurídica e Teoria da Argumentação", "Atividade de Extensão 2", "Psicologia"],
        4: ["Direito Civil IV (Responsabilidade Civil)", "Direito Constitucional II", "Direito Processual Civil II", "Direito Processual Penal I", "Direito Penal III", "Formas Consensuais de Resolução dos Conflitos", "Atividade de Extensão 3", "Educação para Relações Étnico-Raciais e Direitos Humanos"],
        5: ["Direito Civil V (Reais)", "Direito Internacional Público", "Processo Constitucional", "Direito Processual Penal II", "Direito Processual Civil III", "Pesquisa e Direito II", "Estágio Supervisionado I — Resolução Consensual de Conflitos", "Atividade de Extensão 4"],
        6: ["Economia B", "Direito Administrativo I", "Direito Civil VI (Família)", "Direito Processual Penal III", "Direito do Trabalho I", "Direito Agrário", "Políticas Públicas e Direito", "Antropologia e Direito"],
        7: ["Direito Empresarial I", "Estágio Supervisionado II — Prática Jurídica Cível I", "Direito Civil VII (Sucessões)", "Direito do Trabalho II", "Criminologia", "Direito Administrativo II", "Atividade de Extensão 5"],
        8: ["Estágio Supervisionado III — Prática Jurídica Cível II", "Estágio Supervisionado IV — Direitos Coletivos", "Direito Financeiro", "Direito Processual do Trabalho", "Direito Empresarial II", "Direito do Consumidor", "Trabalho de Conclusão de Curso I"],
        9: ["Estágio Supervisionado V — Prática Jurídica Penal I", "Estágio Supervisionado VI — Prática Jurídica Cível III", "Direito Tributário I", "Direito Econômico", "Direitos da Criança, Adolescente, Pessoa Idosa e Pessoa com Deficiência", "Trabalho de Conclusão de Curso II"],
        10: ["Estágio Supervisionado em Prática Jurídica Penal II", "Direito Ambiental", "Direito Previdenciário", "Direito Internacional Privado", "Ética Profissional e Deontologia Jurídica"],
    },
    "Administração": {
        1: ["Introdução à Administração de Empresas", "Introdução à Administração Pública", "Fundamentos de Contabilidade", "Psicologia das Organizações", "Cálculo 1B"],
        2: ["Matemática Financeira", "Contabilidade Gerencial", "Teoria das Organizações", "Sociologia das Organizações", "Cálculo 2B"],
        3: ["Teoria Geral da Administração", "Microeconomia", "Estatística Aplicada à Administração", "Comportamento Organizacional", "Instituições de Direito Público e Privado"],
        4: ["Gestão de Pessoas", "Macroeconomia", "Administração Financeira I", "Marketing", "Métodos Quantitativos para Decisão"],
        5: ["Gestão de Operações", "Gestão de Materiais e Logística", "Pesquisa Operacional", "Contabilidade de Custos", "Pesquisa de Mercado"],
        6: ["Administração Estratégica", "Gestão de Projetos", "Sistemas de Informação Gerencial", "Administração da Produção", "Gestão da Qualidade"],
        7: ["Finanças Corporativas", "Gestão Pública e Políticas Públicas", "Empreendedorismo e Inovação", "Negociação e Tomada de Decisão", "Estágio Supervisionado I"],
        8: ["Gestão Socioambiental", "Consultoria Organizacional", "Estágio Supervisionado II", "Trabalho de Conclusão de Curso"],
    },
    "Engenharia Civil": {
        1: ["Introdução ao Curso de Engenharia Civil", "Desenho I", "Física I", "Cálculo 1A", "Geometria Analítica", "Química Geral B", "Química Geral Experimental"],
        2: ["Desenho II", "Física II", "Laboratório de Física I", "Álgebra Linear", "Cálculo 2A", "Probabilidade e Estatística", "Introdução à Computação"],
        3: ["Desenho Arquitetônico", "Sociologia para Engenheiros", "Física III", "Laboratório de Física II", "Mecânica Geral I", "Cálculo Numérico", "Cálculo 3A"],
        4: ["Introdução à Geotecnia", "Laboratório de Materiais de Construção I", "Materiais de Construção I", "Mecânica dos Fluidos", "Metodologia Científica e Tecnológica", "Resistência dos Materiais I", "Mecânica Geral II", "Equações Diferenciais"],
        5: ["Análise Estrutural I", "Ciências do Ambiente", "Hidráulica I", "Laboratório de Materiais de Construção II", "Laboratório de Mecânica dos Solos I", "Materiais de Construção II", "Mecânica dos Solos I", "Resistência dos Materiais II", "Sistemas Estruturais I"],
        6: ["Análise Estrutural II", "Arquitetura e Urbanismo", "Construção Civil I", "Hidráulica II", "Hidrologia", "Laboratório de Mecânica dos Solos II", "Mecânica dos Solos II", "Topografia e Geodésia"],
        7: ["Concreto Estrutural I", "Construção Civil II", "Estruturas de Aço", "Sistemas de Abastecimento de Água", "Planejamento do Transporte e da Mobilidade Urbana", "Projeto de Estradas I"],
        8: ["Fundações", "Instalações Hidrossanitárias", "Instalações Elétricas Prediais", "Pavimentação", "Planejamento e Controle de Obras"],
        9: ["Saneamento", "Estruturas de Madeira", "Orçamento e Gestão de Obras", "Engenharia de Transportes", "Segurança do Trabalho na Construção"],
        10: ["Estágio Supervisionado em Engenharia Civil", "Trabalho de Conclusão de Curso em Engenharia Civil", "Projeto Integrador de Engenharia Civil"],
    },
    "Engenharia Mecânica": {
        1: ["Cálculo 1A", "Geometria Analítica", "Física I", "Desenho Técnico", "Introdução à Engenharia Mecânica", "Química Geral"],
        2: ["Cálculo 2A", "Álgebra Linear", "Física II", "Laboratório de Física I", "Desenho Técnico Mecânico", "Introdução à Computação"],
        3: ["Cálculo 3A", "Física III", "Mecânica Geral I", "Probabilidade e Estatística", "Programação Aplicada à Engenharia", "Materiais de Engenharia I"],
        4: ["Equações Diferenciais", "Mecânica Geral II", "Resistência dos Materiais I", "Termodinâmica I", "Metrologia e Instrumentação"],
        5: ["Resistência dos Materiais II", "Mecânica dos Fluidos I", "Termodinâmica II", "Materiais de Engenharia II", "Processos de Fabricação I"],
        6: ["Transferência de Calor", "Elementos de Máquinas I", "Máquinas Térmicas", "Processos de Fabricação II", "Sistemas Hidráulicos e Pneumáticos"],
        7: ["Vibrações Mecânicas", "Máquinas de Fluxo", "Elementos de Máquinas II", "Controle de Sistemas Mecânicos", "Projeto de Máquinas I"],
        8: ["Automação Industrial", "Refrigeração e Ar-Condicionado", "Projeto Mecânico Assistido por Computador", "Manutenção Industrial", "Engenharia de Produção"],
        9: ["Projeto de Máquinas II", "Gestão da Qualidade na Engenharia", "Engenharia de Segurança do Trabalho", "Estágio Supervisionado em Engenharia Mecânica"],
        10: ["Trabalho de Conclusão de Curso em Engenharia Mecânica", "Projeto Integrador de Engenharia Mecânica", "Ética e Legislação Profissional"],
    },
    "Engenharia Elétrica": {
        1: ["Cálculo 1A", "Geometria Analítica", "Física I", "Química Geral", "Introdução à Engenharia Elétrica", "Computação e Sociedade"],
        2: ["Cálculo 2A", "Álgebra Linear", "Física II", "Laboratório de Física I", "Circuitos Digitais", "Introdução à Programação"],
        3: ["Cálculo 3A", "Física III", "Eletromagnetismo", "Circuitos Elétricos I", "Probabilidade e Estatística", "Equações Diferenciais"],
        4: ["Circuitos Elétricos II", "Eletrônica Analógica I", "Sinais e Sistemas", "Conversão Eletromecânica de Energia", "Instrumentação Elétrica"],
        5: ["Eletrônica Analógica II", "Máquinas Elétricas I", "Sistemas Lineares", "Instalações Elétricas", "Eletrônica Digital Aplicada"],
        6: ["Sistemas de Controle", "Máquinas Elétricas II", "Sistemas de Energia Elétrica I", "Eletrônica de Potência", "Medidas Elétricas"],
        7: ["Sistemas de Energia Elétrica II", "Microprocessadores e Microcontroladores", "Proteção de Sistemas Elétricos", "Automação Industrial", "Telecomunicações"],
        8: ["Processamento Digital de Sinais", "Geração de Energia Elétrica", "Distribuição de Energia Elétrica", "Sistemas Embarcados", "Eficiência Energética"],
        9: ["Energias Renováveis", "Planejamento de Sistemas Elétricos", "Projeto de Sistemas Elétricos", "Estágio Supervisionado em Engenharia Elétrica"],
        10: ["Trabalho de Conclusão de Curso em Engenharia Elétrica", "Projeto Integrador de Engenharia Elétrica", "Ética e Legislação Profissional"],
    },
    "Psicologia": {
        1: ["Filosofia e Psicologia", "História, Teorias e Sistemas da Psicologia I", "Introdução às Ciências Sociais I", "Atividades Integradas de Estágio Básico: Pesquisa I", "Psicologia: Ciência e Profissão", "Anatomia Humana Sistêmica e Segmentar", "Estatística Aplicada à Psicologia"],
        2: ["Introdução às Ciências Sociais II", "História, Teorias e Sistemas da Psicologia II", "Investigação e Métodos em Psicologia I", "Atividades Integradas de Estágio Básico: Pesquisa II", "Processos Psicológicos Básicos", "Fisiologia Humana"],
        3: ["História, Teorias e Sistemas da Psicologia III", "Psicologia do Desenvolvimento I", "Psicologia Social I", "Psicologia da Aprendizagem", "Metodologia de Pesquisa em Psicologia"],
        4: ["Psicologia do Desenvolvimento II", "Psicologia Social II", "Psicologia da Personalidade I", "Psicopatologia I", "Avaliação Psicológica I"],
        5: ["Psicologia da Personalidade II", "Psicopatologia II", "Avaliação Psicológica II", "Psicologia Escolar e Educacional", "Psicologia Organizacional e do Trabalho I"],
        6: ["Psicologia Clínica I", "Psicologia Organizacional e do Trabalho II", "Psicologia da Saúde", "Psicometria", "Políticas Públicas e Direitos Humanos"],
        7: ["Abordagens Clínicas I", "Psicologia Comunitária", "Psicologia Jurídica", "Psicologia Hospitalar", "Estágio Básico em Avaliação Psicológica"],
        8: ["Abordagens Clínicas II", "Intervenções em Grupos", "Psicologia e Processos Educativos", "Ética Profissional em Psicologia", "Estágio Básico em Intervenção"],
        9: ["Estágio Específico em Psicologia I", "Pesquisa em Psicologia Aplicada", "Trabalho de Conclusão de Curso I"],
        10: ["Estágio Específico em Psicologia II", "Trabalho de Conclusão de Curso II", "Práticas Profissionais e Inserção no Trabalho"],
    },
    "Biomedicina": {
        1: ["Anatomia Humana I", "Biossegurança", "Biologia Celular", "Histologia I e Embriologia", "Biomedicina e Saúde Coletiva", "Física Aplicada à Biologia", "Cálculo 1C", "Química Geral", "Química Orgânica"],
        2: ["Bioestatística", "Bioquímica", "Anatomia Humana II", "Histologia II", "Fisiologia Humana", "Metodologia Científica"],
        3: ["Genética", "Microbiologia", "Imunologia", "Parasitologia", "Biologia Molecular", "Epidemiologia"],
        4: ["Patologia Geral", "Farmacologia", "Hematologia", "Imuno-hematologia", "Processos de Análises Clínicas I"],
        5: ["Bioquímica Clínica", "Microbiologia Clínica", "Parasitologia Clínica", "Citopatologia", "Imunologia Clínica"],
        6: ["Histotecnologia", "Genética Molecular", "Diagnóstico por Imagem", "Análises Clínicas II", "Toxicologia Analítica"],
        7: ["Hematologia Clínica Avançada", "Biologia Molecular Aplicada ao Diagnóstico", "Gestão Laboratorial", "Estágio Supervisionado em Biomedicina I"],
        8: ["Estágio Supervisionado em Biomedicina II", "Trabalho de Conclusão de Curso", "Ética e Legislação Biomédica"],
    },
    "Nutrição": {
        1: ["Fundamentos Teórico-Práticos do SUS", "Introdução à Prática Profissional", "Antropologia da Saúde", "Histologia e Embriologia Geral", "Anatomia Humana Sistêmica e Segmentar", "Genética na Nutrição", "Química Geral"],
        2: ["Estudo Experimental dos Alimentos", "Promoção da Saúde", "Sociologia e Saúde", "Bioquímica da Nutrição", "Fisiologia Humana", "Microbiologia dos Alimentos"],
        3: ["Avaliação Nutricional I", "Composição dos Alimentos", "Nutrição e Metabolismo", "Parasitologia", "Epidemiologia Nutricional", "Técnica Dietética I"],
        4: ["Avaliação Nutricional II", "Técnica Dietética II", "Higiene e Legislação dos Alimentos", "Nutrição nos Ciclos da Vida I", "Patologia da Nutrição", "Bioestatística"],
        5: ["Nutrição nos Ciclos da Vida II", "Dietoterapia I", "Administração de Unidades de Alimentação e Nutrição I", "Educação Alimentar e Nutricional", "Bromatologia"],
        6: ["Dietoterapia II", "Nutrição Clínica", "Administração de Unidades de Alimentação e Nutrição II", "Tecnologia de Alimentos", "Nutrição Materno-Infantil"],
        7: ["Nutrição em Saúde Coletiva", "Nutrição Esportiva", "Nutrição do Idoso", "Planejamento de Cardápios", "Controle Higiênico-Sanitário de Alimentos"],
        8: ["Nutrição Hospitalar", "Nutrição em Doenças Crônicas", "Terapia Nutricional", "Estágio em Alimentação Coletiva I"],
        9: ["Estágio em Nutrição Clínica", "Estágio em Saúde Coletiva", "Trabalho de Conclusão de Curso I"],
        10: ["Estágio em Alimentação Coletiva II", "Estágio Curricular Integrado em Nutrição", "Trabalho de Conclusão de Curso II"],
    },
    "Arquitetura e Urbanismo": {
        1: ["Introdução à Arquitetura e Urbanismo", "Desenho de Observação", "Geometria Descritiva", "História da Arte e da Arquitetura I", "Representação Gráfica I"],
        2: ["Projeto de Arquitetura I", "Desenho Arquitetônico", "História da Arquitetura II", "Conforto Ambiental I", "Materiais e Técnicas Construtivas I"],
        3: ["Projeto de Arquitetura II", "Topografia", "Sistemas Estruturais I", "Conforto Ambiental II", "Teoria e História do Urbanismo I"],
        4: ["Projeto de Arquitetura III", "Sistemas Estruturais II", "Instalações Prediais I", "Tecnologia da Construção I", "Teoria e História da Arquitetura Brasileira"],
        5: ["Projeto de Arquitetura IV", "Planejamento Urbano I", "Instalações Prediais II", "Tecnologia da Construção II", "Paisagismo I"],
        6: ["Projeto de Arquitetura V", "Planejamento Urbano II", "Sistemas Estruturais III", "Paisagismo II", "Desempenho Ambiental da Edificação"],
        7: ["Projeto de Urbanismo I", "Restauro e Patrimônio Cultural", "Orçamento e Planejamento de Obras", "Legislação Urbana", "Projeto de Interiores"],
        8: ["Projeto de Urbanismo II", "Habitação e Interesse Social", "Infraestrutura Urbana", "Gestão de Projetos de Arquitetura", "Ateliê Integrado"],
        9: ["Projeto Final de Graduação I", "Estágio Supervisionado em Arquitetura e Urbanismo", "Pesquisa em Arquitetura e Urbanismo"],
        10: ["Projeto Final de Graduação II", "Ética e Legislação Profissional", "Prática Integrada em Arquitetura e Urbanismo"],
    },
    "Ciências Contábeis": {
        1: ["Contabilidade Introdutória I", "Introdução à Teoria da Contabilidade", "Matemática Financeira Aplicada à Contabilidade", "Fundamentos da Microeconomia", "Instituições do Direito Público e Privado"],
        2: ["Contabilidade Introdutória II", "Introdução à Administração de Empresas", "Fundamentos da Macroeconomia", "Estatística Aplicada", "Direito Empresarial"],
        3: ["Contabilidade Intermediária I", "Contabilidade de Custos I", "Matemática Financeira Avançada", "Legislação Tributária", "Teoria das Organizações"],
        4: ["Contabilidade Intermediária II", "Contabilidade de Custos II", "Contabilidade Pública I", "Análise das Demonstrações Contábeis", "Sistemas de Informação Contábil"],
        5: ["Contabilidade Avançada I", "Auditoria I", "Contabilidade Tributária", "Orçamento Empresarial", "Estatística Aplicada à Pesquisa Contábil"],
        6: ["Contabilidade Avançada II", "Auditoria II", "Contabilidade Pública II", "Controladoria", "Perícia Contábil"],
        7: ["Contabilidade Societária", "Contabilidade do Agronegócio", "Governança e Compliance", "Ética Profissional Contábil", "Pesquisa em Contabilidade"],
        8: ["Prática Contábil Informatizada", "Análise de Investimentos", "Gestão de Riscos", "Trabalho de Conclusão de Curso I"],
        9: ["Estágio Supervisionado em Ciências Contábeis", "Trabalho de Conclusão de Curso II", "Prática Profissional e Responsabilidade Técnica"],
    },
    "Sistemas de Informação": {
        1: ["Cálculo 1A", "Computação e Sociedade", "Introdução à Programação", "Fundamentos de Matemática para Computação"],
        2: ["Probabilidade e Estatística A", "Algoritmos e Estruturas de Dados 1", "Lógica Matemática", "Metodologia Científica"],
        3: ["Algoritmos e Estruturas de Dados 2", "Programação Orientada a Objetos", "Arquitetura de Computadores", "Banco de Dados I", "Matemática Discreta"],
        4: ["Engenharia de Software I", "Sistemas Operacionais", "Redes de Computadores I", "Banco de Dados II", "Interação Humano-Computador"],
        5: ["Engenharia de Software II", "Análise e Projeto de Sistemas", "Desenvolvimento Web", "Redes de Computadores II", "Pesquisa Operacional"],
        6: ["Sistemas Distribuídos", "Segurança da Informação", "Gestão de Projetos de TI", "Inteligência Artificial", "Sistemas de Informação Gerenciais"],
        7: ["Governança de Tecnologia da Informação", "Arquitetura de Software", "Empreendedorismo em TI", "Auditoria e Controle de Sistemas", "Estágio em Sistemas de Informação I"],
        8: ["Gestão de Serviços de TI", "Mineração e Análise de Dados", "Projeto de Sistemas de Informação", "Estágio em Sistemas de Informação II"],
        9: ["Trabalho de Conclusão de Curso em Sistemas de Informação", "Projeto Integrador de Sistemas", "Ética e Legislação em Computação"],
    },
    "Ciência da Computação": {
        1: ["Geometria Analítica", "Fundamentos de Matemática para Computação", "Introdução à Programação", "Computação e Sociedade"],
        2: ["Circuitos Digitais", "Álgebra Linear", "Matemática Discreta", "Programação Orientada a Objetos", "Algoritmos e Estruturas de Dados 1"],
        3: ["Cálculo 1A", "Pesquisa Operacional", "Lógica Matemática", "Algoritmos e Estruturas de Dados 2", "Arquitetura de Computadores"],
        4: ["Probabilidade e Estatística", "Linguagens Formais e Autômatos", "Banco de Dados", "Sistemas Operacionais", "Programação Funcional"],
        5: ["Engenharia de Software", "Redes de Computadores", "Teoria da Computação", "Compiladores", "Inteligência Artificial"],
        6: ["Sistemas Distribuídos", "Análise de Algoritmos", "Interação Humano-Computador", "Computação Gráfica", "Segurança de Sistemas"],
        7: ["Aprendizado de Máquina", "Processamento de Imagens", "Sistemas Embarcados", "Projeto e Análise de Sistemas", "Pesquisa em Computação"],
        8: ["Estágio em Ciência da Computação", "Trabalho de Conclusão de Curso", "Ética e Legislação em Computação", "Projeto Integrador em Computação"],
    },
    "Pedagogia": {
        1: ["Fundamentos Históricos da Educação", "Filosofia da Educação", "Sociologia da Educação", "Psicologia da Educação I", "Leitura e Produção de Texto Acadêmico"],
        2: ["História da Educação Brasileira", "Psicologia da Educação II", "Políticas Educacionais", "Didática e Formação Docente", "Educação e Diversidade"],
        3: ["Currículo e Cultura", "Alfabetização e Letramento I", "Educação Infantil I", "Educação Inclusiva", "Pesquisa em Educação I"],
        4: ["Alfabetização e Letramento II", "Educação Infantil II", "Didática e Organização do Trabalho Pedagógico", "Educação de Jovens e Adultos", "Tecnologias na Educação"],
        5: ["Ensino de Língua Portuguesa", "Ensino de Matemática", "Ensino de Ciências da Natureza", "Gestão dos Processos Educativos", "Estágio em Educação Infantil I"],
        6: ["Ensino de História e Geografia", "Arte e Educação", "Educação do Campo e Contextos Interculturais", "Avaliação da Aprendizagem", "Estágio em Anos Iniciais I"],
        7: ["Libras e Educação de Surdos", "Planejamento e Gestão Escolar", "Estágio em Educação Infantil II", "Pesquisa em Educação II", "Trabalho de Conclusão de Curso I"],
        8: ["Estágio em Anos Iniciais II", "Educação e Direitos Humanos", "Trabalho de Conclusão de Curso II", "Práticas Pedagógicas Integradoras"],
    },
    "Educação Física": {
        1: ["Introdução à Educação Física", "Anatomia Humana", "História da Educação Física", "Fundamentos Socioculturais do Movimento Humano", "Biologia Celular e Histologia"],
        2: ["Fisiologia Humana", "Cinesiologia", "Aprendizagem Motora", "Psicologia do Esporte", "Metodologia Científica"],
        3: ["Biomecânica", "Fisiologia do Exercício", "Crescimento e Desenvolvimento Humano", "Atividades Aquáticas", "Medidas e Avaliação em Educação Física"],
        4: ["Treinamento Esportivo", "Atividades Gímnicas", "Esportes Coletivos I", "Lazer e Cultura", "Educação Física Adaptada"],
        5: ["Esportes Coletivos II", "Atividades Rítmicas e Expressivas", "Nutrição Aplicada ao Exercício", "Saúde Coletiva e Atividade Física", "Gestão Esportiva"],
        6: ["Esportes Individuais", "Prescrição do Exercício para Grupos Especiais", "Psicomotricidade", "Atividade Física e Envelhecimento", "Estágio Supervisionado I"],
        7: ["Treinamento de Força e Condicionamento", "Atividade Física e Doenças Crônicas", "Organização de Eventos Esportivos", "Estágio Supervisionado II", "Pesquisa em Educação Física"],
        8: ["Estágio Supervisionado III", "Trabalho de Conclusão de Curso", "Ética e Legislação Profissional", "Projeto Integrador em Educação Física"],
    },
    "Marketing": {
        1: ["Fundamentos de Marketing", "Comportamento do Consumidor", "Comunicação e Produção de Texto", "Introdução à Administração", "Pesquisa de Mercado I"],
        2: ["Marketing Estratégico", "Marketing Digital I", "Gestão de Marcas", "Estatística Aplicada a Marketing", "Jornada e Experiência do Cliente"],
        3: ["Marketing de Conteúdo", "Mídias Sociais e Comunidades Digitais", "Pesquisa de Mercado II", "Publicidade e Promoção", "Marketing de Serviços"],
        4: ["SEO e Marketing de Busca", "Publicidade Digital e Mídia Paga", "CRM e Relacionamento com Clientes", "Análise de Dados de Marketing", "Design de Experiência do Usuário"],
        5: ["Planejamento de Campanhas", "Marketing de Produto", "Comércio Eletrônico", "Marketing B2B", "Gestão Comercial"],
        6: ["Marketing de Performance", "Marketing de Influência", "Branding e Posicionamento", "Precificação e Estratégia de Valor", "Marketing de Varejo"],
        7: ["Marketing Internacional", "Pesquisa Aplicada ao Consumidor", "Ética, Privacidade e LGPD", "Gestão de Projetos de Marketing", "Plano Integrado de Marketing I"],
        8: ["Marketing Analítico", "Estratégia de Crescimento e Retenção", "Plano Integrado de Marketing II", "Projeto Final de Marketing"],
    },
    "Jornalismo": {
        1: ["Língua Portuguesa", "Produção de Texto Jornalístico I", "Estudos da Imagem", "Introdução ao Jornalismo", "História do Jornalismo", "Cidadania e Direitos Humanos"],
        2: ["Produção de Texto Jornalístico II", "Teorias da Comunicação", "Fotojornalismo", "Radiojornalismo I", "Jornalismo e Sociedade"],
        3: ["Apuração e Reportagem I", "Telejornalismo I", "Radiojornalismo II", "Comunicação e Cultura Digital", "Ética e Legislação em Jornalismo"],
        4: ["Apuração e Reportagem II", "Telejornalismo II", "Jornalismo de Dados I", "Assessoria de Comunicação", "Teorias do Jornalismo"],
        5: ["Jornalismo Investigativo", "Jornalismo Digital", "Edição Jornalística", "Jornalismo e Políticas Públicas", "Pesquisa em Comunicação"],
        6: ["Jornalismo de Dados II", "Documentário e Narrativas Audiovisuais", "Comunicação Organizacional", "Empreendedorismo em Comunicação", "Projeto Experimental I"],
        7: ["Podcast e Jornalismo Sonoro", "Fact-checking e Verificação de Informação", "Gestão de Projetos Jornalísticos", "Projeto Experimental II"],
        8: ["Estágio Supervisionado em Jornalismo", "Trabalho de Conclusão de Curso", "Prática Profissional e Portfólio"],
    },
}

# Fontes institucionais consultáveis. Para cursos cuja transcrição integral da matriz não
# foi possível obter, o status informa expressamente que a lista é uma trilha de referência.
COURSE_METADATA = {
    "ENEM": {"institution": "INEP", "version": "Matriz de Referência do ENEM", "url": "https://www.gov.br/inep/pt-br/centrais-de-conteudo/acervo-linha-editorial/publicacoes-institucionais/avaliacoes-e-exames-da-educacao-basica/matrizes-de-referencia-enem", "status": "referencia_oficial", "note": "Áreas e competências do INEP; tópicos didáticos de revisão, sem períodos universitários."},
    "Odontologia": {"institution": "UFG — Faculdade de Odontologia", "version": "Matriz ODON-BI-2, ingresso 2023-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/114575212", "status": "matriz_oficial_referenciada", "note": "Disciplinas obrigatórias listadas conforme a matriz UFG 2023; optativas não fazem parte da grade-base."},
    "Medicina": {"institution": "UFG — Faculdade de Medicina", "version": "Matriz MED-BI-3, ingresso 2022-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/114161758", "status": "matriz_oficial_referenciada", "note": "A matriz oficial usa módulos integrados e estágios sequenciais; tópicos de estudo são guias didáticos."},
    "Enfermagem": {"institution": "UFG — Faculdade de Enfermagem", "version": "Matriz ENF-BI-2, ingresso 2017-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/6311487", "status": "matriz_oficial_referenciada", "note": "Referência institucional UFG; verificar atualizações do PPC antes de usar para equivalência acadêmica."},
    "Farmácia": {"institution": "UFG — Faculdade de Farmácia", "version": "Matriz FARM-BI-2, ingresso 2017-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/6311434", "status": "referencia_institucional_parcial", "note": "Períodos iniciais baseados na matriz pública; componentes dos períodos finais precisam de conferência integral no SIGAA antes de serem tratados como oficiais."},
    "Fisioterapia": {"institution": "UFG — curso de Fisioterapia", "version": "Matriz FISIO-BI-1, ingresso 2022-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/111082559", "status": "referencia_institucional_parcial", "note": "A fonte oficial UFG 2022 está identificada, mas a transcrição componente a componente de todos os períodos ainda precisa ser conferida; roteiros de assuntos não são ementas oficiais."},
    "Medicina Veterinária": {"institution": "UFG — Escola de Veterinária e Zootecnia", "version": "matriz institucional consultada em SIGAA", "url": "https://sigaa.sistemas.ufg.br/sigaa/public/curso/curriculo.jsf?id=69678377&lc=pt_BR", "status": "referencia_institucional_parcial", "note": "Trilha distribuída por progressão formativa; confirmar todos os componentes com a matriz vigente do SIGAA."},
    "Agronomia": {"institution": "UFG — Escola de Agronomia", "version": "Matriz AGRO-BI-3, ingresso 2012-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/1394551", "status": "referencia_institucional_parcial", "note": "Primeiros períodos conferidos na matriz UFG antiga (2012); sequência restante precisa de conferência integral e possível atualização do PPC."},
    "Direito": {"institution": "UFG — Faculdade de Direito", "version": "Matriz DIRE-BN-2, ingresso 2024-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/118130122", "status": "referencia_institucional_parcial", "note": "Períodos iniciais e intermediários baseados na matriz UFG 2024; último período e ementas precisam de conferência integral no PPC/SIGAA."},
    "Administração": {"institution": "UFG — FACE", "version": "Matriz ADM-BN-2, ingresso 2017-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/6311502", "status": "referencia_institucional_parcial", "note": "Primeiros períodos baseados na matriz UFG 2017; sequência restante e ementas precisam de conferência integral."},
    "Engenharia Civil": {"institution": "UFG — Escola de Engenharia Civil e Ambiental", "version": "Matriz ENGCI-BI-2, ingresso 2009-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/1394474", "status": "referencia_institucional_parcial", "note": "A referência SIGAA é antiga (2009), não foi possível confirmar que ainda seja o PPC vigente; não tratar esta trilha como matriz oficial integral."},
    "Engenharia Mecânica": {"institution": "UFG — EMC", "version": "Matriz ENGME-BI-2, criada em 2018", "url": "https://sigaa.sistemas.ufg.br/sigaa/public/curso/curriculo.jsf?id=69673272&lc=pt_BR", "status": "referencia_institucional_parcial", "note": "Referência ao currículo UFG 2018; lista didática precisa de conferência componente a componente com a matriz detalhada."},
    "Engenharia Elétrica": {"institution": "UFG — EMC", "version": "Matriz ENGEL-BI-2, criada em 2020", "url": "https://sigaa.sistemas.ufg.br/sigaa/public/curso/curriculo.jsf?id=69678370&lc=pt_BR", "status": "referencia_institucional_parcial", "note": "Referência ao currículo UFG 2020; confirmar lista detalhada com a matriz vigente."},
    "Psicologia": {"institution": "UFG — Faculdade de Educação", "version": "Matriz PSICO-BI-3, ingresso 2024-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/118142450", "status": "referencia_institucional_parcial", "note": "Primeiros períodos baseados na matriz UFG 2024; sequência e ementas precisam de conferência integral."},
    "Biomedicina": {"institution": "UFG — Instituto de Ciências Biológicas", "version": "Matriz BIOM-BI-3, ingresso 2015-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/2140399", "status": "referencia_institucional_parcial", "note": "Matriz pública de 2015; vários períodos da sequência didática foram organizados como referência e precisam de validação pelo PPC vigente."},
    "Nutrição": {"institution": "UFG — Faculdade de Nutrição", "version": "Matriz NUT-BM-3, ingresso 2023-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/114711230", "status": "referencia_institucional_parcial", "note": "A matriz oficial UFG de 2023 confirma 10 períodos; a sequência detalhada dos períodos posteriores ao início precisa de conferência integral no SIGAA."},
    "Arquitetura e Urbanismo": {"institution": "UFG — curso de Arquitetura e Urbanismo", "version": "referência institucional UFG", "url": "https://prograd.ufg.br/n/16175-ementas-e-matrizes", "status": "referencia_institucional_parcial", "note": "A grade publicada é uma trilha de referência; verificar a matriz de ingresso e o PPC específico antes de tratá-la como oficial."},
    "Ciências Contábeis": {"institution": "UFG — FACE", "version": "Matriz CICONT-BM-3, ingresso 2015-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/2112068", "status": "referencia_institucional_parcial", "note": "Primeiros períodos baseados na matriz UFG 2015; sequência restante e ementas precisam de conferência integral."},
    "Sistemas de Informação": {"institution": "UFG — Instituto de Informática", "version": "Matriz SIINF-BN-2, ingresso 2017-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/6214319", "status": "referencia_institucional_parcial", "note": "Primeiros períodos baseados na matriz UFG 2017; sequência restante e ementas precisam de conferência integral."},
    "Ciência da Computação": {"institution": "UFG — Instituto de Informática", "version": "Matriz CICOMP-BI-4, ingresso 2024-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/118188393", "status": "referencia_institucional_parcial", "note": "Primeiros períodos baseados na matriz UFG 2024; sequência restante e ementas precisam de conferência integral. O SIGAA informa duração mínima de 8 e média de 9 períodos."},
    "Pedagogia": {"institution": "UFG — área de Educação", "version": "referência institucional UFG", "url": "https://prograd.ufg.br/n/16175-ementas-e-matrizes", "status": "referencia_institucional_parcial", "note": "Trilha de referência pedagógica; conferir a matriz/PPC do campus e da habilitação."},
    "Educação Física": {"institution": "UFG — Faculdade de Educação Física e Dança", "version": "matriz institucional consultada no SIGAA", "url": "https://sigaa.sistemas.ufg.br/sigaa/public/curso/curriculo.jsf?id=69673279&lc=pt_BR", "status": "referencia_institucional_parcial", "note": "Trilha de referência do bacharelado; conferir campus, habilitação e PPC vigente."},
    "Marketing": {"institution": "Trilha formativa independente", "version": "currículo orientativo, não é matriz oficial de graduação", "url": "https://prograd.ufg.br/n/16175-ementas-e-matrizes", "status": "trilha_nao_oficial", "note": "Não foi identificada matriz oficial específica de graduação em Marketing na UFG; não apresentar como grade curricular de universidade federal."},
    "Jornalismo": {"institution": "UFG — Faculdade de Informação e Comunicação", "version": "Matriz JORN-BM-1, ingresso 2016-1", "url": "https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/3820420", "status": "referencia_institucional_parcial", "note": "A matriz pública de 2016 foi usada como referência; a grade completa atual e as ementas precisam de conferência no PPC vigente."},
}


SPECIFIC_TOPIC_OVERRIDES: dict[tuple[str, str], list[str]] = {
    ("Odontologia", "Dentística I"): ["Diagnóstico de cárie e avaliação de risco cariológico", "Remoção seletiva de tecido cariado e preparos minimamente invasivos", "Isolamento do campo operatório e proteção do complexo dentino-pulpar", "Restaurações diretas anteriores e posteriores: indicação e execução"],
    ("Odontologia", "Dentística II"): ["Reabilitação de lesões extensas e restaurações indiretas", "Adesão em substratos dentários e longevidade restauradora", "Acabamento, polimento, ajuste oclusal e controle de falhas", "Planejamento estético funcional e seleção de materiais restauradores"],
    ("Odontologia", "Diagnóstico Bucal I"): ["Anamnese odontológica e exame extraoral e intraoral", "Descrição clínica de alterações de mucosa e tecidos moles", "Princípios de diagnóstico diferencial em lesões comuns", "Registro sistemático dos achados e encaminhamento inicial"],
    ("Odontologia", "Diagnóstico Bucal II"): ["Interpretação de exames de imagem odontológica", "Raciocínio diagnóstico para alterações periapicais e periodontais", "Seleção e interpretação de exames complementares", "Formulação de hipóteses diagnósticas com base em sinais e sintomas"],
    ("Odontologia", "Diagnóstico Bucal III"): ["Diagnóstico diferencial de lesões potencialmente malignas", "Correlação clínico-radiográfica em alterações ósseas dos maxilares", "Indicações e limites de biópsia e exames laboratoriais", "Plano de investigação e critérios de encaminhamento especializado"],
    ("Odontologia", "Diagnóstico Bucal IV"): ["Integração dos dados clínicos, radiográficos e histopatológicos", "Discussão de casos de maior complexidade diagnóstica", "Definição de prioridades e plano de cuidado integrado", "Acompanhamento longitudinal e documentação de desfechos clínicos"],
    ("Odontologia", "Clínica Infantil I"): ["Acolhimento da criança e avaliação do risco de cárie", "Prevenção individual e orientação de responsáveis", "Manejo comportamental e adaptação ao ambiente odontológico", "Procedimentos preventivos e restauradores de baixa complexidade"],
    ("Odontologia", "Clínica Infantil II"): ["Plano de tratamento integral para dentição decídua e mista", "Manejo de urgências e traumatismos dentários infantis", "Tratamento pulpar em odontopediatria: indicação e acompanhamento", "Avaliação de crescimento, desenvolvimento e encaminhamento ortodôntico"],
    ("Medicina", "Humanidades I"): ["Modelos históricos de saúde, doença e cuidado", "Determinantes sociais e culturais do processo saúde-doença", "Relação médico-paciente e comunicação clínica", "Ética, vulnerabilidade e diversidade na prática médica"],
    ("Medicina", "Humanidades II"): ["Bioética clínica e deliberação em casos complexos", "Direitos dos pacientes, autonomia e consentimento informado", "Medicalização, saúde coletiva e desigualdades", "Responsabilidade profissional e humanização do cuidado"],
    ("Medicina", "Introdução ao Cuidar I"): ["Higiene, conforto, mobilização e cuidados básicos", "Sinais vitais e observação sistemática do paciente", "Comunicação terapêutica e acolhimento", "Prevenção de eventos adversos e princípios de segurança"],
    ("Medicina", "Introdução ao Cuidar II"): ["Procedimentos básicos e técnica asséptica", "Administração segura de medicamentos e registros", "Plano de cuidados centrado na pessoa", "Trabalho multiprofissional e continuidade assistencial"],
    ("Medicina", "Determinantes Biológicos no Processo Saúde-Doença I"): ["Bases celulares e moleculares da lesão", "Inflamação, reparo tecidual e adaptação celular", "Interação agente-hospedeiro e resposta imune", "Fundamentos biológicos das manifestações clínicas"],
    ("Medicina", "Determinantes Biológicos no Processo Saúde-Doença II"): ["Mecanismos fisiopatológicos multissistêmicos", "Alterações hemodinâmicas e distúrbios metabólicos", "Carcinogênese e progressão de doenças crônicas", "Correlação entre mecanismos biológicos, exames e sintomas"],
    ("Enfermagem", "Bases para o Cuidar do Indivíduo e da Família I"): ["Processo de enfermagem: coleta de dados e identificação de necessidades", "Técnicas básicas de cuidado, higiene e conforto", "Verificação de sinais vitais e registro de enfermagem", "Comunicação e segurança no cuidado inicial"],
    ("Enfermagem", "Bases para o Cuidar do Indivíduo e da Família II"): ["Raciocínio clínico e priorização dos diagnósticos de enfermagem", "Planejamento, implementação e avaliação de cuidados", "Procedimentos de maior complexidade básica e prevenção de complicações", "Educação à família e continuidade do cuidado"],
    ("Enfermagem", "Farmacologia Básica"): ["Farmacocinética e farmacodinâmica dos principais grupos", "Cálculo de doses e vias de administração", "Interações, contraindicações e efeitos adversos", "Princípios de segurança na administração medicamentosa"],
    ("Enfermagem", "Farmacologia Aplicada à Enfermagem"): ["Administração segura em cenários clínicos e hospitalares", "Monitoramento de resposta terapêutica e eventos adversos", "Medicamentos de alto risco e dupla checagem", "Orientação ao paciente sobre uso correto e adesão"],
    ("Enfermagem", "Enfermagem Ginecológica e Obstétrica I"): ["Anatomia e fisiologia reprodutiva e planejamento reprodutivo", "Atenção pré-natal de baixo risco e avaliação materna", "Educação em saúde sexual e reprodutiva", "Identificação de sinais de alerta na gestação"],
    ("Enfermagem", "Enfermagem Ginecológica e Obstétrica II"): ["Assistência de enfermagem ao trabalho de parto e puerpério", "Cuidados imediatos ao recém-nascido", "Complicações obstétricas e resposta de enfermagem", "Atenção integral e humanizada ao ciclo gravídico-puerperal"],
    ("Enfermagem", "Enfermagem Pediátrica e Neonatológica I"): ["Crescimento e desenvolvimento infantil", "Avaliação clínica da criança e do recém-nascido", "Imunização, prevenção de acidentes e promoção da saúde", "Comunicação e cuidado centrado na família"],
    ("Enfermagem", "Enfermagem Pediátrica e Neonatológica II"): ["Cuidados de enfermagem ao neonato de risco", "Manejo de problemas clínicos pediátricos frequentes", "Sinais de deterioração e resposta rápida em pediatria", "Plano de alta, orientação familiar e continuidade do cuidado"],
    ("Psicologia", "História, Teorias e Sistemas da Psicologia I"): ["Origens filosóficas e surgimento da psicologia científica", "Estruturalismo, funcionalismo e behaviorismo clássico", "Métodos iniciais de investigação psicológica", "Contextos sociais da institucionalização da psicologia"],
    ("Psicologia", "História, Teorias e Sistemas da Psicologia II"): ["Psicanálise e teorias psicodinâmicas", "Gestalt e abordagens fenomenológicas", "Psicologia histórico-cultural e construtivismo", "Comparação crítica de pressupostos teóricos"],
    ("Psicologia", "História, Teorias e Sistemas da Psicologia III"): ["Perspectivas contemporâneas e integrativas", "Debates sobre ciência, evidência e prática psicológica", "Influência dos contextos culturais nas teorias", "Limites e contribuições dos modelos psicológicos atuais"],
    ("Psicologia", "Introdução às Ciências Sociais I"): ["Conceitos de sociedade, cultura e socialização", "Clássicos da sociologia e organização social", "Estratificação, classe e desigualdade", "Instituições sociais e produção de subjetividade"],
    ("Psicologia", "Introdução às Ciências Sociais II"): ["Raça, gênero, território e marcadores sociais", "Poder, ideologia e movimentos sociais", "Globalização, trabalho e transformações sociais", "Implicações sociais para a atuação psicológica"],
    ("Ciências Contábeis", "Contabilidade Introdutória I"): ["Patrimônio, contas e equação patrimonial", "Débito, crédito e partidas dobradas", "Escrituração de operações básicas", "Balancete e demonstrações iniciais"],
    ("Ciências Contábeis", "Contabilidade Introdutória II"): ["Ajustes de fim de período e competência", "Estoques, depreciação e provisões", "Apuração do resultado e encerramento de contas", "Balanço patrimonial e demonstração do resultado"],
    ("Ciências Contábeis", "Contabilidade Intermediária I"): ["Ativos circulantes e não circulantes", "Mensuração e reconhecimento contábil", "Passivos, provisões e contingências", "Apresentação e divulgação de demonstrações"],
    ("Ciências Contábeis", "Contabilidade Intermediária II"): ["Instrumentos financeiros e investimentos", "Arrendamentos, impairment e recuperabilidade", "Patrimônio líquido e distribuição de resultados", "Análise de políticas e estimativas contábeis"],
    ("Sistemas de Informação", "Algoritmos e Estruturas de Dados 1"): ["Análise de complexidade básica", "Vetores, listas e pilhas", "Filas, recursão e ordenação", "Testes e escolha de estruturas para problemas"],
    ("Sistemas de Informação", "Algoritmos e Estruturas de Dados 2"): ["Árvores e árvores de busca", "Tabelas hash e tratamento de colisões", "Grafos e algoritmos de percurso", "Análise comparativa de algoritmos e estruturas"],
    ("Ciência da Computação", "Algoritmos e Estruturas de Dados 1"): ["Tipos abstratos de dados e análise de complexidade", "Vetores, listas, pilhas e filas", "Algoritmos de busca e ordenação", "Implementação, testes e avaliação de desempenho"],
    ("Ciência da Computação", "Algoritmos e Estruturas de Dados 2"): ["Árvores balanceadas e heaps", "Grafos, caminhos e conectividade", "Tabelas hash e estruturas indexadas", "Provas de corretude e análise assintótica"],
    ("Engenharia Elétrica", "Circuitos Elétricos I"): ["Leis de Kirchhoff e análise nodal", "Circuitos resistivos em corrente contínua", "Teoremas de Thévenin e Norton", "Análise transitória de circuitos de primeira ordem"],
    ("Engenharia Elétrica", "Circuitos Elétricos II"): ["Regime senoidal e fasores", "Potência ativa, reativa e fator de potência", "Resposta em frequência e ressonância", "Circuitos trifásicos e correção de fator de potência"],
    ("Engenharia Elétrica", "Máquinas Elétricas I"): ["Transformadores monofásicos e trifásicos", "Circuito equivalente e ensaios", "Regulação de tensão e rendimento", "Aplicações e proteção de transformadores"],
    ("Engenharia Elétrica", "Máquinas Elétricas II"): ["Máquinas de indução e síncronas", "Máquinas de corrente contínua", "Partida, controle de velocidade e frenagem", "Ensaios, perdas e seleção de máquinas"],
    ("Engenharia Mecânica", "Termodinâmica I"): ["Propriedades de substâncias puras", "Primeira lei e balanços de energia", "Sistemas fechados e volumes de controle", "Ciclos de potência e refrigeração introdutórios"],
    ("Engenharia Mecânica", "Termodinâmica II"): ["Segunda lei e entropia", "Exergia e irreversibilidades", "Ciclos de potência e refrigeração avançados", "Análise energética e eficiência de sistemas térmicos"],
    ("Nutrição", "Dietoterapia I"): ["Planejamento dietético para doenças prevalentes", "Prescrição nutricional e metas terapêuticas", "Adequação de consistência e fracionamento alimentar", "Monitoramento da resposta clínica e nutricional"],
    ("Nutrição", "Dietoterapia II"): ["Terapia nutricional em condições clínicas complexas", "Nutrição enteral e parenteral: indicação e monitoramento", "Interação fármaco-nutriente e manejo de complicações", "Protocolos interdisciplinares e avaliação de desfechos"],
    ("Pedagogia", "Alfabetização e Letramento I"): ["Sistema de escrita alfabética e consciência fonológica", "Hipóteses de escrita e diagnóstico inicial", "Práticas sociais de leitura e escrita", "Planejamento de intervenções iniciais de alfabetização"],
    ("Pedagogia", "Alfabetização e Letramento II"): ["Fluência, compreensão e produção de textos", "Diversidade linguística e dificuldades de aprendizagem", "Avaliação formativa da alfabetização", "Sequências didáticas e acompanhamento de progresso"],
    ("Jornalismo", "Produção de Texto Jornalístico I"): ["Critérios de noticiabilidade e estrutura da notícia", "Lide, sublide e pirâmide invertida", "Apuração, checagem e atribuição de fontes", "Edição de texto informativo e clareza"],
    ("Jornalismo", "Produção de Texto Jornalístico II"): ["Reportagem, perfil e entrevista em profundidade", "Narrativa, contexto e diversidade de fontes", "Edição de reportagens e revisão factual", "Ética, linguagem e prevenção de vieses"],
}


# Segunda revisão: assuntos progressivos e específicos para evitar que matérias
# de nomes próximos/etapas I-II recebam o mesmo roteiro genérico.
SPECIFIC_TOPIC_OVERRIDES.update({
    ("Enfermagem", "Introdução à Enfermagem"): ["História e identidade profissional da enfermagem", "Lei do exercício profissional, código de ética e responsabilidades", "Organização dos serviços, equipe e processo de trabalho", "Fundamentos da observação, comunicação e registro de enfermagem"],
    ("Enfermagem", "Sociologia e Saúde"): ["Saúde como fenômeno social e historicamente construído", "Desigualdades sociais, território e acesso ao SUS", "Cultura, gênero, raça e determinantes sociais", "Implicações sociais para o cuidado e as políticas públicas"],
    ("Enfermagem", "Antropologia da Saúde"): ["Representações culturais de corpo, adoecimento e cura", "Práticas populares de cuidado e relação com os serviços", "Diversidade cultural, interculturalidade e comunicação", "Etnografia e análise antropológica de situações de cuidado"],
    ("Enfermagem", "Trabalho de Conclusão de Curso I"): ["Delimitação do problema e justificativa da pesquisa", "Objetivos, pergunta de pesquisa e revisão inicial", "Escolha do delineamento e construção do projeto", "Ética em pesquisa e preparação para submissão ao comitê"],
    ("Enfermagem", "Trabalho de Conclusão de Curso II"): ["Execução do plano de pesquisa aprovado", "Organização e análise dos dados coletados", "Discussão dos resultados frente à literatura", "Redação final, normalização e defesa do trabalho"],
    ("Farmácia", "Bioquímica Clínica"): ["Marcadores bioquímicos de função renal e hepática", "Perfil glicêmico, lipídico e avaliação metabólica", "Controle de qualidade e interpretação de resultados laboratoriais", "Correlação clínico-laboratorial e limites de referência"],
    ("Farmácia", "Química e Bioquímica de Alimentos"): ["Composição química e valor nutricional dos alimentos", "Transformações bioquímicas no processamento e armazenamento", "Reações de escurecimento, oxidação e estabilidade", "Métodos de análise e interpretação de parâmetros de qualidade"],
    ("Farmácia", "Farmacologia Básica"): ["Farmacodinâmica: receptores, agonismo e antagonismo", "Farmacocinética: absorção, distribuição e eliminação", "Relação dose-resposta e variabilidade individual", "Bases para uso racional e seguro de medicamentos"],
    ("Farmácia", "Farmacologia I"): ["Farmacologia autonômica e neurotransmissão", "Anti-inflamatórios, analgésicos e fármacos relacionados", "Fármacos cardiovasculares: mecanismos e indicações", "Efeitos adversos, contraindicações e interações relevantes"],
    ("Farmácia", "Farmacologia II"): ["Fármacos que atuam no sistema nervoso central", "Antimicrobianos: mecanismos, espectro e resistência", "Fármacos endócrinos e metabólicos", "Seleção terapêutica, monitoramento e segurança clínica"],
    ("Farmácia", "Farmacocinética Aplicada"): ["Modelos farmacocinéticos e parâmetros de exposição", "Biodisponibilidade, bioequivalência e concentração plasmática", "Ajuste de dose por função renal, hepática e faixa etária", "Monitorização terapêutica e aplicações em casos clínicos"],
    ("Farmácia", "Toxicologia Geral"): ["Princípios de toxicidade, exposição e relação dose-efeito", "Absorção, distribuição, biotransformação e eliminação de tóxicos", "Avaliação de risco, biomarcadores e limites de exposição", "Condutas iniciais e prevenção de intoxicações"],
    ("Farmácia", "Toxicologia Aplicada"): ["Toxicologia de medicamentos, drogas e produtos químicos", "Diagnóstico e interpretação de síndromes tóxicas", "Antídotos, descontaminação e suporte ao intoxicado", "Toxicovigilância, cadeia de exposição e prevenção"],
    ("Farmácia", "Trabalho de Conclusão de Curso I"): ["Pergunta, hipótese e objetivos do projeto farmacêutico", "Revisão bibliográfica e método de investigação", "Plano de coleta, análise e gestão de dados", "Ética, biossegurança e submissões necessárias"],
    ("Farmácia", "Trabalho de Conclusão de Curso II"): ["Execução e documentação do estudo aprovado", "Análise crítica dos resultados", "Discussão das implicações farmacêuticas e limitações", "Redação científica, referências e defesa"],
    ("Fisioterapia", "Anatomia Humana I"): ["Planos, eixos, termos e organização anatômica", "Osteologia e artrologia dos membros", "Miologia e principais ações musculares", "Anatomia funcional aplicada à postura e ao movimento"],
    ("Fisioterapia", "Anatomia Humana II"): ["Anatomia do tronco e cavidades corporais", "Sistemas cardiovascular e respiratório: organização anatômica", "Sistema nervoso periférico e vias de inervação", "Correlação anatômica com avaliação funcional e clínica"],
    ("Fisioterapia", "Fisiologia Humana I"): ["Membranas celulares, excitabilidade e sinalização", "Fisiologia neuromuscular e contração", "Controle cardiovascular e hemodinâmica", "Ventilação, transporte de gases e trocas respiratórias"],
    ("Fisioterapia", "Fisiologia Humana II"): ["Filtração renal e equilíbrio hidroeletrolítico", "Digestão, absorção e regulação metabólica", "Controle endócrino e resposta ao estresse", "Integração dos sistemas na atividade física e na doença"],
    ("Fisioterapia", "Fisiologia do Exercício"): ["Respostas agudas cardiovasculares e respiratórias ao exercício", "Metabolismo energético e limiares fisiológicos", "Adaptações ao treinamento aeróbio e resistido", "Prescrição, monitoramento e segurança do exercício"],
    ("Fisioterapia", "Trabalho de Conclusão de Curso I"): ["Construção da pergunta clínica e objetivos", "Revisão de evidências e escolha do desenho de estudo", "Protocolo, instrumentos de avaliação e análise planejada", "Ética em pesquisa e elaboração do projeto"],
    ("Fisioterapia", "Trabalho de Conclusão de Curso II"): ["Coleta e organização de dados da pesquisa", "Análise estatística ou qualitativa dos resultados", "Discussão clínica, limitações e aplicabilidade", "Redação final e apresentação do estudo"],
    ("Medicina Veterinária", "Anatomia dos Animais Domésticos I"): ["Terminologia anatômica veterinária e planos corporais", "Osteologia comparada dos animais domésticos", "Articulações e músculos do aparelho locomotor", "Anatomia topográfica dos membros e correlação clínica"],
    ("Medicina Veterinária", "Anatomia dos Animais Domésticos II"): ["Anatomia comparada das cavidades torácica e abdominal", "Sistema digestório e variações entre espécies", "Sistema urogenital e anatomia reprodutiva", "Sistema nervoso, cabeça e pescoço em espécies domésticas"],
    ("Medicina Veterinária", "Fisiologia Animal I"): ["Fisiologia celular e homeostase", "Neurofisiologia, músculo e controle motor", "Função cardiovascular e respiratória", "Regulação da temperatura e adaptação ao ambiente"],
    ("Medicina Veterinária", "Fisiologia Animal II"): ["Fisiologia gastrointestinal comparada e digestão por espécie", "Função renal e balanço hídrico", "Endocrinologia e metabolismo", "Fisiologia reprodutiva, lactação e gestação"],
    ("Medicina Veterinária", "Parasitologia Veterinária I"): ["Protozoários de interesse veterinário e seus ciclos", "Helmintos: morfologia, transmissão e patogenia", "Relações hospedeiro-parasito e epidemiologia", "Diagnóstico coproparasitológico e prevenção"],
    ("Medicina Veterinária", "Parasitologia Veterinária II"): ["Ectoparasitos de importância clínica e produtiva", "Ciclos complexos e zoonoses parasitárias", "Resistência a antiparasitários e manejo integrado", "Diagnóstico diferencial e controle por espécie e ambiente"],
    ("Medicina Veterinária", "Farmacologia Veterinária I"): ["Princípios farmacocinéticos e farmacodinâmicos em animais", "Fármacos do sistema nervoso autônomo e central", "Analgésicos, anestésicos e anti-inflamatórios", "Variação de dose, espécie, segurança e resíduos"],
    ("Medicina Veterinária", "Farmacologia Veterinária II"): ["Antimicrobianos e uso prudente na clínica veterinária", "Fármacos cardiovasculares, endócrinos e gastrointestinais", "Terapêutica por espécie e condição clínica", "Interações, farmacovigilância e prevenção de resistência"],
    ("Medicina Veterinária", "Toxicologia Veterinária"): ["Plantas tóxicas, micotoxinas e contaminantes", "Intoxicações por fármacos, pesticidas e metais", "Coleta de amostras e diagnóstico toxicológico", "Descontaminação, tratamento e prevenção em rebanhos e animais de companhia"],
    ("Agronomia", "Entomologia Agrícola I"): ["Morfologia, fisiologia e identificação dos principais grupos de insetos", "Ciclo de vida e dinâmica populacional de pragas", "Amostragem e monitoramento de insetos no campo", "Relações entre insetos, cultura hospedeira e dano econômico"],
    ("Agronomia", "Entomologia Agrícola II"): ["Manejo integrado de pragas e níveis de ação", "Controle biológico e conservação de inimigos naturais", "Resistência a inseticidas e manejo de resistência", "Planejamento de estratégias de controle por cultura e sistema produtivo"],
    ("Agronomia", "Grandes Culturas I"): ["Planejamento e implantação de culturas anuais de verão", "Cultivares, semeadura, população e arranjo de plantas", "Manejo nutricional e fitossanitário durante o ciclo", "Colheita, produtividade e avaliação técnico-econômica"],
    ("Agronomia", "Grandes Culturas II"): ["Sistemas de produção de culturas de inverno e segunda safra", "Rotação, sucessão e integração de culturas", "Manejo de riscos climáticos e de mercado", "Qualidade de grãos, armazenamento e sustentabilidade produtiva"],
    ("Agronomia", "Projeto de Trabalho de Conclusão de Curso"): ["Definição de problema agronômico e justificativa", "Revisão de literatura e hipótese", "Desenho experimental, amostragem e análise planejada", "Cronograma, orçamento e protocolo de pesquisa"],
    ("Agronomia", "Trabalho de Conclusão de Curso"): ["Execução e registro do experimento ou estudo de campo", "Análise de dados e interpretação agronômica", "Discussão dos resultados e implicações para o manejo", "Redação científica, referências e apresentação final"],
    ("Direito", "Direito Civil I (Parte Geral)"): ["Pessoas naturais e jurídicas e capacidade civil", "Bens, fatos jurídicos, atos e negócios jurídicos", "Defeitos, invalidade, prescrição e decadência", "Aplicação da Parte Geral do Código Civil em casos"],
    ("Direito", "Direito Civil II (Obrigações)"): ["Estrutura e modalidades das obrigações", "Adimplemento, pagamento e extinção obrigacional", "Inadimplemento, mora, perdas e danos", "Transmissão das obrigações e responsabilidade patrimonial"],
    ("Direito", "Direito Civil III (Contratos)"): ["Princípios contratuais e formação do contrato", "Classificação, interpretação e efeitos contratuais", "Vícios, revisão, resolução e extinção dos contratos", "Contratos típicos e análise de casos concretos"],
    ("Direito", "Direito Civil IV (Responsabilidade Civil)"): ["Responsabilidade subjetiva e objetiva", "Conduta, culpa, nexo causal e dano indenizável", "Responsabilidade por fato de terceiro, produto e serviço", "Quantificação de danos e jurisprudência aplicada"],
    ("Direito", "Direito Civil V (Reais)"): ["Posse, proteção possessória e seus efeitos", "Propriedade, função social e aquisição", "Direitos reais sobre coisa alheia e garantias", "Condomínio, usucapião e conflitos imobiliários"],
    ("Direito", "Direito Civil VI (Família)"): ["Casamento, união estável e regime de bens", "Filiação, poder familiar e proteção de crianças", "Alimentos, guarda e convivência familiar", "Tutela, curatela e soluções consensuais de conflitos"],
    ("Direito", "Direito Civil VII (Sucessões)"): ["Abertura da sucessão e transmissão hereditária", "Sucessão legítima e ordem de vocação hereditária", "Testamentos, legados e capacidade testamentária", "Inventário, partilha e planejamento sucessório"],
    ("Direito", "Direito Penal I"): ["Princípios penais e aplicação da lei penal no tempo e espaço", "Teoria do crime: tipicidade, ilicitude e culpabilidade", "Dolo, culpa, erro e imputabilidade", "Concurso de pessoas e iter criminis"],
    ("Direito", "Direito Penal II"): ["Penas: espécies, aplicação e individualização", "Concurso de crimes e dosimetria da pena", "Suspensão, substituição e execução penal", "Extinção da punibilidade e efeitos da condenação"],
    ("Direito", "Direito Penal III"): ["Crimes contra a pessoa e a vida", "Crimes contra patrimônio, dignidade sexual e liberdade", "Crimes contra administração pública e fé pública", "Tipificação, concurso e jurisprudência penal aplicada"],
    ("Direito", "Direito Constitucional I"): ["Constituição, poder constituinte e supremacia constitucional", "Princípios fundamentais e direitos individuais", "Direitos sociais, nacionalidade e direitos políticos", "Organização político-administrativa do Estado"],
    ("Direito", "Direito Constitucional II"): ["Organização e competências dos Poderes", "Controle concentrado e difuso de constitucionalidade", "Processo legislativo e funções essenciais à justiça", "Ordem econômica, social e jurisprudência constitucional"],
    ("Direito", "Trabalho de Conclusão de Curso I"): ["Delimitação do tema, problema e hipótese jurídica", "Revisão bibliográfica e marco normativo/jurisprudencial", "Metodologia e estrutura provisória dos capítulos", "Projeto, cronograma e normalização acadêmica"],
    ("Direito", "Trabalho de Conclusão de Curso II"): ["Desenvolvimento argumentativo e revisão dos capítulos", "Análise crítica da legislação e da jurisprudência", "Conclusões, limites e propostas de interpretação", "Revisão técnica, referências e defesa"],
    ("Engenharia Civil", "Materiais de Construção I"): ["Propriedades físicas e mecânicas de materiais de construção", "Agregados, aglomerantes e caracterização laboratorial", "Dosagem inicial e controle de qualidade", "Normas técnicas, recebimento e armazenamento de materiais"],
    ("Engenharia Civil", "Materiais de Construção II"): ["Concreto: dosagem, produção, transporte e cura", "Aço, madeira, polímeros e materiais de vedação", "Durabilidade, patologia e desempenho dos sistemas", "Seleção de materiais conforme exigência de projeto e ambiente"],
    ("Engenharia Civil", "Resistência dos Materiais I"): ["Esforços internos e equilíbrio de barras", "Tensão, deformação e propriedades mecânicas", "Tração, compressão, cisalhamento e torção", "Diagramas de esforço e dimensionamento básico"],
    ("Engenharia Civil", "Resistência dos Materiais II"): ["Flexão simples e composta", "Flambagem e estabilidade de barras", "Estado plano de tensões e critérios de falha", "Deslocamentos, energia de deformação e aplicações estruturais"],
    ("Engenharia Civil", "Mecânica dos Solos I"): ["Origem, composição e classificação dos solos", "Índices físicos, granulometria e limites de consistência", "Permeabilidade e tensões efetivas", "Compactação e investigação geotécnica inicial"],
    ("Engenharia Civil", "Mecânica dos Solos II"): ["Resistência ao cisalhamento e envoltórias de ruptura", "Adensamento e recalques", "Empuxos de terra e estabilidade de taludes", "Capacidade de carga e dimensionamento geotécnico"],
    ("Engenharia Civil", "Construção Civil I"): ["Planejamento do canteiro e serviços preliminares", "Fundações, estrutura e sequência executiva", "Leitura de projetos, quantitativos e medições", "Segurança, produtividade e controle de execução"],
    ("Engenharia Civil", "Construção Civil II"): ["Sistemas de vedação, revestimento e acabamento", "Instalações prediais e compatibilização", "Patologias construtivas, inspeção e manutenção", "Orçamento, planejamento físico-financeiro e entrega da obra"],
    ("Engenharia Mecânica", "Materiais de Engenharia I"): ["Estrutura atômica, ligações e organização cristalina", "Diagramas de fases e transformações", "Propriedades mecânicas e ensaios", "Seleção de metais para componentes mecânicos"],
    ("Engenharia Mecânica", "Materiais de Engenharia II"): ["Tratamentos térmicos e termoquímicos", "Polímeros, cerâmicas e compósitos", "Corrosão, fadiga, fluência e mecanismos de falha", "Seleção de materiais e análise de falhas em serviço"],
    ("Engenharia Mecânica", "Processos de Fabricação I"): ["Fundição e conformação mecânica", "Usinagem convencional e parâmetros de corte", "Tolerâncias dimensionais e acabamento superficial", "Planejamento de processo e segurança operacional"],
    ("Engenharia Mecânica", "Processos de Fabricação II"): ["Soldagem e união de materiais", "Manufatura aditiva e processos não convencionais", "Automação, CNC e integração de células de produção", "Inspeção, qualidade e seleção de processo por peça"],
    ("Engenharia Elétrica", "Introdução à Programação"): ["Tipos de dados, variáveis e expressões", "Estruturas de seleção e repetição", "Funções, modularização e arquivos", "Testes e soluções computacionais para problemas elétricos"],
    ("Psicologia", "Psicologia do Desenvolvimento I"): ["Desenvolvimento pré-natal, nascimento e primeira infância", "Apego, linguagem e desenvolvimento socioemocional inicial", "Desenvolvimento cognitivo e motor na infância", "Métodos de observação e avaliação do desenvolvimento infantil"],
    ("Psicologia", "Psicologia do Desenvolvimento II"): ["Desenvolvimento na adolescência e construção da identidade", "Vida adulta, relações, trabalho e parentalidade", "Envelhecimento, cognição e mudanças psicossociais", "Trajetórias de desenvolvimento e fatores de proteção/risco"],
    ("Psicologia", "Psicologia Social I"): ["Bases históricas e principais teorias da psicologia social", "Cognição social, atribuição e formação de atitudes", "Influência social, conformidade e relações intergrupais", "Métodos de investigação de processos sociais"],
    ("Psicologia", "Psicologia Social II"): ["Identidade social, preconceito e discriminação", "Poder, ideologia e representações sociais", "Grupos, instituições, participação e movimentos sociais", "Intervenção psicossocial e análise de contextos comunitários"],
    ("Psicologia", "Psicopatologia I"): ["Sinais, sintomas e exame do estado mental", "Transtornos de ansiedade, humor e trauma", "Classificação diagnóstica e diagnóstico diferencial", "Entrevista clínica, risco e encaminhamento responsável"],
    ("Psicologia", "Psicopatologia II"): ["Transtornos psicóticos e da personalidade", "Transtornos relacionados a substâncias e comportamento alimentar", "Condições neurocognitivas e comorbidades", "Formulação de caso, evidências e limites do diagnóstico"],
    ("Psicologia", "Trabalho de Conclusão de Curso I"): ["Pergunta de pesquisa, hipótese e objetivos", "Revisão de literatura e fundamentação teórica", "Método, instrumentos, amostra e ética", "Projeto e plano de análise de dados"],
    ("Psicologia", "Trabalho de Conclusão de Curso II"): ["Coleta, organização e tratamento dos dados", "Análise dos resultados e diálogo com teoria", "Discussão, limitações e implicações profissionais", "Redação final e apresentação pública"],
    ("Biomedicina", "Anatomia Humana I"): ["Terminologia anatômica, osteologia e artrologia", "Miologia e aparelho locomotor", "Sistema cardiovascular e respiratório: anatomia", "Correlação de estruturas com exames e prática biomédica"],
    ("Biomedicina", "Anatomia Humana II"): ["Sistema digestório e órgãos anexos", "Sistemas urinário e reprodutor", "Sistema nervoso, órgãos dos sentidos e endocrinologia anatômica", "Topografia e correlações clínico-laboratoriais"],
    ("Biomedicina", "Histologia I e Embriologia"): ["Tecidos epitelial, conjuntivo, adiposo e cartilaginoso", "Tecidos ósseo, muscular e nervoso", "Gametogênese, fecundação e implantação", "Organogênese e desenvolvimento embrionário inicial"],
    ("Biomedicina", "Histologia II"): ["Histologia integrada dos sistemas cardiovascular e respiratório", "Tecidos do sistema digestório e glândulas anexas", "Rim, vias urinárias e sistema reprodutor", "Reconhecimento microscópico e correlações patológicas"],
    ("Biomedicina", "Bioquímica"): ["Estrutura de proteínas, carboidratos, lipídios e ácidos nucleicos", "Enzimas, cinética e regulação metabólica", "Glicólise, ciclo de Krebs e fosforilação oxidativa", "Metabolismo integrado em jejum, alimentação e exercício"],
    ("Biomedicina", "Bioquímica Clínica"): ["Marcadores de função renal e equilíbrio hidroeletrolítico", "Perfil hepático, glicêmico e lipídico", "Enzimas, proteínas plasmáticas e marcadores de lesão", "Interpretação, controle de qualidade e valores de referência"],
    ("Biomedicina", "Genética"): ["Leis de Mendel e padrões de herança", "Citogenética e alterações cromossômicas", "Heredogramas, aconselhamento e risco genético", "Genética de populações e doenças hereditárias"],
    ("Biomedicina", "Genética Molecular"): ["Replicação, transcrição e tradução", "Regulação da expressão gênica e epigenética", "PCR, sequenciamento e métodos moleculares", "Aplicação molecular no diagnóstico e medicina personalizada"],
    ("Nutrição", "Técnica Dietética I"): ["Métodos de cocção e alterações físicas dos alimentos", "Fatores de correção, rendimento e porcionamento", "Planejamento de preparações e fichas técnicas", "Avaliação sensorial e padronização de receitas"],
    ("Nutrição", "Técnica Dietética II"): ["Planejamento de cardápios e adequação nutricional", "Modificações de consistência e dietas especiais", "Produção em escala e controle do processo", "Análise de custo, aceitabilidade e qualidade da refeição"],
    ("Nutrição", "Nutrição nos Ciclos da Vida I"): ["Necessidades nutricionais na gestação e lactação", "Alimentação do lactente e aleitamento materno", "Introdução alimentar e nutrição na primeira infância", "Avaliação antropométrica de gestantes e crianças"],
    ("Nutrição", "Nutrição nos Ciclos da Vida II"): ["Necessidades nutricionais na adolescência", "Avaliação e planejamento alimentar do adulto", "Envelhecimento, sarcopenia e risco nutricional", "Intervenções nutricionais por fase da vida e contexto social"],
    ("Nutrição", "Administração de Unidades de Alimentação e Nutrição I"): ["Estrutura e dimensionamento de unidades de alimentação", "Planejamento de cardápios, compras e estoque", "Fluxos de produção, pessoal e equipamentos", "Custos, fichas técnicas e produtividade"],
    ("Nutrição", "Administração de Unidades de Alimentação e Nutrição II"): ["Gestão de qualidade e segurança dos alimentos", "Boas práticas, POPs e análise de perigos", "Indicadores de desperdício e avaliação de satisfação", "Liderança, auditoria e melhoria contínua de serviços"],
    ("Nutrição", "Trabalho de Conclusão de Curso I"): ["Problema de pesquisa em alimentação e nutrição", "Revisão de evidências e hipótese", "Método, amostra, instrumentos e análise planejada", "Ética, protocolo e cronograma do projeto"],
    ("Nutrição", "Trabalho de Conclusão de Curso II"): ["Coleta e tratamento de dados nutricionais", "Análise estatística ou qualitativa", "Discussão com literatura e limitações", "Redação, normalização e apresentação final"],
    ("Arquitetura e Urbanismo", "História da Arte e da Arquitetura I"): ["Arquitetura e arte da Antiguidade ao mundo medieval", "Sistemas construtivos e formas espaciais históricas", "Arquitetura clássica e tradição tratadística", "Leitura crítica de edifícios e contextos históricos"],
    ("Arquitetura e Urbanismo", "História da Arquitetura II"): ["Renascimento, barroco e transformações urbanas", "Revolução industrial e arquitetura moderna", "Modernismo, crítica e arquitetura contemporânea", "Patrimônio, conservação e interpretação historiográfica"],
    ("Ciências Contábeis", "Contabilidade de Custos I"): ["Classificação de custos, despesas e investimentos", "Custeio por absorção e departamentalização", "Materiais, mão de obra e custos indiretos", "Apuração de custo de produto e resultado"],
    ("Ciências Contábeis", "Contabilidade de Custos II"): ["Custeio variável, margem de contribuição e ponto de equilíbrio", "Custeio baseado em atividades (ABC)", "Custos-padrão, análise de variações e orçamento", "Decisão gerencial, mix de produtos e precificação"],
    ("Ciências Contábeis", "Auditoria I"): ["Planejamento, materialidade e risco de auditoria", "Controles internos e testes de controles", "Evidências, amostragem e documentação", "Procedimentos de auditoria em contas patrimoniais"],
    ("Ciências Contábeis", "Auditoria II"): ["Auditoria de resultados e estimativas contábeis", "Fraudes, partes relacionadas e eventos subsequentes", "Relatórios, opinião modificada e comunicação", "Qualidade, independência e normas profissionais"],
    ("Ciências Contábeis", "Trabalho de Conclusão de Curso I"): ["Problema contábil, objetivo e justificativa", "Referencial teórico e revisão de literatura", "Método, amostra, fonte de dados e análise", "Projeto de pesquisa e requisitos éticos"],
    ("Ciências Contábeis", "Trabalho de Conclusão de Curso II"): ["Coleta e tratamento de dados contábeis", "Análise dos resultados e confronto com a literatura", "Implicações gerenciais/regulatórias e limitações", "Redação, normalização e defesa"],
    ("Sistemas de Informação", "Banco de Dados I"): ["Modelagem conceitual e diagramas entidade-relacionamento", "Modelo relacional, chaves e integridade", "Álgebra relacional e normalização", "SQL de definição e manipulação de dados"],
    ("Sistemas de Informação", "Banco de Dados II"): ["Índices, planos de consulta e otimização", "Transações, concorrência e recuperação", "Segurança, autorização e auditoria de acesso", "NoSQL, replicação e arquitetura de dados distribuídos"],
    ("Sistemas de Informação", "Redes de Computadores I"): ["Modelos OSI/TCP-IP e camada de enlace", "Endereçamento IPv4/IPv6 e sub-redes", "Roteamento e protocolos básicos", "Diagnóstico de conectividade e análise de pacotes"],
    ("Sistemas de Informação", "Redes de Computadores II"): ["Serviços de rede, DNS, DHCP e autenticação", "Roteamento avançado, VLANs e redundância", "Segurança, monitoramento e desempenho de redes", "Arquiteturas sem fio, nuvem e resolução de incidentes"],
    ("Ciência da Computação", "Banco de Dados"): ["Projeto conceitual, lógico e normalização", "SQL, integridade e transações", "Índices, otimização e plano de consultas", "Persistência, segurança e recuperação de dados"],
    ("Ciência da Computação", "Sistemas Operacionais"): ["Processos, threads e escalonamento", "Memória virtual e gerenciamento de páginas", "Sistemas de arquivos e dispositivos de entrada/saída", "Concorrência, sincronização e segurança do sistema"],
    ("Ciência da Computação", "Programação Funcional"): ["Funções puras, imutabilidade e transparência referencial", "Funções de alta ordem e composição", "Tipos algébricos, recursão e avaliação preguiçosa", "Testabilidade e uso de abstrações funcionais"],
    ("Pedagogia", "Psicologia da Educação I"): ["Teorias da aprendizagem e desenvolvimento na infância", "Behaviorismo, cognitivismo e contribuições para o ensino", "Motivação, atenção e memória na aprendizagem", "Observação do desenvolvimento e implicações pedagógicas"],
    ("Pedagogia", "Psicologia da Educação II"): ["Abordagens histórico-culturais e aprendizagem mediada", "Desenvolvimento socioemocional e relações escolares", "Dificuldades de aprendizagem e necessidades de apoio", "Aplicação de teorias psicológicas ao planejamento docente"],
    ("Pedagogia", "Educação Infantil I"): ["Direitos da criança e concepções de infância", "Brincadeira, interação e organização dos ambientes", "Campos de experiência e planejamento pedagógico", "Observação, documentação e avaliação na educação infantil"],
    ("Pedagogia", "Educação Infantil II"): ["Currículo integrado e práticas para bebês e crianças pequenas", "Literatura, artes, movimento e exploração do mundo", "Inclusão, diversidade e parceria com famílias", "Projeto pedagógico, transições e avaliação formativa"],
    ("Educação Física", "Fisiologia Humana"): ["Fisiologia celular e controle neuromuscular", "Função cardiovascular e transporte de oxigênio", "Ventilação pulmonar e trocas gasosas", "Homeostase e integração dos sistemas em repouso"],
    ("Educação Física", "Fisiologia do Exercício"): ["Respostas agudas ao exercício e sistemas energéticos", "Limiar ventilatório, VO2 e fadiga", "Adaptações ao treinamento aeróbio e de força", "Prescrição, monitoramento e recuperação do exercício"],
    ("Educação Física", "Cinesiologia"): ["Planos e eixos de movimento e terminologia", "Ações musculares e análise de movimentos fundamentais", "Amplitude articular e controle motor", "Análise cinesiológica de gestos motores básicos"],
    ("Educação Física", "Biomecânica"): ["Cinemática linear e angular do movimento", "Forças internas/externas, torque e alavancas", "Impulso, quantidade de movimento e equilíbrio", "Análise biomecânica do gesto esportivo e prevenção de lesões"],
    ("Marketing", "Pesquisa de Mercado I"): ["Definição do problema de mercado e objetivos", "Pesquisa exploratória, desk research e dados secundários", "Amostragem, questionário e roteiro de entrevista", "Coleta inicial, qualidade e organização dos dados"],
    ("Marketing", "Pesquisa de Mercado II"): ["Desenhos descritivos e causais e testes de hipótese", "Análise de dados quantitativos e qualitativos", "Segmentação baseada em evidências e insights", "Relatório executivo, recomendações e apresentação de resultados"],
    ("Jornalismo", "Produção de Texto Jornalístico I"): ["Critérios de noticiabilidade e estrutura da notícia", "Lide, sublide e pirâmide invertida", "Apuração, checagem e atribuição de fontes", "Edição de texto informativo e clareza"],
    ("Jornalismo", "Produção de Texto Jornalístico II"): ["Reportagem, perfil e entrevista em profundidade", "Narrativa, contexto e diversidade de fontes", "Edição de reportagens e revisão factual", "Ética, linguagem e prevenção de vieses"],
    ("Jornalismo", "Radiojornalismo I"): ["Linguagem radiofônica, roteiro e estrutura de boletim", "Locução, dicção, respiração e leitura de texto", "Captação, edição básica e paisagem sonora", "Produção e apresentação de notícias para rádio"],
    ("Jornalismo", "Radiojornalismo II"): ["Reportagem sonora, entrevista e entrada ao vivo", "Montagem, edição avançada e desenho de som", "Podcast, distribuição digital e métricas de audiência", "Ética, direitos autorais e verificação no áudio"],
    ("Jornalismo", "Telejornalismo I"): ["Linguagem audiovisual e estrutura de telejornal", "Roteiro, texto para televisão e cabeça/nota", "Enquadramento, captação e operação básica de câmera", "Edição de reportagem e sincronização áudio-vídeo"],
    ("Jornalismo", "Telejornalismo II"): ["Reportagem externa e produção de pauta audiovisual", "Passagem, stand-up e entrevista para TV", "Edição narrativa, imagens de cobertura e gráficos", "Transmissão ao vivo, checagem e responsabilidade editorial"],
})

def study_topics(course: str, discipline: str, period: int) -> list[str]:
    """Create discipline-specific study outlines; these are learning guides, not official ementa text."""
    override = SPECIFIC_TOPIC_OVERRIDES.get((course, discipline))
    if override:
        return list(override)
    d = discipline.casefold()
    # ENEM uses the tested-area topic map defined in seed.py, not this helper.
    roman = None
    for token, value in [(" xii", 12), (" xi", 11), (" x", 10), (" ix", 9), (" viii", 8), (" vii", 7), (" vi", 6), (" v", 5), (" iv", 4), (" iii", 3), (" ii", 2), (" i", 1)]:
        if d.endswith(token):
            roman = value
            break
    if "método clínico" in d:
        progressive = {1: ["Comunicação clínica e acolhimento", "Anamnese e história clínica", "Exame físico introdutório", "Registro clínico e segurança do paciente"], 2: ["Raciocínio clínico inicial", "Exame físico por sistemas", "Hipóteses diagnósticas", "Registro e apresentação de casos"], 3: ["Integração de sinais, sintomas e exames", "Diagnóstico diferencial", "Plano de investigação clínica", "Discussão de casos clínicos integrados"], 4: ["Raciocínio clínico avançado", "Decisão diagnóstica e terapêutica", "Comunicação de más notícias", "Segurança e qualidade da assistência"]}
        return progressive.get(roman, progressive[1])
    if "módulo integrador" in d:
        return {1: ["Integração entre forma, função e saúde", "Bases científicas do problema clínico", "Aprendizagem baseada em problemas", "Comunicação e trabalho em equipe"], 2: ["Integração entre sistemas fisiológicos", "Relações entre saúde e ambiente", "Discussão de problemas clínicos", "Pesquisa e síntese científica"], 3: ["Integração de mecanismos de doença", "Formulação de hipóteses", "Leitura crítica de evidências", "Construção de plano de estudo clínico"], 4: ["Integração clínica e comunitária", "Prioridades de diagnóstico", "Análise de evidências clínicas", "Apresentação de caso integrado"]}.get(roman, ["Integração teórico-prática", "Análise de problemas clínicos", "Discussão em equipe", "Síntese de evidências"])
    if "corpo humano saudável" in d:
        return {1: ["Organização do corpo e homeostase", "Biologia celular e tecidos", "Sistema locomotor e tegumentar", "Fundamentos de anatomia e fisiologia"], 2: ["Integração cardiovascular e respiratória", "Sistema digestório e metabolismo", "Sistema renal e equilíbrio hidroeletrolítico", "Sistema nervoso e regulação endócrina"]}.get(roman, ["Fisiologia dos sistemas humanos", "Mecanismos de homeostase", "Integração entre sistemas", "Variações fisiológicas e envelhecimento"])
    if "saúde, família e comunidade" in d:
        return {1: ["Princípios e organização do SUS", "Atenção primária à saúde", "Território, família e determinantes sociais", "Promoção e prevenção em saúde"], 2: ["Estratégia Saúde da Família", "Planejamento local em saúde", "Vigilância e indicadores territoriais", "Participação social e controle social"], 3: ["Redes de atenção à saúde", "Epidemiologia comunitária", "Coordenação do cuidado", "Avaliação de ações de saúde"], 4: ["Gestão do cuidado em rede", "Equidade e vulnerabilidades", "Políticas públicas de saúde", "Avaliação de intervenções comunitárias"]}.get(roman, ["Atenção primária", "Determinantes sociais", "Vigilância em saúde", "Planejamento territorial"])
    if "anatomia de cabeça e pescoço" in d:
        return ["Ossos do crânio, face e articulação temporomandibular", "Músculos da mastigação e expressão facial", "Nervos cranianos e inervação orofacial", "Vascularização, espaços fasciais e anatomia cervical"]
    if "anatomia e escultura dental" in d:
        return ["Morfologia de dentes decíduos e permanentes", "Oclusão e relações intermaxilares", "Anatomia de superfícies e acidentes dentários", "Escultura dental e reprodução morfológica"]
    if "histologia e desenvolvimento buco-dental" in d:
        return ["Odontogênese e formação dos tecidos dentários", "Histologia de esmalte, dentina e cemento", "Polpa e tecidos periodontais", "Desenvolvimento craniofacial e erupção dentária"]
    if "dentística" in d:
        return ["Diagnóstico e classificação das lesões cariosas", "Princípios de preparo e preservação de estrutura dental", "Sistemas adesivos e materiais restauradores", "Técnicas restauradoras e controle de qualidade"]
    if "diagnóstico bucal" in d:
        return ["Anamnese e exame clínico estomatológico", "Diagnóstico diferencial de lesões orais", "Exames complementares e interpretação de imagens", "Plano de cuidado, encaminhamento e registro clínico"]
    if "clínica de atenção básica" in d or "clínica integrada" in d or "clínica infantil" in d:
        stage = roman or period
        return [f"Avaliação clínica e plano de cuidado — etapa {stage}", f"Execução de procedimentos clínicos supervisionados — etapa {stage}", f"Controle de risco, biossegurança e acompanhamento — etapa {stage}", f"Registro clínico, comunicação e continuidade do cuidado — etapa {stage}"]
    if "estágio" in d:
        return [f"Planejamento de atividades e objetivos do estágio em {discipline}", f"Procedimentos e protocolos do campo de prática em {course}", "Ética, biossegurança e registro das atividades", "Avaliação reflexiva de casos e desenvolvimento profissional"]
    if "trabalho de conclusão" in d or d.startswith("tcc"):
        if d.endswith(" i") or "projeto" in d:
            return ["Delimitação do problema, pergunta e objetivos", "Revisão de literatura e fundamentação teórica", "Desenho metodológico, ética e plano de análise", "Projeto, cronograma, referências e submissões necessárias"]
        if d.endswith(" ii") or "defesa" in d:
            return ["Execução do método aprovado e organização dos dados", "Análise, interpretação e confronto com a literatura", "Discussão dos achados, limitações e aplicações", "Redação final, normalização e apresentação/defesa"]
        return ["Problema, objetivos e justificativa do trabalho", "Revisão bibliográfica e método científico", "Análise, interpretação e discussão dos resultados", "Redação acadêmica, referências e apresentação"]
    # Casos adicionais observados na auditoria de listas idênticas.
    if "psicologia aplicada à enfermagem" in d:
        return ["Desenvolvimento humano, comportamento e respostas ao adoecimento", "Comunicação terapêutica, vínculo e relação profissional-paciente", "Aspectos psicossociais da adesão, dor e hospitalização", "Limites de atuação, encaminhamento e cuidado interdisciplinar"]
    if "práticas de enfermagem em saúde coletiva" in d:
        return ["Territorialização, diagnóstico comunitário e cadastro familiar", "Planejamento de ações de prevenção e promoção", "Busca ativa, visitas domiciliares e acompanhamento de grupos", "Indicadores locais, registro e avaliação das intervenções"]
    if d.endswith("administração em enfermagem i"):
        return ["Teorias de administração e organização do serviço de enfermagem", "Dimensionamento, escala, distribuição e supervisão da equipe", "Comunicação, liderança e tomada de decisão cotidiana", "Indicadores operacionais e avaliação da qualidade assistencial"]
    if d.endswith("administração em enfermagem ii"):
        return ["Gestão de custos, recursos materiais e dimensionamento de pessoal", "Gestão de risco, indicadores e acreditação", "Planejamento estratégico e avaliação do serviço", "Gestão de conflitos, mudança e melhoria contínua"]
    if "ética e exercício da enfermagem" in d:
        return ["Lei do exercício profissional e atribuições da equipe", "Código de ética, sigilo e responsabilidade por atos", "Processo ético, documentação e direitos do paciente", "Dilemas de cuidado, vulnerabilidade e tomada de decisão ética"]
    if "enfermagem hebiátrica" in d:
        return ["Puberdade, mudanças físicas e desenvolvimento psicossocial", "Saúde sexual, reprodutiva e prevenção de agravos", "Imunização, saúde mental e prevenção de violências", "Acolhimento do adolescente, confidencialidade e rede de proteção"]
    if "enfermagem psiquiátrica" in d:
        return ["Avaliação de necessidades psicossociais e exame do estado mental", "Cuidado em liberdade, projeto terapêutico singular e RAPS", "Manejo de crise, prevenção do suicídio e redução de danos", "Reabilitação psicossocial, família e direitos da pessoa em sofrimento mental"]
    if "saúde mental" in d and course == "Enfermagem":
        return ["Conceitos de saúde mental e determinantes do sofrimento psíquico", "Acolhimento, escuta qualificada e vínculo terapêutico", "Promoção, prevenção e cuidado comunitário", "Rede psicossocial, reforma psiquiátrica e direitos dos usuários"]
    if "farmacotécnica e cosmetologia" in d:
        return ["Formas farmacêuticas semissólidas, líquidas e sólidas", "Matérias-primas cosméticas, emulsões, géis e estabilidade", "Cálculos, escalonamento e controles de processo", "Desenvolvimento de formulações e rotulagem segura"]
    if "tecnologia farmacêutica" in d:
        return ["Operações unitárias e equipamentos de produção farmacêutica", "Granulação, compressão, revestimento e encapsulação", "Validação de processo, estabilidade e embalagem", "Boas práticas de fabricação e controle de desvios"]
    if "fundamentos da administração" in d and course == "Farmácia":
        return ["Estrutura organizacional e funções gerenciais", "Planejamento, organização, direção e controle", "Custos, orçamento e indicadores de desempenho", "Liderança, processos e tomada de decisão em serviços farmacêuticos"]
    if "gestão de serviços farmacêuticos" in d:
        return ["Planejamento estratégico e modelos de serviços farmacêuticos", "Gestão de pessoas, processos, custos e contratos", "Indicadores de qualidade, acesso e resultados em saúde", "Inovação, avaliação econômica e melhoria dos serviços"]
    if "semiologia e farmacoterapia" in d:
        return ["Anamnese, sinais, sintomas e parâmetros clínicos", "Identificação de problemas relacionados à farmacoterapia", "Seleção de metas, monitoramento e plano terapêutico", "Seguimento clínico, documentação e comunicação interprofissional"]
    if "farmácia clínica" in d:
        return ["Revisão sistemática da farmacoterapia e conciliação", "Identificação e resolução de problemas relacionados a medicamentos", "Monitoramento de efetividade, segurança e adesão", "Registro clínico e atuação integrada à equipe assistencial"]
    if "assistência farmacêutica no sus" in d:
        return ["Política Nacional de Assistência Farmacêutica e componentes do SUS", "Protocolos clínicos, listas de medicamentos e acesso", "Programação, financiamento e dispensação no sistema público", "Indicadores de acesso, uso racional e avaliação de políticas"]
    if "assistência farmacêutica em serviços de saúde" in d:
        return ["Ciclo da assistência farmacêutica no serviço de saúde", "Seleção, aquisição, armazenamento e distribuição", "Dispensação, acompanhamento e segurança do medicamento", "Organização local, indicadores e gestão de desabastecimentos"]

    if course == "Fisioterapia":
        if d.endswith("musculoesquelética i"): return ["Avaliação de dor e disfunções articulares periféricas", "Testes ortopédicos, amplitude e força muscular", "Intervenção inicial em lesões traumato-ortopédicas", "Educação, exercício terapêutico e critérios de progressão"]
        if d.endswith("musculoesquelética ii"): return ["Avaliação de coluna e disfunções musculoesqueléticas complexas", "Reabilitação pós-operatória e retorno à função", "Terapia manual e exercício em quadros persistentes", "Desfechos funcionais e prevenção de recidivas"]
        if "respiratória" in d: return ["Avaliação ventilatória, ausculta e testes funcionais", "Higiene brônquica e técnicas de expansão pulmonar", "Treinamento muscular respiratório e reabilitação", "Monitoramento de resposta, segurança e critérios de interrupção"]
        if "cardiovascular" in d: return ["Avaliação cardiovascular e estratificação de risco", "Resposta hemodinâmica ao exercício e teste funcional", "Prescrição de exercício em cardiopatias", "Monitoramento, contraindicações e reabilitação cardíaca"]
        if d.endswith("neurológica i"): return ["Avaliação do tônus, força, sensibilidade e reflexos", "Princípios de controle motor e neuroplasticidade", "Intervenção em alterações neurológicas iniciais", "Treino de equilíbrio, marcha e funcionalidade básica"]
        if d.endswith("neurológica ii"): return ["Reabilitação em condições neurológicas crônicas e complexas", "Treino orientado à tarefa e recuperação funcional", "Tecnologias assistivas e adaptação ambiental", "Mensuração de independência, participação e qualidade de vida"]
        if "pediátrica" in d: return ["Avaliação do desenvolvimento neuropsicomotor", "Intervenções precoces e estimulação funcional", "Condições neuromotoras e respiratórias na infância", "Participação familiar, brincar e metas funcionais"]
        if "geriátrica" in d: return ["Avaliação da funcionalidade, fragilidade e risco de queda", "Treinamento de força, equilíbrio e mobilidade", "Sarcopenia, multimorbidade e prevenção de incapacidade", "Planos de cuidado, ambiente seguro e autonomia do idoso"]
        if "terapia intensiva" in d: return ["Avaliação e monitoramento do paciente crítico", "Mobilização precoce e prevenção de complicações da imobilidade", "Suporte ventilatório e interação paciente-ventilador", "Critérios de segurança, progressão e desfechos em UTI"]
        if "saúde da mulher" in d: return ["Assoalho pélvico e avaliação funcional pélvica", "Fisioterapia na gestação, parto e puerpério", "Incontinência, dor pélvica e disfunções uroginecológicas", "Educação, exercício terapêutico e cuidado centrado na pessoa"]
        if "esportiva" in d: return ["Avaliação funcional e biomecânica do gesto esportivo", "Prevenção de lesões e manejo de carga", "Reabilitação por fases e critérios de retorno ao esporte", "Monitoramento de desempenho e redução de risco de recidiva"]
        if "dermatofuncional" in d: return ["Avaliação tegumentar, cicatrizes e alterações de tecido", "Recursos físicos e técnicas aplicadas com segurança", "Cuidados em pós-operatório e reparo tecidual", "Contraindicações, evidência e acompanhamento de resultados"]
        if "do trabalho" in d: return ["Análise ergonômica de tarefas e postos de trabalho", "Riscos biomecânicos e organização do trabalho", "Prevenção de distúrbios musculoesqueléticos ocupacionais", "Programas de saúde do trabalhador e avaliação de resultados"]
        if "saúde coletiva" in d: return ["Perfil funcional e necessidades de reabilitação no território", "Atenção primária, prevenção de incapacidades e educação em saúde", "Trabalho multiprofissional e rede de cuidados", "Acessibilidade, participação social e avaliação de intervenções"]
        if "eletrotermofoto" in d: return ["Princípios físicos de correntes, calor, frio e luz", "Indicações, parâmetros dosimétricos e contraindicações", "Aplicação supervisionada e monitoramento da resposta", "Segurança, evidências e integração com exercício terapêutico"]
        if "cinesioterapia" in d: return ["Princípios de exercício terapêutico e prescrição", "Mobilização articular, alongamento e fortalecimento", "Treino de coordenação, equilíbrio e função", "Dosagem, progressão e mensuração de resultados"]
        if "cinesiologia" in d: return ["Planos, eixos e descrição dos movimentos articulares", "Ações musculares e análise cinesiológica", "Amplitude, alavancas e estabilidade articular", "Análise de gestos funcionais e alterações de movimento"]
        if "biomecânica" in d: return ["Cinemática e cinética do movimento humano", "Força, torque, alavancas e centro de massa", "Marcha, postura e distribuição de cargas", "Análise quantitativa de movimentos e implicações clínicas"]

    if d.endswith("histologia veterinária i"):
        return ["Métodos histológicos, microscopia e preparo de lâminas", "Tecidos epiteliais e conjuntivos em espécies domésticas", "Cartilagem, osso, sangue e tecido muscular", "Correlação entre organização microscópica e função"]
    if d.endswith("histologia veterinária ii"):
        return ["Histologia dos sistemas digestório e respiratório animais", "Rim, vias urinárias e órgãos reprodutivos", "Glândulas endócrinas, pele e órgãos linfoides", "Reconhecimento microscópico comparado e correlações patológicas"]
    if "embriologia veterinária" in d:
        return ["Gametogênese, fecundação e clivagem embrionária", "Gastrulação, folhetos embrionários e neurulação", "Placenta, membranas fetais e desenvolvimento por espécie", "Teratogênese, gestação e desenvolvimento pré-natal"]
    if "patologia geral veterinária" in d:
        return ["Lesão celular, necrose, apoptose e adaptações", "Inflamação, reparo, distúrbios circulatórios e choque", "Neoplasia e respostas sistêmicas à doença", "Mecanismos patológicos e correlação macro/microscópica"]
    if "patologia especial veterinária" in d:
        return ["Patologia do sistema respiratório e cardiovascular animal", "Patologia digestória, hepática e pancreática", "Patologia renal, reprodutiva e neurológica", "Diagnóstico diferencial por espécie e integração anatomoclínica"]

    if "introdução à agronomia" in d:
        return ["História, campos de atuação e papel social da agronomia", "Sistemas agrícolas, cadeias produtivas e políticas do setor", "Princípios de sustentabilidade e uso responsável de insumos", "Organização da propriedade rural e diagnóstico inicial de sistemas"]
    if "forragicultura" in d:
        return ["Espécies forrageiras e adaptação edafoclimática", "Implantação, adubação e manejo do pastejo", "Conservação de forragem: feno e silagem", "Produtividade, valor nutritivo e planejamento forrageiro"]
    if "zootecnia geral" in d:
        return ["Bases de melhoramento, reprodução e manejo animal", "Nutrição, ambiência e bem-estar dos animais de produção", "Sistemas de produção e índices zootécnicos", "Biosseguridade, sustentabilidade e avaliação econômica"]
    if "plantas daninhas" in d:
        return ["Identificação, biologia e banco de sementes de plantas daninhas", "Interferência, competição e período crítico de controle", "Métodos preventivo, cultural, mecânico e químico", "Manejo integrado e resistência a herbicidas"]
    if "agroecologia" in d:
        return ["Princípios ecológicos e desenho de agroecossistemas", "Biodiversidade funcional, ciclagem e saúde do solo", "Sistemas agroflorestais e práticas de baixo impacto", "Transição agroecológica, indicadores e participação comunitária"]
    if "hidráulica e irrigação" in d:
        return ["Hidrostática, vazão e energia em condutos", "Perdas de carga, bombas e dimensionamento de tubulações", "Sistemas de irrigação e uniformidade de aplicação", "Manejo da irrigação por clima, solo e demanda da cultura"]
    if "economia rural" in d:
        return ["Oferta, demanda, custos e formação de preços agropecuários", "Mercados agrícolas, sazonalidade e comercialização", "Crédito rural, risco e políticas agrícolas", "Indicadores econômicos e avaliação de alternativas produtivas"]
    if "gestão de propriedades rurais" in d:
        return ["Planejamento, inventário e organização da propriedade", "Custos de produção, fluxo de caixa e indicadores", "Gestão de pessoas, máquinas e insumos agrícolas", "Tomada de decisão, sucessão e avaliação de desempenho rural"]
    if "gestão ambiental rural" in d:
        return ["Legislação ambiental rural e regularização da propriedade", "Áreas de preservação, reserva legal e uso do solo", "Gestão de resíduos, água e conservação de recursos naturais", "Indicadores ambientais e planos de adequação sustentável"]

    if "relações de gênero e direito" in d:
        return ["Gênero, sexo, identidade e construção social das desigualdades", "Direitos humanos, igualdade e proteção contra discriminação", "Violência de gênero, políticas públicas e acesso à justiça", "Jurisprudência e instrumentos jurídicos nacionais e internacionais"]
    if "teoria geral do processo" in d:
        return ["Jurisdição, ação, processo e acesso à justiça", "Princípios constitucionais e garantias processuais", "Competência, sujeitos e atos processuais", "Pressupostos processuais e formas de solução de conflitos"]
    if "história do direito" in d:
        return ["Instituições jurídicas da Antiguidade e tradição romana", "Formação do direito medieval e moderno", "Codificação, constitucionalismo e direito brasileiro", "Contexto histórico na interpretação das instituições jurídicas"]
    if "direito digital" in d:
        return ["Proteção de dados pessoais, LGPD e bases legais", "Responsabilidade civil por conteúdo e serviços digitais", "Provas eletrônicas, contratos e identidade digital", "Plataformas, inteligência artificial e desafios regulatórios"]
    if "pesquisa e direito i" in d or "pesquisa e direito ii" in d:
        if " i " in f" {d} ": return ["Delimitação do problema jurídico e pergunta de pesquisa", "Busca em legislação, doutrina e jurisprudência", "Métodos de pesquisa jurídica e construção do referencial", "Projeto, citações, ética e plano de análise"]
        return ["Análise e sistematização de fontes jurídicas", "Interpretação crítica da legislação e dos precedentes", "Argumentação, resultados e discussão", "Redação científica, normalização e apresentação do estudo"]
    if "hermenêutica jurídica" in d:
        return ["Métodos literal, sistemático, histórico e teleológico", "Regras, princípios e ponderação jurídica", "Argumentação, precedentes e coerência decisória", "Interpretação de casos difíceis e justificação da decisão"]
    if "direito agrário" in d:
        return ["Estatuto da Terra, função social e propriedade rural", "Contratos agrários, arrendamento e parceria", "Reforma agrária, regularização e conflitos fundiários", "Política agrícola, meio ambiente e jurisprudência agrária"]
    if "políticas públicas e direito" in d:
        return ["Ciclo de políticas públicas e definição de problemas", "Competências estatais, orçamento e implementação", "Controle judicial e limites de intervenção", "Avaliação de políticas, direitos sociais e evidências"]
    if "direito financeiro" in d:
        return ["Receita pública, tributos e repartição de receitas", "Orçamento público, PPA, LDO e LOA", "Despesa, crédito público e responsabilidade fiscal", "Controle financeiro, transparência e prestação de contas"]
    if "direito do consumidor" in d:
        return ["Relação de consumo, vulnerabilidade e direitos básicos", "Oferta, publicidade, práticas abusivas e contratos", "Responsabilidade por vício/fato de produto e serviço", "Tutela coletiva, órgãos de defesa e solução de conflitos"]
    if "direito tributário" in d:
        return ["Sistema tributário, competências e limitações ao poder de tributar", "Obrigação, crédito tributário e lançamento", "Suspensão, extinção, exclusão e garantias do crédito", "Processo tributário, execução fiscal e jurisprudência"]
    if "direito ambiental" in d:
        return ["Princípios ambientais, competências e licenciamento", "Responsabilidade civil, administrativa e penal ambiental", "Proteção de biodiversidade, água e áreas protegidas", "Instrumentos processuais e solução de conflitos socioambientais"]
    if "direito previdenciário" in d:
        return ["Seguridade social e regimes previdenciários", "Qualidade de segurado, dependentes e carência", "Benefícios, cálculo, manutenção e revisão", "Processo administrativo/judicial e jurisprudência previdenciária"]
    if "direito internacional público" in d:
        return ["Fontes, sujeitos e personalidade jurídica internacional", "Tratados, responsabilidade internacional e solução de controvérsias", "Organizações internacionais e sistema ONU", "Direitos humanos, uso da força e cooperação internacional"]
    if "direito internacional privado" in d:
        return ["Conflitos de leis no espaço e regras de conexão", "Jurisdição internacional e competência", "Reconhecimento de decisões estrangeiras e cooperação jurídica", "Família, contratos e negócios transnacionais"]

    if "introdução à administração pública" in d:
        return ["Modelos de administração pública e evolução do Estado", "Princípios constitucionais e organização administrativa", "Políticas públicas, participação e controle social", "Transparência, integridade e avaliação de serviços públicos"]
    if "fundamentos de contabilidade" in d:
        return ["Patrimônio, equação patrimonial e variações", "Contas, débito/crédito e partidas dobradas", "Escrituração e demonstrações contábeis básicas", "Leitura de balanço e resultado para decisão gerencial"]
    if "teoria das organizações" in d:
        return ["Estruturas organizacionais e divisão do trabalho", "Abordagens clássicas, humanas e contingenciais", "Cultura, poder, conflito e mudança organizacional", "Desenho organizacional e análise de casos empresariais"]
    if "microeconomia" in d:
        return ["Oferta, demanda, equilíbrio e elasticidades", "Preferências, utilidade e decisão do consumidor", "Produção, custos e decisões da firma", "Estruturas de mercado e análise de eficiência"]
    if "macroeconomia" in d:
        return ["Produto, renda e indicadores macroeconômicos", "Inflação, desemprego e ciclos econômicos", "Política monetária, fiscal e cambial", "Crescimento, setor externo e avaliação de conjuntura"]
    if "empreendedorismo e inovação" in d or "empreendedorismo em ti" in d:
        return ["Identificação de oportunidades e proposta de valor", "Modelos de negócio, validação e descoberta de clientes", "Custos, financiamento e indicadores de viabilidade", "Experimentação, inovação e desenvolvimento do empreendimento"]
    if "gestão socioambiental" in d:
        return ["Sustentabilidade, materialidade e partes interessadas", "Gestão de impactos, riscos e conformidade ambiental", "Indicadores ESG, relatórios e responsabilidade social", "Economia circular e integração socioambiental à estratégia"]
    if "direito processual do trabalho" in d:
        return ["Competência da Justiça do Trabalho e organização judiciária", "Reclamação trabalhista, defesa, audiência e prova", "Sentença, liquidação, execução e meios de impugnação", "Recursos trabalhistas, precedentes e prática processual"]
    if "direito econômico" in d:
        return ["Ordem econômica constitucional e papel do Estado", "Concorrência, regulação e defesa do mercado", "Abuso de poder econômico, concentração e sanções", "Análise de casos regulatórios e políticas econômicas"]
    if "direitos da criança" in d:
        return ["Doutrina da proteção integral e prioridade absoluta", "Direitos da criança, adolescente, pessoa idosa e pessoa com deficiência", "Medidas protetivas, acessibilidade e políticas de atendimento", "Sistema de garantias, responsabilização e tutela coletiva"]
    if "filosofia moral" in d:
        return ["Ética normativa: virtudes, deveres e consequências", "Liberdade, responsabilidade e dilemas morais", "Justiça, dignidade e teorias contemporâneas", "Argumentação ética aplicada a problemas profissionais"]
    if "filosofia do direito" in d:
        return ["Conceitos de justiça, validade, eficácia e legitimidade", "Jusnaturalismo, positivismo e pós-positivismo", "Direito, moral, linguagem e interpretação", "Crítica das instituições e fundamentos da autoridade jurídica"]
    if "educação para relações étnico-raciais" in d:
        return ["História e contribuição de povos africanos, afro-brasileiros e indígenas", "Racismo estrutural, discriminação e desigualdades", "Direitos humanos, políticas afirmativas e legislação educacional", "Práticas antirracistas, reparação e acesso à justiça"]
    if "processo constitucional" in d:
        return ["Jurisdição constitucional e legitimidade do controle", "Ações de controle concentrado e seus efeitos", "Remédios constitucionais e tutela de direitos fundamentais", "Precedentes, decisões estruturais e processo constitucional"]
    if "administração financeira i" in d and course == "Administração":
        return ["Matemática financeira e valor do dinheiro no tempo", "Orçamento, capital de giro e projeção de caixa", "Análise de demonstrativos e indicadores financeiros", "Decisões de curto prazo e gestão de liquidez"]
    if "finanças corporativas" in d:
        return ["Custo de capital e estrutura ótima de financiamento", "Avaliação de investimentos e fluxo de caixa descontado", "Risco, retorno, dividendos e valuation", "Decisões corporativas, governança e criação de valor"]
    if "gestão de operações" in d:
        return ["Estratégia de operações e desenho de processos", "Planejamento de capacidade, estoque e cadeia de suprimentos", "Produtividade, gargalos e melhoria contínua", "Indicadores operacionais e qualidade do serviço/produto"]
    if "administração da produção" in d:
        return ["Planejamento agregado, MRP e programação da produção", "Sequenciamento, capacidade e controle do chão de fábrica", "Manutenção, confiabilidade e disponibilidade de equipamentos", "Produtividade, perdas e avaliação do sistema produtivo"]
    if "gestão da qualidade" in d:
        return ["Sistemas da qualidade, normalização e requisitos", "Ferramentas estatísticas e análise de causa", "Auditoria, não conformidade e ação corretiva", "Melhoria contínua, experiência do cliente e indicadores"]
    if "pesquisa operacional" in d:
        return ["Modelagem de problemas e programação linear", "Métodos de otimização e análise de sensibilidade", "Filas, simulação e tomada de decisão sob restrição", "Interpretação de soluções e aplicação a operações"]
    if "investigação e métodos em psicologia" in d:
        return ["Pergunta de pesquisa, hipótese e variáveis psicológicas", "Métodos observacionais, experimentais e correlacionais", "Amostragem, validade de instrumentos e confiabilidade", "Ética, análise de dados e comunicação científica"]
    if "psicologia e processos educativos" in d:
        return ["Desenvolvimento, aprendizagem e contexto escolar", "Relações entre escola, família e comunidade", "Inclusão, dificuldades de aprendizagem e encaminhamento", "Intervenção institucional, prevenção e avaliação de resultados"]
    if "psicologia da aprendizagem" in d:
        return ["Condicionamento, memória e processos cognitivos", "Motivação, atenção e autorregulação", "Aprendizagem social, construtivismo e mediação", "Avaliação de estratégias de aprendizagem e diferenças individuais"]
    if "psicologia escolar e educacional" in d:
        return ["A escola como instituição e campo de intervenção", "Queixas escolares, fracasso escolar e análise institucional", "Trabalho com docentes, famílias e equipes multiprofissionais", "Práticas inclusivas, políticas educacionais e prevenção"]
    if "epidemiologia e saúde coletiva" in d and course == "Fisioterapia":
        return ["Indicadores de saúde, incidência, prevalência e risco", "Desenhos epidemiológicos e interpretação de medidas", "Vigilância, prevenção e determinantes sociais", "Planejamento de ações de saúde e avaliação de programas"]
    if "fisioterapia em saúde coletiva" in d:
        return ["Necessidades de reabilitação e funcionalidade no território", "Ações de prevenção de incapacidade na atenção primária", "Acessibilidade, participação social e cuidado em rede", "Planejamento, registro e avaliação de intervenção comunitária"]
    if "fitopatologia geral" in d:
        return ["Triângulo da doença e interação patógeno-hospedeiro-ambiente", "Sintomas, sinais, diagnóstico e ciclos de doenças", "Epidemiologia, disseminação e condições favoráveis", "Princípios de manejo integrado e prevenção fitossanitária"]
    if "fitopatologia aplicada" in d:
        return ["Diagnóstico de doenças das principais culturas agrícolas", "Monitoramento, limiares e tomada de decisão em campo", "Controle cultural, genético, biológico e químico integrado", "Resistência, manejo de fungicidas e sustentabilidade"]
    if "fisiologia vegetal" in d:
        return ["Fotossíntese, respiração e metabolismo vegetal", "Relações hídricas e transporte de água e solutos", "Nutrição mineral, crescimento e reguladores vegetais", "Respostas a estresses e produtividade das plantas"]
    if "anatomia e fisiologia dos animais domésticos" in d:
        return ["Organização anatômica e sistemas dos animais domésticos", "Fisiologia digestiva comparada e metabolismo", "Sistemas cardiovascular, respiratório e renal", "Reprodução, termorregulação e adaptação por espécie"]
    if "hidráulica e irrigação" in d:
        return ["Princípios de hidráulica, vazão e pressão em condutos", "Bombas, perdas de carga e seleção de equipamentos", "Dimensionamento e operação de sistemas irrigantes", "Uniformidade, eficiência hídrica e manejo da aplicação"]
    if "irrigação e drenagem" in d:
        return ["Estimativa da evapotranspiração e demanda de água", "Métodos de irrigação e programação por solo/clima", "Drenagem agrícola e controle do lençol freático", "Salinidade, eficiência de uso e sustentabilidade hídrica"]
    if "metodologia científica" in d and course == "Sistemas de Informação":
        return ["Problema de pesquisa e revisão de literatura em computação", "Métodos empíricos, experimentais e estudos de caso", "Coleta, análise e reprodutibilidade de dados", "Ética, escrita científica e comunicação de resultados"]
    if "auditoria e controle de sistemas" in d:
        return ["Riscos, controles internos e governança de TI", "Auditoria de acesso, mudanças, operações e dados", "Conformidade, evidências e relatórios de auditoria", "Planos de correção, monitoramento e melhoria do controle"]
    if "gestão de serviços de ti" in d:
        return ["Catálogo, nível de serviço e central de atendimento", "Gestão de incidentes, problemas e mudanças", "Disponibilidade, continuidade e capacidade de serviços", "Indicadores, melhoria contínua e experiência do usuário"]
    if "redes de computadores" in d and course == "Ciência da Computação":
        return ["Arquitetura TCP/IP, enlace e endereçamento", "Roteamento, transporte e serviços de rede", "Protocolos, captura de pacotes e diagnóstico", "Segurança, desempenho e aplicações distribuídas"]
    if "teoria da computação" in d:
        return ["Autômatos finitos e linguagens regulares", "Gramáticas livres de contexto e autômatos de pilha", "Máquinas de Turing, decidibilidade e reduções", "Complexidade computacional e classes de problemas"]
    if "compiladores" in d:
        return ["Análise léxica e especificação de tokens", "Parsing, gramáticas e árvore sintática", "Análise semântica, tabela de símbolos e tipos", "Geração de código, otimização e tratamento de erros"]
    if "análise de algoritmos" in d:
        return ["Notação assintótica e análise de recorrências", "Divisão e conquista, programação dinâmica e gulosa", "Grafos, fluxo e algoritmos clássicos", "Prova de corretude e comparação de complexidade"]
    if "computação gráfica" in d:
        return ["Transformações geométricas 2D/3D e sistemas de coordenadas", "Projeção, câmera, iluminação e materiais", "Rasterização, curvas e modelagem geométrica", "Renderização, visualização e avaliação de desempenho"]
    if "pesquisa em computação" in d:
        return ["Formulação da questão e revisão sistemática da literatura", "Desenho experimental, comparação e métricas", "Reprodutibilidade, conjuntos de dados e análise", "Escrita científica, limitações e apresentação de resultados"]
    if "projeto integrador em computação" in d:
        return ["Levantamento de requisitos e análise de stakeholders", "Arquitetura, planejamento e desenvolvimento incremental", "Testes, segurança, documentação e validação com usuários", "Entrega, demonstração, avaliação e retrospectiva de equipe"]
    if "educação de jovens e adultos" in d:
        return ["História, legislação e sujeitos da EJA", "Currículo, trabalho e experiências de vida dos estudantes", "Alfabetização, letramento e práticas contextualizadas", "Planejamento, avaliação e permanência escolar"]
    if "tecnologias na educação" in d:
        return ["Tecnologias digitais e ambientes virtuais de aprendizagem", "Desenho de atividades, recursos e acessibilidade digital", "Letramento midiático e avaliação de fontes", "Privacidade, ética e avaliação de aprendizagem com tecnologia"]
    if "educação do campo" in d:
        return ["História, sujeitos e direitos da educação do campo", "Território, trabalho, identidade e pedagogias contextualizadas", "Educação intercultural, povos tradicionais e diversidade", "Políticas públicas, práticas comunitárias e avaliação educativa"]
    if "libras" in d:
        return ["Parâmetros linguísticos e estrutura gramatical da Libras", "Comunidade surda, cultura e identidade", "Legislação, acessibilidade e educação bilíngue", "Comunicação acessível, interpretação e práticas inclusivas"]
    if "planejamento e gestão escolar" in d:
        return ["Projeto político-pedagógico e planejamento participativo", "Organização, financiamento e legislação da gestão escolar", "Liderança, colegiados e relações com a comunidade", "Avaliação institucional, indicadores e prestação de contas"]
    if "comunicação e produção de texto" in d:
        return ["Comunicação profissional, clareza e estrutura textual", "Argumentação, síntese, coesão e revisão", "Gêneros de comunicação corporativa e digital", "Adequação de linguagem, público e objetivo"]
    if "projeto final de marketing" in d:
        return ["Definição do problema, público e proposta de valor", "Plano de execução, recursos, cronograma e responsabilidades", "Indicadores, metas e monitoramento da implementação", "Resultados, recomendações e apresentação do projeto"]
    if "seo e marketing de busca" in d:
        return ["Pesquisa de palavras-chave, intenção e arquitetura de conteúdo", "SEO técnico, rastreabilidade, indexação e desempenho", "SEO on-page, autoridade e experiência da página", "Mensuração orgânica, auditoria e plano de otimização"]
    if "publicidade digital e mídia paga" in d:
        return ["Objetivos de campanha, segmentação e estrutura de contas", "Criativos, lances, orçamento e estratégias de audiência", "Pixel/UTM, atribuição e conversões", "Testes A/B, CAC, ROAS e otimização de mídia"]
    if "pesquisa aplicada ao consumidor" in d:
        return ["Problema de decisão, hipótese e desenho da pesquisa", "Entrevistas, grupos focais, questionários e amostragem", "Análise de motivadores, barreiras e comportamento real", "Insights, recomendações e comunicação para stakeholders"]
    if "projeto final de marketing" in d:
        return ["Diagnóstico e problema estratégico", "Plano integrado, orçamento, cronograma e riscos", "Implementação-piloto e monitoramento dos KPIs", "Avaliação final, recomendações e lições aprendidas"]
    if "apuração e reportagem i" in d:
        return ["Pauta, hipótese e plano de apuração jornalística", "Entrevistas iniciais e confirmação documental", "Redação da notícia/reportagem e contextualização", "Checagem básica, edição e direito de resposta"]
    if "apuração e reportagem ii" in d:
        return ["Reportagem aprofundada e investigação de interesse público", "Cruzamento de bases, documentos e fontes diversas", "Estrutura narrativa, evidências e contrapontos", "Revisão factual, riscos jurídicos e edição final"]
    if "jornalismo de dados i" in d:
        return ["Localização e avaliação de bases públicas", "Planilhas, limpeza, padronização e análise exploratória", "Cálculos descritivos e checagem de consistência", "Narrativa inicial e visualização de dados jornalísticos"]
    if "jornalismo de dados ii" in d:
        return ["Coleta automatizada e integração de múltiplas bases", "Estatística aplicada, cruzamentos e análise de tendências", "Visualização avançada e storytelling com dados", "Reprodutibilidade, transparência metodológica e publicação"]

    if "introdução ao curso de engenharia civil" in d:
        return ["Campos de atuação da engenharia civil e responsabilidade técnica", "Leitura de desenhos, normas e documentação de projeto", "Ética, segurança, sustentabilidade e atribuições profissionais", "Visão integrada do ciclo de vida de empreendimentos"]
    if d.endswith("laboratório de materiais de construção i"):
        return ["Amostragem e caracterização de agregados e aglomerantes", "Ensaios de massa específica, granulometria e consistência", "Procedimentos laboratoriais e registro de resultados", "Normas, incerteza de medição e relatório técnico"]
    if d.endswith("laboratório de materiais de construção ii"):
        return ["Dosagem, moldagem e cura de corpos de prova de concreto", "Ensaios de resistência e avaliação de desempenho", "Ensaios de materiais alternativos e durabilidade", "Interpretação de resultados e controle tecnológico da obra"]
    if d.endswith("laboratório de mecânica dos solos i"):
        return ["Coleta, preparação e identificação de amostras", "Análise granulométrica e limites de Atterberg", "Determinação de umidade, massa específica e índices físicos", "Classificação geotécnica a partir de ensaios básicos"]
    if d.endswith("laboratório de mecânica dos solos ii"):
        return ["Ensaios de compactação e determinação de suporte", "Ensaios de adensamento e permeabilidade", "Ensaios de resistência ao cisalhamento", "Interpretação de parâmetros para projeto geotécnico"]
    if "topografia e geodésia" in d:
        return ["Referenciais geodésicos, coordenadas e sistemas de projeção", "Levantamentos planimétricos e altimétricos", "GNSS, estação total e coleta digital de campo", "Cálculo, ajuste e representação cartográfica dos levantamentos"]
    if "estruturas de aço" in d:
        return ["Propriedades do aço estrutural e estados limites", "Dimensionamento de barras tracionadas e comprimidas", "Vigas, ligações parafusadas e soldadas", "Estabilidade global, detalhamento e normas de projeto"]
    if "projeto de estradas" in d:
        return ["Estudos de traçado e classificação funcional da via", "Geometria horizontal, vertical e seção transversal", "Terraplenagem, drenagem e segurança viária", "Compatibilização de projeto, orçamento e impacto ambiental"]
    if "pavimentação" in d:
        return ["Tráfego, subleito e caracterização dos materiais", "Dimensionamento de pavimentos flexíveis e rígidos", "Dosagem, execução e controle de camadas", "Patologias, avaliação funcional e restauração de pavimentos"]
    if "estruturas de madeira" in d:
        return ["Propriedades da madeira e classes de resistência", "Dimensionamento de elementos e ligações", "Durabilidade, umidade, biodeterioração e proteção", "Detalhamento, execução e inspeção de sistemas de madeira"]
    if "segurança do trabalho na construção" in d:
        return ["Identificação de perigos e avaliação de riscos no canteiro", "Normas de segurança, EPC, EPI e permissões de trabalho", "Trabalho em altura, escavações e instalações provisórias", "Investigação de incidentes e planejamento de prevenção"]
    if d.endswith("resistência dos materiais i") and course == "Engenharia Mecânica":
        return ["Equilíbrio de corpos e diagramas de esforços internos", "Tensão normal, cisalhamento e deformação axial", "Torção de eixos e distribuição de tensões", "Dimensionamento básico por critérios de resistência"]
    if d.endswith("resistência dos materiais ii") and course == "Engenharia Mecânica":
        return ["Flexão pura e transversal em vigas", "Estado combinado de tensões e círculo de Mohr", "Deflexão, energia de deformação e métodos de cálculo", "Flambagem, estabilidade e critérios de falha"]

    if "psicologia: ciência e profissão" in d:
        return ["História da psicologia e consolidação como campo científico", "Áreas de atuação, atribuições e contextos profissionais", "Regulamentação, código de ética e responsabilidade técnica", "Relações entre ciência, profissão e demandas sociais"]
    if "investigação e métodos em psicologia" in d or "metodologia de pesquisa em psicologia" in d:
        return ["Problema, hipótese, variáveis e desenho de pesquisa", "Métodos experimentais, correlacionais e qualitativos", "Amostragem, instrumentos, validade e confiabilidade", "Ética, análise de dados e comunicação científica"]
    if d.endswith("psicologia da personalidade i"):
        return ["Modelos psicodinâmicos e conceitos de personalidade", "Abordagens de traços e diferenças individuais", "Métodos de avaliação e limites de inferência", "Contextos culturais e desenvolvimento da personalidade"]
    if d.endswith("psicologia da personalidade ii"):
        return ["Abordagens humanistas, existenciais e cognitivas", "Personalidade, contexto e padrões de adaptação", "Avaliação integrada e formulação de caso", "Evidências, crítica comparativa e aplicações profissionais"]
    if "psicologia organizacional" in d:
        return ["Comportamento individual, grupos e dinâmica organizacional", "Seleção, avaliação, desenvolvimento e saúde ocupacional", "Clima, cultura, liderança e relações de trabalho", "Intervenções organizacionais, indicadores e ética profissional"]
    if "psicologia clínica" in d:
        return ["Entrevista clínica, contrato e formulação inicial de caso", "Modelos de intervenção e planejamento terapêutico", "Aliança, acompanhamento e avaliação de resultados", "Ética, limites profissionais e encaminhamento em rede"]
    if "psicologia da saúde" in d:
        return ["Modelos de saúde, doença e comportamento de autocuidado", "Adesão ao tratamento, estresse e enfrentamento", "Intervenção psicológica em contexto hospitalar e comunitário", "Humanização, equipe interdisciplinar e avaliação de desfechos"]
    if "psicometria" in d:
        return ["Teoria clássica dos testes e modelos de mensuração", "Validade, fidedignidade, normas e padronização", "Construção, aplicação e correção de instrumentos", "Ética, limites interpretativos e elaboração de laudos"]
    if "psicologia comunitária" in d:
        return ["Comunidade, participação, território e redes de apoio", "Diagnóstico participativo e análise de necessidades coletivas", "Intervenção comunitária, autonomia e fortalecimento de vínculos", "Avaliação de projetos e ética na atuação territorial"]
    if "psicologia jurídica" in d:
        return ["Interfaces entre psicologia, sistema de justiça e direitos", "Avaliação psicológica em contextos periciais", "Família, infância, violência e proteção de direitos", "Documentos técnicos, limites periciais e ética profissional"]
    if "psicologia hospitalar" in d:
        return ["Impacto psicológico de hospitalização e doença grave", "Intervenções breves com pacientes e familiares", "Luto, comunicação de más notícias e cuidados paliativos", "Trabalho interdisciplinar e humanização da assistência"]

    if "microbiologia clínica" in d:
        return ["Coleta, transporte e qualidade de amostras clínicas", "Cultivo, identificação e testes de sensibilidade", "Diagnóstico laboratorial de infecções bacterianas e fúngicas", "Interpretação de laudos, resistência e controle de qualidade"]
    if "imunologia clínica" in d:
        return ["Métodos sorológicos e imunodiagnóstico", "Ensaios de antígeno, anticorpo e imunomonitoramento", "Autoanticorpos, alergias e imunodeficiências laboratoriais", "Controle de qualidade, sensibilidade e especificidade dos testes"]
    if "parasitologia clínica" in d:
        return ["Diagnóstico de protozoários e helmintos em amostras clínicas", "Métodos coproparasitológicos e pesquisa de hemoparasitos", "Coleta, conservação e limitações das técnicas laboratoriais", "Interpretação do resultado e correlação clínico-epidemiológica"]

    if "estudo experimental dos alimentos" in d:
        return ["Delineamento de experimentos culinários e padronização", "Transformações físicas e químicas no preparo", "Avaliação sensorial e aceitabilidade de preparações", "Registro, repetibilidade e interpretação dos resultados"]
    if "composição dos alimentos" in d:
        return ["Composição centesimal e tabelas de composição", "Métodos de análise de macronutrientes e micronutrientes", "Biodisponibilidade, fatores antinutricionais e variabilidade", "Interpretação de rótulos e aplicação no planejamento alimentar"]
    if "nutrição e metabolismo" in d:
        return ["Digestão, absorção e transporte de nutrientes", "Metabolismo de carboidratos, lipídios e proteínas", "Regulação hormonal e integração metabólica", "Adaptações metabólicas no jejum, exercício e doença"]
    if "higiene e legislação dos alimentos" in d or "controle higiênico-sanitário" in d:
        return ["Perigos físicos, químicos e biológicos nos alimentos", "Boas práticas, POPs e controle de temperatura", "Legislação sanitária, inspeção e rastreabilidade", "Investigação de surtos, auditoria e ações corretivas"]
    if "nutrição clínica" in d:
        return ["Avaliação nutricional clínica e identificação de risco", "Diagnóstico nutricional e definição de metas", "Plano alimentar individualizado e monitoramento", "Integração com equipe de saúde e avaliação de desfechos"]
    if "tecnologia de alimentos" in d:
        return ["Processos de conservação por calor, frio e redução de água", "Fermentação, embalagem e estabilidade dos alimentos", "Tecnologias emergentes e alterações nutricionais", "Controle de processo, vida de prateleira e segurança"]
    if "nutrição materno-infantil" in d:
        return ["Avaliação nutricional durante gestação e lactação", "Aleitamento materno e alimentação complementar", "Necessidades na prematuridade e primeira infância", "Prevenção de carências e acompanhamento do crescimento"]
    if "nutrição em saúde coletiva" in d:
        return ["Diagnóstico alimentar e nutricional da população", "Políticas públicas e programas de alimentação e nutrição", "Educação alimentar, segurança alimentar e soberania", "Indicadores, vigilância nutricional e avaliação de políticas"]
    if "nutrição esportiva" in d:
        return ["Avaliação e necessidades energéticas do atleta", "Carboidratos, proteínas e hidratação para desempenho", "Estratégias pré, intra e pós-exercício", "Suplementação baseada em evidências e risco de doping"]
    if "nutrição do idoso" in d:
        return ["Alterações fisiológicas e necessidades na velhice", "Rastreio de desnutrição, sarcopenia e fragilidade", "Planejamento alimentar diante de comorbidades e disfagia", "Atenção integral, autonomia e cuidado multiprofissional"]
    if "nutrição hospitalar" in d:
        return ["Triagem e diagnóstico de risco nutricional hospitalar", "Terapia nutricional oral, enteral e parenteral", "Monitoramento de tolerância e metas nutricionais", "Protocolos assistenciais e transição para alta"]
    if "nutrição em doenças crônicas" in d:
        return ["Manejo nutricional de diabetes e doenças cardiovasculares", "Estratégias alimentares para doença renal e hepática", "Obesidade, inflamação e doenças metabólicas", "Mudança de comportamento, adesão e monitoramento clínico"]

    if "materiais e técnicas construtivas" in d or "tecnologia da construção" in d:
        return ["Sistemas construtivos e sequência de execução", "Materiais, desempenho, durabilidade e patologias", "Detalhes executivos, produtividade e controle de qualidade", "Compatibilização, sustentabilidade e manutenção da edificação"]
    if "topografia" in d and course == "Arquitetura e Urbanismo":
        return ["Levantamento planialtimétrico e representação do terreno", "Curvas de nível, cotas, perfis e cálculo de áreas", "Equipamentos, precisão e registro de campo", "Uso do levantamento na implantação de projeto arquitetônico"]
    if "teoria e história do urbanismo" in d:
        return ["Formação histórica das cidades e modelos urbanos", "Urbanismo moderno, planejamento e crítica", "Segregação socioespacial, mobilidade e infraestrutura", "Leitura crítica do espaço urbano e políticas de intervenção"]
    if "teoria e história da arquitetura brasileira" in d:
        return ["Arquitetura colonial e matrizes indígenas, africanas e europeias", "Ecletismo, modernismo e formação da arquitetura brasileira", "Brasília, regionalismos e arquitetura contemporânea", "Patrimônio, memória, identidade e preservação"]
    if "ética e legislação profissional" in d and course == "Arquitetura e Urbanismo":
        return ["Atribuições profissionais, conselho e responsabilidade técnica", "Código de ética, contrato e relação com clientes", "Legislação urbanística, acessibilidade e licenciamento", "Responsabilidade civil, ambiental e segurança do projeto"]

    if d.endswith("contabilidade avançada i"):
        return ["Combinações de negócios e consolidação inicial", "Investimentos em coligadas e controladas", "Método de equivalência patrimonial", "Demonstrações consolidadas e eliminações básicas"]
    if d.endswith("contabilidade avançada ii"):
        return ["Reorganizações societárias e operações entre empresas", "Conversão de demonstrações e efeitos cambiais", "Instrumentos financeiros e mensuração complexa", "Consolidação avançada, divulgação e normas aplicáveis"]
    if "contabilidade tributária" in d:
        return ["Tributos sobre faturamento, renda e patrimônio", "Apuração fiscal e diferenças entre resultado contábil e fiscal", "Planejamento tributário lícito e regimes de tributação", "Obrigações acessórias e controles de conformidade"]
    if "contabilidade societária" in d:
        return ["Constituição, alterações e dissolução de sociedades", "Capital social, reservas e distribuição de resultados", "Reorganizações societárias e demonstrações específicas", "Normas societárias, divulgação e responsabilidade dos administradores"]
    if "contabilidade do agronegócio" in d:
        return ["Reconhecimento de ativos biológicos e produtos agrícolas", "Custos de produção e avaliação de estoques rurais", "Receitas, contratos e particularidades fiscais do setor", "Demonstrações e análise de desempenho agropecuário"]
    if "gestão de riscos" in d:
        return ["Identificação, análise e priorização de riscos", "Controles preventivos, detectivos e plano de resposta", "Matriz de risco, apetite e indicadores-chave", "Monitoramento, comunicação e governança de riscos"]

    if "computação e sociedade" in d:
        return ["História da computação e transformação digital", "Ética, privacidade, segurança e direitos digitais", "Impactos sociais, ambientais e econômicos dos sistemas", "Inclusão digital, acessibilidade e responsabilidade profissional"]
    if "introdução à programação" in d:
        return ["Algoritmos, variáveis, tipos e expressões", "Decisão, repetição e decomposição de problemas", "Funções, modularização e estruturas de dados básicas", "Testes, depuração e documentação de programas"]
    if "programação orientada a objetos" in d:
        return ["Classes, objetos, encapsulamento e composição", "Herança, polimorfismo e interfaces", "Tratamento de erros, coleções e princípios de projeto", "Testes unitários e manutenção de aplicações orientadas a objetos"]
    if "sistemas de informação gerenciais" in d:
        return ["Tipos de sistemas e suporte aos níveis organizacionais", "Indicadores, relatórios e apoio à decisão", "Integração de processos, dados e governança", "Avaliação de benefícios, riscos e implantação de sistemas"]
    if "arquitetura de software" in d:
        return ["Estilos arquiteturais, componentes e atributos de qualidade", "Padrões de projeto e princípios de modularidade", "Integração, observabilidade, escalabilidade e resiliência", "Documentação arquitetural e análise de trade-offs"]
    if "projeto de sistemas de informação" in d:
        return ["Levantamento de requisitos e análise de stakeholders", "Modelagem de processos, dados e casos de uso", "Prototipação, arquitetura e planejamento de entrega", "Validação, implantação e avaliação pós-implantação"]
    if "ética e legislação em computação" in d:
        return ["Privacidade, LGPD e tratamento de dados pessoais", "Direito autoral, licenças de software e propriedade intelectual", "Cibercrime, evidências digitais e responsabilidade", "Ética da IA, acessibilidade e responsabilidade profissional"]

    if "fundamentos históricos da educação" in d or "história da educação brasileira" in d:
        return ["Instituições educacionais e ideias pedagógicas em seu contexto histórico", "Transformações da escola no Brasil e políticas educacionais", "Desigualdades, acesso e disputas pelo direito à educação", "Leitura crítica de fontes e periodização histórica da educação"]
    if "filosofia da educação" in d:
        return ["Concepções de conhecimento, pessoa e sociedade na educação", "Pensadores clássicos e modernos da filosofia educacional", "Ética, democracia, autonomia e finalidade da escola", "Análise crítica de problemas educacionais contemporâneos"]
    if "sociologia da educação" in d:
        return ["Educação, estratificação social e reprodução das desigualdades", "Escola, cultura, capital social e mobilidade", "Estado, políticas públicas e relações de poder", "Sociologia escolar aplicada a situações concretas"]
    if "didática" in d:
        return ["Objetivos de aprendizagem, planejamento e sequenciamento didático", "Métodos de ensino, recursos e mediação pedagógica", "Avaliação formativa, feedback e recuperação", "Reflexão sobre a prática e adaptação ao contexto escolar"]
    if "educação inclusiva" in d or "educação e diversidade" in d:
        return ["Educação especial na perspectiva inclusiva e legislação", "Acessibilidade, desenho universal e adaptações razoáveis", "Diversidade cultural, linguística e combate à discriminação", "Planejamento colaborativo e avaliação de barreiras à aprendizagem"]
    if "currículo e cultura" in d:
        return ["Teorias curriculares e seleção de conhecimentos", "Currículo, identidade, poder e diversidade cultural", "Currículo formal, vivido e oculto", "Análise e construção de propostas curriculares contextualizadas"]
    if "ensino de língua portuguesa" in d:
        return ["Práticas de linguagem, gêneros textuais e leitura", "Alfabetização, produção textual e análise linguística", "Literatura e formação de leitores", "Planejamento didático e avaliação da aprendizagem linguística"]
    if "ensino de ciências da natureza" in d:
        return ["Alfabetização científica e natureza da ciência", "Conceitos de vida, matéria, energia e ambiente", "Investigação, experimentação e argumentação em ciências", "Planejamento e avaliação de sequências investigativas"]
    if "ensino de história e geografia" in d:
        return ["Tempo histórico, fontes, memória e narrativas", "Espaço geográfico, território, paisagem e escala", "Cartografia, relações sociedade-natureza e cidadania", "Planejamento interdisciplinar e avaliação das aprendizagens"]
    if "arte e educação" in d:
        return ["Linguagens artísticas, repertório e fruição estética", "Processos criativos, experimentação e produção", "Arte, cultura, identidade e diversidade", "Mediação cultural e avaliação de práticas artísticas escolares"]

    if "fundamentos de marketing" in d:
        return ["Conceitos centrais de marketing, valor e orientação ao mercado", "Ambiente, segmentação, público-alvo e posicionamento", "Composto de marketing e jornada de compra", "Planejamento de marketing e indicadores introdutórios"]
    if "gestão de marcas" in d:
        return ["Identidade, propósito, posicionamento e arquitetura de marca", "Brand equity, associações e percepção de valor", "Tom de voz, consistência e experiência da marca", "Pesquisa de marca, métricas e gestão de reputação"]
    if "marketing de conteúdo" in d:
        return ["Personas, jornada e estratégia editorial", "Formatos, calendário, distribuição e reaproveitamento", "SEO editorial, narrativa e qualidade informacional", "Métricas de alcance, engajamento e conversão de conteúdo"]
    if "mídias sociais" in d:
        return ["Plataformas, comunidades e objetivos de presença social", "Planejamento de pauta, formatos e moderação", "Gestão de comunidade, crise e reputação", "Métricas, testes e análise do desempenho social"]
    if "publicidade e promoção" in d:
        return ["Objetivos de comunicação e construção de mensagem publicitária", "Mix promocional, mídia, frequência e alcance", "Briefing, criação, produção e aprovação de campanha", "Avaliação de resultados, ética publicitária e regulação"]
    if "marketing de serviços" in d:
        return ["Características dos serviços e gestão da experiência", "Jornada, pontos de contato e qualidade percebida", "Capacidade, demanda, espera e recuperação de serviço", "Fidelização, satisfação e métricas de experiência"]
    if "crm e relacionamento" in d:
        return ["Ciclo de vida do cliente e segmentação relacional", "Dados, consentimento, privacidade e qualidade cadastral", "Automação de relacionamento e jornadas personalizadas", "Retenção, churn, lifetime value e métricas de relacionamento"]
    if "análise de dados de marketing" in d or "marketing analítico" in d:
        return ["Coleta, limpeza e integração de dados de marketing", "Funil, coortes, atribuição e análise de conversão", "Experimentos, testes A/B e inferência aplicada", "Dashboards, interpretação e tomada de decisão baseada em dados"]
    if "planejamento de campanhas" in d:
        return ["Briefing, objetivos SMART e definição de públicos", "Estratégia criativa, canais, orçamento e cronograma", "Plano de mídia, execução e gestão de riscos", "KPIs, avaliação pós-campanha e otimização"]
    if "marketing de produto" in d:
        return ["Pesquisa de necessidade e proposta de valor", "Posicionamento, lançamento e ciclo de vida do produto", "Preço, portfólio e alinhamento com vendas", "Adoção, retenção e métricas de produto"]
    if "marketing b2b" in d:
        return ["Mercados organizacionais e comitês de compra", "Segmentação de contas, ICP e proposta de valor B2B", "Marketing baseado em contas e integração com vendas", "Pipeline, geração de demanda e métricas de receita"]
    if "marketing de performance" in d:
        return ["Objetivos de aquisição e estruturação do funil", "Canais pagos, lances, orçamento e segmentação", "Tracking, conversões e atribuição", "Experimentos, ROAS/CAC e otimização contínua"]
    if "marketing de influência" in d:
        return ["Seleção de criadores e aderência à marca", "Briefing, contratos, transparência e publicidade identificada", "Mensuração de alcance, engajamento e conversão", "Riscos de reputação, direitos de imagem e avaliação de campanhas"]
    if "marketing de varejo" in d:
        return ["Comportamento de compra e jornada no ponto de venda", "Sortimento, exposição, promoção e experiência omnicanal", "Trade marketing, canais e integração com fornecedores", "Vendas, margem, giro e indicadores de varejo"]
    if "marketing internacional" in d:
        return ["Seleção de mercados e análise de ambiente internacional", "Adaptação de produto, preço, comunicação e distribuição", "Culturas, regulações, comércio e riscos cambiais", "Estratégias de entrada e avaliação de resultados internacionais"]
    if d.endswith("plano integrado de marketing i"):
        return ["Diagnóstico de mercado e pesquisa de contexto", "Definição de objetivos, público e posicionamento", "Proposta de valor, estratégia e plano de ação", "Orçamento, cronograma, indicadores e aprovação do plano"]
    if d.endswith("plano integrado de marketing ii"):
        return ["Implementação e acompanhamento do plano aprovado", "Monitoramento de KPIs e gestão de ajustes", "Avaliação de resultados, orçamento e retorno", "Relatório final, recomendações e aprendizagem do projeto"]

    if "introdução ao jornalismo" in d:
        return ["Funções sociais, campos e rotinas do jornalismo", "Notícia, critérios de noticiabilidade e interesse público", "Fontes, apuração, verificação e responsabilidade", "Ética, liberdade de imprensa e direito à informação"]
    if "história do jornalismo" in d:
        return ["Origens da imprensa e transformação dos meios", "Imprensa brasileira, censura e democratização", "Mudanças tecnológicas e modelos de negócio jornalístico", "Historiografia, memória e análise crítica de produtos jornalísticos"]
    if "teorias da comunicação" in d:
        return ["Modelos clássicos de comunicação e transmissão", "Indústria cultural, estudos culturais e recepção", "Comunicação, poder, mediação e esfera pública", "Aplicação crítica de teorias a fenômenos midiáticos atuais"]
    if "fotojornalismo" in d:
        return ["Composição, exposição, foco e narrativa visual", "Apuração visual, legenda, contexto e sequência fotográfica", "Edição, ética, manipulação e direitos de imagem", "Reportagem fotográfica e organização de portfólio"]
    if "jornalismo e sociedade" in d:
        return ["Jornalismo, democracia e esfera pública", "Representação social, pluralidade e grupos sub-representados", "Mídia, poder, economia política e concentração", "Impacto social da informação e responsabilidade editorial"]
    if "comunicação e cultura digital" in d:
        return ["Plataformas digitais, redes e ecossistemas de informação", "Cultura participativa, circulação e algoritmos", "Desinformação, bolhas e verificação de conteúdo", "Métricas, ética e transformação de práticas comunicacionais"]
    if "assessoria de comunicação" in d:
        return ["Diagnóstico de comunicação e relacionamento com stakeholders", "Planejamento de pauta, releases e relacionamento com imprensa", "Comunicação de crise e preparação de porta-vozes", "Mensuração, reputação e avaliação de resultados"]
    if "teorias do jornalismo" in d:
        return ["Teorias da produção da notícia e gatekeeping", "Rotinas de redação, enquadramento e valores-notícia", "Influências econômicas, políticas e tecnológicas", "Pesquisa empírica e crítica das teorias do jornalismo"]
    if "jornalismo investigativo" in d:
        return ["Hipótese investigativa, interesse público e plano de apuração", "Fontes documentais, dados públicos e proteção de fontes", "Verificação cruzada, rastreabilidade e segurança", "Publicação responsável, direito de resposta e avaliação de risco"]
    if "jornalismo digital" in d:
        return ["Narrativa multimídia, hipertexto e atualização contínua", "Distribuição multiplataforma e estratégia de audiência", "SEO jornalístico, acessibilidade e experiência de leitura", "Métricas, fidelização e modelos editoriais digitais"]
    if "podcast e jornalismo sonoro" in d:
        return ["Conceito, formato, roteiro e arco narrativo do podcast", "Entrevista, locução, captação e edição de áudio", "Publicação, distribuição e estratégia de audiência", "Direitos autorais, checagem e métricas de escuta"]

    # Diferencia os ramos biomédicos: não reutilizar um roteiro genérico para
    # microbiologia, imunologia, parasitologia e patologia como se fossem iguais.
    if "imunolog" in d:
        return ["Imunidade inata: barreiras, células e mediadores", "Imunidade adaptativa: linfócitos, anticorpos e memória", "Hipersensibilidades, autoimunidade e imunodeficiências", "Vacinas, imunodiagnóstico e interpretação de respostas imunes"]
    if "microbiolog" in d:
        return ["Estrutura, classificação e crescimento de microrganismos", "Patogenicidade, transmissão e interação microrganismo-hospedeiro", "Coleta, cultivo, identificação e testes de sensibilidade", "Desinfecção, esterilização, prevenção e controle de infecções"]
    if "parasitolog" in d:
        return ["Morfologia e ciclos biológicos dos parasitos de interesse", "Vias de transmissão, hospedeiros e epidemiologia", "Métodos de coleta e diagnóstico parasitológico", "Prevenção, tratamento e controle integrado das parasitoses"]
    if "patologia bucal" in d:
        return ["Lesões inflamatórias e reacionais da mucosa oral", "Cistos, tumores odontogênicos e alterações ósseas maxilares", "Lesões potencialmente malignas e neoplasias da cavidade oral", "Correlação clínico-radiográfica, biópsia e laudo histopatológico"]
    if "patologia clínica veterinária" in d:
        return ["Hematologia veterinária e avaliação de esfregaços", "Bioquímica sérica, urinálise e líquidos cavitários", "Controle pré-analítico, analítico e pós-analítico", "Interpretação laboratorial integrada por espécie e quadro clínico"]
    if "citopatologia" in d:
        return ["Princípios de coleta, fixação e preparação citológica", "Critérios morfológicos de benignidade, atipia e malignidade", "Citologia de líquidos, secreções e punções aspirativas", "Limites diagnósticos, controle de qualidade e correlação histológica"]
    if "patologia" in d:
        return ["Lesão celular, adaptações, morte celular e depósitos", "Inflamação aguda/crônica, reparo e cicatrização", "Distúrbios hemodinâmicos, trombose e choque", "Neoplasia, mecanismos de progressão e correlação morfológica"]
    if "toxicologia analítica" in d:
        return ["Coleta, conservação e cadeia de custódia de amostras", "Preparo de amostras e extração de analitos", "Métodos instrumentais e validação de ensaios toxicológicos", "Interpretação quantitativa, limites e laudo analítico"]
    if "bioética" in d:
        return ["Autonomia, beneficência, não maleficência e justiça", "Consentimento informado, confidencialidade e vulnerabilidade", "Conflitos éticos e deliberação baseada em princípios", "Ética em pesquisa, integridade científica e comitês de ética"]
    if "antropologia" in d:
        return ["Cultura, identidade, parentesco e organização social", "Etnografia, observação participante e entrevista", "Diversidade cultural, poder e desigualdades", "Interpretação antropológica de práticas e instituições no campo profissional"]
    if "sociologia" in d:
        return ["Clássicos sociológicos e conceitos de estrutura e ação social", "Instituições, estratificação, classe e mobilidade", "Trabalho, desigualdades, gênero e relações étnico-raciais", "Aplicação de teorias sociológicas a problemas contemporâneos"]
    if "filosofia" in d:
        return ["Problemas filosóficos centrais e leitura argumentativa", "Autores, escolas e contextos históricos da tradição", "Conhecimento, ética, política e concepções de pessoa", "Construção de argumentos e análise crítica de textos"]
    if "ética profissional" in d or "deontologia" in d:
        return ["Deveres, responsabilidades e limites da atuação profissional", "Códigos de ética, legislação e órgãos reguladores", "Sigilo, conflito de interesses e responsabilidade por decisões", "Análise de casos, denúncia, prevenção de danos e prestação de contas"]

    # Práticas clínicas de enfermagem têm objetivos próprios por campo assistencial.
    if "enfermagem clínica" in d:
        return ["Avaliação clínica do adulto e organização do processo de enfermagem", "Cuidados a pessoas com condições clínicas prevalentes", "Monitoramento de sinais de agravamento e prevenção de complicações", "Educação para autocuidado, alta e continuidade assistencial"]
    if "enfermagem cirúrgica" in d or "centro cirúrgico" in d:
        return ["Avaliação pré-operatória e preparo seguro do paciente", "Asepsia, instrumentação e fluxo do centro cirúrgico", "Assistência intraoperatória e recuperação pós-anestésica", "Prevenção de infecção, checklist e segurança cirúrgica"]
    if "enfermagem psiquiátrica" in d or "saúde mental" in d:
        return ["Acolhimento e avaliação de necessidades em saúde mental", "Comunicação terapêutica e plano de cuidado psicossocial", "Manejo de crise, risco e cuidado em liberdade", "Rede de atenção psicossocial, família e reabilitação"]
    if "cuidado crítico" in d or "terapia intensiva" in d:
        return ["Monitorização hemodinâmica e avaliação sistemática", "Suporte respiratório e cuidados com dispositivos", "Reconhecimento de deterioração e resposta a emergências", "Prevenção de eventos adversos, infecções e lesões relacionadas à imobilidade"]
    if "doenças infecciosas" in d:
        return ["Precauções, isolamento e vigilância de infecções transmissíveis", "Cuidados de enfermagem na antibioticoterapia e coleta de exames", "Reconhecimento de sinais de gravidade e complicações", "Educação, notificação e prevenção de transmissão nos serviços"]

    # Farmácia: separa administração, gestão e tecnologia de medicamentos.
    if "farmacotécnica" in d or "tecnologia farmacêutica" in d:
        return ["Formas farmacêuticas e operações de produção", "Excipientes, estabilidade e incompatibilidades", "Processos, equipamentos e controle em escala", "Boas práticas de fabricação e qualidade do produto"]
    if "farmácia clínica" in d or "farmacoterapia" in d or "semiologia" in d:
        return ["Anamnese farmacêutica e identificação de problemas relacionados a medicamentos", "Revisão de farmacoterapia e avaliação de efetividade/segurança", "Plano de cuidado farmacêutico e monitoramento", "Comunicação interprofissional e documentação do seguimento"]
    if "assistência farmacêutica" in d:
        return ["Seleção, programação, aquisição e armazenamento de medicamentos", "Componente básico, estratégico e especializado no SUS", "Dispensação, uso racional e acompanhamento farmacoterapêutico", "Indicadores, financiamento e avaliação da assistência farmacêutica"]
    if "farmácia hospitalar" in d:
        return ["Seleção e padronização de medicamentos no hospital", "Logística, distribuição e rastreabilidade", "Conciliação medicamentosa e segurança em transições de cuidado", "Farmácia clínica, comissões e gestão de riscos"]

    # Agrárias: roteiros específicos para solo, cultura e sistemas de produção.
    if "fitopatologia" in d:
        return ["Agentes fitopatogênicos, sintomas e sinais de doença", "Ciclo da doença, epidemiologia e condições predisponentes", "Diagnóstico, amostragem e identificação de patógenos", "Manejo integrado, resistência genética e controle sustentável"]
    if "fertilidade do solo" in d:
        return ["Acidez, calagem e necessidade de corretivos", "Disponibilidade, dinâmica e deficiência de nutrientes", "Interpretação de análise de solo e recomendação de adubação", "Eficiência de uso de fertilizantes e balanço de nutrientes"]
    if "irrigação" in d or "drenagem" in d:
        return ["Relações solo-água-planta-atmosfera e demanda hídrica", "Métodos de irrigação e critérios de dimensionamento", "Uniformidade, manejo da lâmina e eficiência de aplicação", "Drenagem agrícola, salinidade e conservação dos recursos hídricos"]
    if "sementes" in d:
        return ["Formação, maturação e fisiologia de sementes", "Pureza, germinação, vigor e armazenamento", "Amostragem, análise e certificação de lotes", "Tratamento, qualidade e estabelecimento de lavouras"]
    if "solos" in d or "solo e água" in d or "ciência do solo" in d:
        return ["Gênese, morfologia e classificação dos solos", "Propriedades físicas e químicas e interpretação de perfis", "Erosão, compactação e indicadores de degradação", "Conservação, cobertura e manejo sustentável do solo e da água"]
    if "fitotecnia" in d or "culturas regionais" in d:
        return ["Fenologia e exigências ambientais da cultura", "Escolha de cultivar, implantação e manejo cultural", "Monitoramento nutricional, fitossanitário e hídrico", "Colheita, qualidade, produtividade e avaliação econômica"]

    # Direito por ramo e por sequência processual; evita que vários componentes
    # jurídicos usem o mesmo roteiro genérico.
    if "processual civil" in d:
        stage = roman or 1
        if stage == 1: return ["Jurisdição, ação, competência e sujeitos do processo", "Pressupostos processuais, petição inicial e resposta", "Providências preliminares, saneamento e organização da prova", "Atos processuais, prazos e decisões interlocutórias"]
        if stage == 2: return ["Teoria geral da prova e audiência de instrução", "Sentença, coisa julgada e remessa necessária", "Liquidação e cumprimento de sentença", "Tutelas provisórias e impugnações cabíveis"]
        return ["Execução de títulos judiciais e extrajudiciais", "Defesas do executado e atos de expropriação", "Recursos, precedentes e técnicas de julgamento", "Procedimentos especiais e solução coletiva de conflitos"]
    if "processual penal" in d:
        stage = roman or 1
        if stage == 1: return ["Investigação preliminar, inquérito e ação penal", "Jurisdição, competência e sujeitos processuais", "Resposta à acusação e medidas cautelares", "Procedimento comum e produção de prova"]
        if stage == 2: return ["Procedimento do júri e crimes de competência especial", "Provas penais, cadeia de custódia e perícias", "Sentença, nulidades e efeitos processuais", "Recursos criminais e impugnações ordinárias"]
        return ["Recursos excepcionais e ações autônomas de impugnação", "Execução penal e incidentes executórios", "Medidas consensuais e justiça penal negociada", "Garantias processuais e jurisprudência avançada"]
    if "direito administrativo" in d:
        return ["Organização administrativa, órgãos, entidades e agentes", "Atos administrativos, poderes e deveres da administração", "Licitações, contratos e serviços públicos" if roman == 1 else "Contratos, licitações e gestão de compras públicas", "Responsabilidade estatal, controle e improbidade" if roman == 1 else "Processo administrativo, controle, sanções e responsabilização"]
    if "direito do trabalho" in d and "processual" not in d:
        if roman == 1: return ["Relação de emprego, sujeitos e requisitos do vínculo", "Jornada, remuneração, férias e outras condições de trabalho", "Alteração, suspensão e extinção do contrato", "Proteção à maternidade, saúde e segurança do trabalhador"]
        return ["Direito coletivo, sindicatos e negociação coletiva", "Greve, representação e conflitos coletivos", "Terceirização, novas formas de trabalho e plataformas", "Responsabilidade trabalhista, jurisprudência e casos complexos"]
    if "direito empresarial" in d:
        if roman == 1: return ["Empresário, estabelecimento e registro empresarial", "Sociedades: constituição, personalidade e tipos", "Capital social, administração e responsabilidade dos sócios", "Escrituração, nome empresarial e propriedade industrial"]
        return ["Reorganização societária e operações empresariais", "Crise da empresa, recuperação e falência", "Títulos de crédito, contratos empresariais e garantias", "Concorrência, insolvência e jurisprudência comercial"]

    # Gestão/negócios: distinguir conteúdos por área de aplicação.
    if "gestão de pessoas" in d or "recursos humanos" in d:
        return ["Recrutamento, seleção e integração de pessoas", "Treinamento, competências e avaliação de desempenho", "Remuneração, clima, liderança e relações de trabalho", "Diversidade, saúde ocupacional e indicadores de pessoas"]
    if "administração financeira" in d or "finanças corporativas" in d or "gestão financeira" in d:
        return ["Valor do dinheiro no tempo e custo de capital", "Orçamento de caixa, capital de giro e liquidez", "Investimento, risco, retorno e estrutura de capital", "Avaliação financeira e decisões de financiamento"]
    if "gestão de operações" in d or "administração da produção" in d or "gestão da qualidade" in d:
        return ["Processos, capacidade, arranjo físico e produtividade", "Planejamento e controle da produção e estoques", "Qualidade, melhoria contínua e análise de causas", "Indicadores operacionais, cadeia de suprimentos e desempenho"]
    if "administração estratégica" in d or "marketing estratégico" in d:
        return ["Diagnóstico ambiental e análise competitiva", "Recursos, capacidades, objetivos e posicionamento", "Formulação, execução e alinhamento estratégico", "Indicadores, controle e adaptação da estratégia"]
    if "contabilidade pública" in d:
        return ["Orçamento público e ciclo orçamentário", "Receita, despesa e estágios da execução", "Patrimônio público e demonstrações contábeis", "Sistemas de informação, controle e prestação de contas"]
    if "pesquisa de mercado" in d:
        return ["Definição do problema, objetivos e fontes de dados", "Desenho amostral, questionários e coleta", "Análise de dados e interpretação de segmentos", "Relatório de insights e recomendação estratégica"]

    # Tecnologia da informação: evita tratar disciplinas com focos diferentes como
    # a mesma lista de 'modelos, implementação, testes e projeto'.
    if "engenharia de software" in d:
        if roman == 1: return ["Processos de software, requisitos e casos de uso", "Modelagem UML e desenho arquitetural inicial", "Testes, versionamento e qualidade de software", "Planejamento de projeto e documentação técnica"]
        return ["Arquitetura, padrões de projeto e refatoração", "Integração contínua, entrega e automação de testes", "Manutenção, métricas e evolução de sistemas", "Confiabilidade, segurança e avaliação de qualidade"]
    if "sistemas operacionais" in d:
        return ["Processos, threads, escalonamento e sincronização", "Gerenciamento de memória e memória virtual", "Sistemas de arquivos, dispositivos e entrada/saída", "Proteção, concorrência e monitoramento do sistema"]
    if "inteligência artificial" in d or "machine learning" in d:
        return ["Representação de problemas, busca e tomada de decisão", "Aprendizado supervisionado, não supervisionado e avaliação", "Preparação de dados, métricas e validação de modelos", "Viés, explicabilidade, privacidade e implantação responsável"]
    if "gestão de projetos" in d:
        return ["Escopo, requisitos, cronograma e estimativas", "Custos, riscos, qualidade e comunicação", "Execução, acompanhamento, mudanças e stakeholders", "Encerramento, avaliação de resultados e lições aprendidas"]

    # Comunicação: produção de conteúdo, estratégia e análise são trilhas distintas.
    if "jornalismo de dados" in d:
        return ["Perguntas jornalísticas e identificação de bases públicas", "Limpeza, organização e análise exploratória de dados", "Visualização, infografia e comunicação de achados", "Reprodutibilidade, checagem e limites de interpretação"]
    if "apuração e reportagem" in d:
        return ["Definição de pauta, hipótese e plano de apuração", "Entrevista, documentação e cruzamento de fontes", "Narrativa, contexto, contraponto e diversidade de vozes", "Verificação factual, edição e avaliação de riscos legais/éticos"]
    if "marketing digital" in d or "seo" in d or "mídia paga" in d or "publicidade digital" in d:
        return ["Intenção de busca, jornada e planejamento de canais", "SEO técnico/editorial ou configuração de campanhas pagas", "Segmentação, criativos, orçamento e testes A/B", "Conversão, atribuição, métricas e otimização de resultados"]
    if "comportamento do consumidor" in d:
        return ["Processos de decisão, motivação e percepção", "Influências culturais, sociais e situacionais", "Jornada, hábitos, lealdade e experiência do consumidor", "Pesquisa de comportamento e implicações para estratégia de marca"]

    # Health / life sciences
    if any(k in d for k in ["anatomia", "histologia", "embriologia", "fisiologia", "bioquímica", "genética", "biologia celular"]):
        if "cabeça" in d or "dental" in d: return ["Estruturas anatômicas e relações topográficas", "Desenvolvimento e diferenciação dos tecidos", "Função e correlação estrutura-função", "Aplicações clínicas da área"]
        if "fisiologia" in d: return ["Mecanismos de regulação fisiológica", "Função integrada dos sistemas", "Homeostase e respostas adaptativas", "Alterações funcionais e interpretação de dados"]
        if "genética" in d: return ["Estrutura e expressão do material genético", "Padrões de herança e variação", "Mutação, regulação e genética molecular", "Aplicações clínicas, populacionais ou produtivas da genética"]
        if "bioquímica" in d: return ["Estrutura e função de biomoléculas", "Enzimas e vias metabólicas", "Metabolismo energético e regulação", "Interpretação de alterações bioquímicas relacionadas à disciplina"]
        if "histologia" in d or "embriologia" in d: return ["Organização microscópica de células e tecidos", "Desenvolvimento embrionário e diferenciação", "Relação entre estrutura e função tecidual", "Reconhecimento microscópico e correlações aplicadas"]
        return ["Organização estrutural e terminologia específica", "Principais sistemas, tecidos ou processos da disciplina", "Relações estrutura-função", "Aplicações clínicas, laboratoriais ou produtivas"]
    if any(k in d for k in ["microbiologia", "imunologia", "parasitologia", "patologia", "doenças infecciosas"]):
        return ["Agentes, mecanismos e classificação relacionados à disciplina", "Transmissão, resposta do hospedeiro e fatores de risco", "Métodos de identificação, diagnóstico e interpretação", "Prevenção, controle e aplicação profissional"]
    if any(k in d for k in ["farmacologia", "farmacocinética", "farmacodinâmica", "farmacoterapia", "toxicologia"]):
        return ["Mecanismos de ação e relação dose-resposta", "Absorção, distribuição, metabolismo e excreção", "Indicações, contraindicações, interações e reações adversas", "Uso seguro, monitoramento e análise de casos"]
    if any(k in d for k in ["nutrição", "dietoterapia", "alimentos", "dietética", "alimentação"]):
        return ["Necessidades nutricionais e avaliação do estado nutricional", "Composição, preparo, segurança e qualidade dos alimentos", "Planejamento alimentar conforme ciclo de vida e contexto clínico", "Intervenção nutricional, monitoramento e educação alimentar"]
    if any(k in d for k in ["enfermagem", "cuidar", "estágio supervisionado em enfermagem"]):
        return ["Processo de enfermagem e avaliação das necessidades", "Planejamento e execução de cuidados baseados em evidências", "Segurança do paciente, registros e administração de terapias", "Educação em saúde, ética e avaliação de resultados"]
    if any(k in d for k in ["fisioterapia", "cinesiologia", "biomecânica", "cinesioterapia", "reabilitação", "terapia manual", "eletrotermofoto"]):
        return ["Avaliação funcional e identificação de limitações", "Fundamentos biomecânicos e fisiológicos da intervenção", "Seleção e aplicação de recursos terapêuticos", "Mensuração de resultados, progressão e segurança"]
    # Law
    if any(k in d for k in ["direito", "processo", "criminologia", "hermenêutica", "teoria do direito", "estágio supervisionado"]):
        if "penal" in d or "criminologia" in d: return ["Princípios, fontes e estrutura normativa da matéria", "Institutos jurídicos e elementos constitutivos", "Procedimentos, garantias e interpretação de casos", "Jurisprudência, aplicação prática e análise crítica"]
        if "civil" in d or "família" in d or "sucessões" in d or "obrigações" in d or "contratos" in d: return ["Institutos e conceitos centrais da matéria", "Requisitos, efeitos e formas de extinção das relações jurídicas", "Responsabilidade, proteção de direitos e solução de conflitos", "Estudo de casos e aplicação do Código Civil"]
        if "constitucional" in d or "constituição" in d or "direitos humanos" in d: return ["Princípios constitucionais e organização do Estado", "Direitos fundamentais, proteção e limites", "Controle de constitucionalidade e remédios jurídicos", "Aplicação jurisprudencial e análise de casos"]
        return ["Conceitos, princípios e fontes normativas da área", "Institutos jurídicos e requisitos de aplicação", "Procedimentos, competências e garantias processuais", "Análise de casos, legislação e jurisprudência"]
    # Engineering, math, physics and computing
    if any(k in d for k in ["cálculo", "álgebra", "geometria", "equações diferenciais", "matemática", "estatística", "probabilidade"]):
        return ["Definições, propriedades e notação fundamentais", "Métodos de cálculo, demonstração ou modelagem", "Interpretação gráfica e análise de resultados", f"Aplicações de {discipline} em problemas de {course}"]
    if any(k in d for k in ["física", "mecânica geral", "termodinâmica", "fluidos", "hidráulica", "hidrologia", "eletromagnetismo", "circuitos", "eletrônica", "máquinas elétricas", "transferência de calor"]):
        return ["Modelos físicos e grandezas fundamentais", "Leis de conservação, equações e condições de contorno", "Resolução de problemas e interpretação de medições", f"Aplicações de {discipline} em sistemas de {course}"]
    if any(k in d for k in ["programação", "algoritmos", "computação", "software", "banco de dados", "sistemas operacionais", "redes", "inteligência artificial", "sistemas de informação", "circuitos digitais", "lógica matemática", "compiladores", "machine learning"]):
        return ["Modelos, arquitetura e conceitos fundamentais da disciplina", "Construção, implementação ou análise de soluções", "Testes, depuração, desempenho e segurança", "Projeto aplicado e avaliação de qualidade da solução"]
    if any(k in d for k in ["estruturas", "construção", "materiais", "solos", "fundação", "topografia", "estradas", "pavimentação", "engenharia civil"]):
        return ["Propriedades dos materiais e parâmetros de projeto", "Métodos de cálculo, dimensionamento e representação técnica", "Normas técnicas, segurança e controle de qualidade", "Aplicação em projeto, execução, inspeção ou manutenção"]
    if any(k in d for k in ["agronomia", "solo", "fitotecnia", "culturas", "irrigação", "plantas", "entomologia", "fitopatologia", "sementes", "forragicultura", "zootecnia", "agroecologia"]):
        return ["Bases biológicas, ambientais e agronômicas do tema", "Manejo, monitoramento e tomada de decisão técnica", "Produtividade, sustentabilidade e prevenção de riscos", "Aplicação em sistemas de produção e análise de resultados"]
    # Education / psychology / communication
    if any(k in d for k in ["pedagogia", "educação", "didática", "alfabetização", "currículo", "aprendizagem", "ensino", "escola"]):
        return ["Fundamentos teóricos e históricos da área", "Planejamento pedagógico e estratégias de intervenção", "Diversidade, inclusão e avaliação da aprendizagem", "Práticas educativas e análise reflexiva de situações reais"]
    if any(k in d for k in ["psicologia", "psicopatologia", "psicoterapia", "psicometria", "processos psicológicos", "personalidade"]):
        return ["Modelos teóricos e conceitos centrais", "Métodos de avaliação e análise do comportamento", "Contextos de desenvolvimento, saúde e relações sociais", "Aplicações profissionais, ética e análise de casos"]
    if any(k in d for k in ["jornalismo", "comunicação", "reportagem", "radiojornalismo", "telejornalismo", "fotojornalismo", "marketing", "marca", "publicidade", "consumidor", "mídias", "campanha", "conteúdo", "seo", "crm", "vendas"]):
        return ["Públicos, objetivos e fundamentos estratégicos da área", "Métodos de planejamento, produção e execução", "Métricas, análise de resultados e otimização", "Ética, direitos, acessibilidade e aplicação em projeto"]
    if any(k in d for k in ["contabilidade", "auditoria", "finanças", "economia", "administração", "gestão", "organizações", "empreendedorismo", "projetos", "logística", "custos"]):
        return ["Conceitos, modelos e terminologia da área", "Métodos de análise, planejamento e decisão", "Indicadores, controles e interpretação de resultados", "Aplicação prática por estudos de caso e solução de problemas"]
    if any(k in d for k in ["história", "filosofia", "sociologia", "antropologia", "humanidades", "cidadania", "gênero", "ética"]):
        return ["Conceitos e correntes teóricas fundamentais", "Contexto histórico e autores de referência", "Debates contemporâneos e perspectivas críticas", "Aplicação conceitual na área profissional do curso"]
    if "estágio" in d:
        return ["Plano de atividades e objetivos de aprendizagem", "Procedimentos profissionais e protocolos do campo", "Ética, segurança e registro reflexivo", "Avaliação de competências e resultados da prática"]
    if "trabalho de conclusão" in d or "pesquisa" in d or "metodologia científica" in d:
        return ["Pergunta de pesquisa, objetivos e revisão de literatura", "Desenho metodológico, ética e coleta de dados", "Análise e discussão de resultados", "Redação acadêmica, referências e apresentação"]
    return [f"Conceitos e fundamentos de {discipline}", f"Métodos, ferramentas e procedimentos próprios de {discipline}", f"Aplicações de {discipline} no campo de {course}", f"Estudos de caso e resolução de problemas de {discipline}"]


def normalize_topic(value: str) -> str:
    import re
    import unicodedata
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().casefold()
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", value).split())


def make_topic_titles_unique(period_topics: dict[int, dict[str, list[str]]]) -> dict[int, dict[str, list[str]]]:
    """Disambiguate duplicated topic titles across one course without deleting them."""
    result: dict[int, dict[str, list[str]]] = {}
    seen: set[str] = set()
    for period in sorted(period_topics):
        result[period] = {}
        for discipline, topics in period_topics[period].items():
            unique: list[str] = []
            local: set[str] = set()
            for topic in topics:
                title = topic.strip()
                norm = normalize_topic(title)
                if norm in seen or norm in local:
                    title = f"{discipline}: {title}"
                    norm = normalize_topic(title)
                if norm in seen or norm in local:
                    title = f"{discipline} (período {period}): {topic.strip()}"
                    norm = normalize_topic(title)
                suffix = 2
                while norm in seen or norm in local:
                    title = f"{discipline} (parte {suffix}): {topic.strip()}"
                    norm = normalize_topic(title)
                    suffix += 1
                unique.append(title)
                local.add(norm)
                seen.add(norm)
            result[period][discipline] = unique
    return result
