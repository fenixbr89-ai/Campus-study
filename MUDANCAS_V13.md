# Campus Study V13 — catálogo e administração de conteúdo

## Corrigido
- Frontend Vercel agora encaminha `/api/*` para o backend do Render usando `vercel.json`.
- Isso corrige o catálogo quando o frontend está no Vercel e o backend no Render e preserva a sessão por cookie via mesma origem.
- Mantida a criação automática dos 23 cursos no backend quando o banco possui menos de 23.
- Removida a IA do código do projeto e da navegação.
- Removido o crédito pessoal do rodapé.

## Administração
O administrador pode criar e editar:
- cursos;
- períodos;
- disciplinas;
- assuntos.

Na área de conteúdos, o administrador pode cadastrar manualmente materiais vinculados ao assunto, escolhendo Curso → Período → Disciplina → Assunto.

Tipos disponíveis:
- Videoaula;
- PDF;
- Livro;
- Artigo científico;
- Resumo;
- Questão;
- Flashcard;
- Mapa mental;
- Material.

PDFs e livros são cadastrados por referência/link nesta versão. O armazenamento físico de arquivos exige um serviço de arquivos persistente (Render Disk, S3, Cloudinary etc.) e não foi ativado para não introduzir armazenamento efêmero no Render.
