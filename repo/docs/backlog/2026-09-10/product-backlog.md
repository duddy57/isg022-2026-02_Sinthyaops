# Product Backlog — CRM agentic-first

- **Data:** 10/09/2026
- **Status:** Rascunho priorizado para descoberta e execução

## Visão e escopo do produto

Construir um CRM que permita gerir clientes e engajar agentes de engenharia de software por integrações como OpenCode, Codex e Claude Code. A direção é agentic-first: o agente ajuda a transformar contexto do cliente em trabalho executável, mas o produto não presume paridade de funcionalidades com outras soluções de CRM/Comp AI.

**Papéis principais:** administrador (organização, usuários e políticas); gestor comercial (carteira, pipeline e relatórios); operador/engenheiro (atividades, tarefas e resultados técnicos); auditor (consulta de histórico e evidências).

**Estado conhecido:** já existe gerenciamento de usuários em FastAPI com JWT. CRM e integrações ainda são planejados; portanto, os itens abaixo não pressupõem modelos, endpoints ou conectores existentes.

## Princípios orientadores

1. **Aprovação humana:** ações externas, alterações relevantes e execução de comandos exigem aprovação explícita, salvo política documentada.
2. **Rastreabilidade:** registrar quem solicitou, qual agente executou, entradas, decisões, saídas, aprovações e falhas.
3. **Segurança e isolamento:** separar organizações, limitar escopos e segredos, aplicar menor privilégio e não expor dados de um cliente a outro.
4. **Entrega incremental:** começar com fluxos confiáveis e observáveis, não com autonomia ampla.

## Fronteira do MVP

O MVP cobre uma organização autenticada com usuários e papéis, contatos/empresas, deals e atividades básicos; criação de uma tarefa agentic a partir de um registro CRM; revisão/aprovação antes da execução; um contrato de conector implementado inicialmente para um provedor; armazenamento de execução, artefatos e auditoria; logs e métricas essenciais. Ficam fora do MVP automações autônomas de produção, múltiplos provedores completos, cobrança, mobile e migração avançada.

## Backlog priorizado

| ID | Épico | História de usuário | Prioridade | Critérios de aceitação | Dependências |
|---|---|---|---|---|---|
| PLAT-01 | Plataforma e autenticação | Como administrador, quero usar a base existente de usuários FastAPI/JWT para acessar uma organização. | P0 | Login/refresh/revogação funcionam; cada requisição identifica usuário e organização; testes cobrem token inválido/expirado. | Usuários FastAPI + JWT existentes |
| PLAT-02 | Plataforma e autenticação | Como administrador, quero convidar usuários e atribuir papéis. | P0 | Convite, ativação e alteração de papel são auditáveis; usuário desativado não acessa a API. | PLAT-01 |
| CRM-01 | CRM core | Como operador, quero cadastrar e buscar contatos e empresas. | P0 | CRUD validado, busca por nome/e-mail, vínculo contato-empresa e isolamento por organização. | PLAT-01 |
| CRM-02 | CRM core | Como gestor, quero acompanhar deals em um pipeline. | P0 | Deal tem etapa, valor, responsável, contato/empresa e histórico de mudanças; transições inválidas são rejeitadas. | CRM-01, PLAT-02 |
| CRM-03 | CRM core | Como usuário, quero registrar atividades e próximos passos. | P0 | Nota, tarefa e interação têm autor, data, vínculo CRM e status; consultas mostram a linha do tempo. | CRM-01, CRM-02 |
| AGT-01 | Workspace de agentes | Como operador, quero criar uma solicitação agentic com contexto CRM selecionado. | P0 | Tarefa mostra objetivo, contexto, escopo e estado; nenhum dado fora da organização é incluído. | CRM-01, CRM-03, PLAT-02 |
| AGT-02 | Fluxo de tarefa agentic | Como operador, quero revisar e aprovar um plano antes da execução. | P0 | Estados `rascunho`, `aguardando_aprovação`, `executando`, `concluída` e `falhou`; aprovação/rejeição registram usuário e motivo. | AGT-01, SEC-01 |
| CON-01 | Abstração de conectores | Como administrador, quero configurar um conector de agente por contrato comum. | P0 | Interface define capacidades, entrada, cancelamento, timeout e erro; segredo fica protegido e não aparece em logs. | PLAT-01, SEC-02 |
| RUN-01 | Execuções, artefatos e auditoria | Como usuário, quero consultar uma execução e seus artefatos. | P0 | Run tem timestamps, status, provedor, correlação e saída; artefatos têm tipo, tamanho, acesso controlado e retenção definida. | AGT-02, CON-01 |
| SEC-01 | Permissões e segurança | Como administrador, quero restringir ações e dados por papel e organização. | P0 | Matriz de autorização cobre CRM, tarefas, conectores e artefatos; testes negativos impedem acesso cruzado. | PLAT-02 |
| SEC-02 | Permissões e segurança | Como administrador, quero armazenar credenciais de conectores com menor privilégio. | P0 | Segredos são cifrados/mascarados, escopos são configuráveis, rotação e revogação são possíveis. | PLAT-01 |
| OBS-01 | Observabilidade | Como operador, quero diagnosticar tarefas sem acessar segredos. | P0 | Logs estruturados têm correlação e níveis; erros e duração de runs são métricas; health check cobre dependências. | RUN-01, SEC-02 |
| CON-02 | Abstração de conectores | Como administrador, quero conectar OpenCode, Codex ou Claude Code conforme sua disponibilidade. | P1 | Pelo menos um conector é entregue; os demais seguem o mesmo contrato, com capability matrix e erro explícito quando indisponíveis. | CON-01, SEC-02 |
| AGT-03 | Fluxo de tarefa agentic | Como operador, quero retomar, cancelar ou pedir nova execução com contexto controlado. | P1 | Cancelamento é idempotente; retry tem limite/backoff; nova execução referencia a anterior e exige aprovação quando necessário. | RUN-01, OBS-01 |
| RUN-02 | Execuções, artefatos e auditoria | Como auditor, quero exportar o histórico de uma tarefa. | P1 | Exportação inclui eventos, aprovações, versões e artefatos permitidos, sem credenciais; acesso é registrado. | RUN-01, SEC-01 |
| REP-01 | Relatórios | Como gestor, quero ver pipeline, atividades e resultados agentic básicos. | P1 | Filtros por período, responsável e etapa; totais são consistentes com CRM; permissões são aplicadas. | CRM-02, CRM-03, RUN-01 |
| OBS-02 | Observabilidade | Como administrador, quero acompanhar saúde e custo operacional dos conectores. | P2 | Painel/API mostra taxa de erro, latência, volume e consumo estimado por organização/provedor. | CON-02, OBS-01 |
| REP-02 | Relatórios | Como gestor, quero comparar conversão e tempo de ciclo. | P2 | Relatório define fórmulas, período e fonte; resultados podem ser exportados conforme permissão. | REP-01, CRM-02 |

## Itens prioritários

Os itens P0 devem ser entregues nesta ordem de dependência e valor:

1. **PLAT-01 — Identidade e sessão:** habilitar acesso confiável usando o gerenciamento FastAPI/JWT existente.
2. **PLAT-02 — Usuários e papéis:** permitir colaboração controlada dentro de uma organização.
3. **SEC-01 — Autorização e isolamento:** garantir que cada papel só opere os recursos permitidos.
4. **SEC-02 — Segredos de conectores:** preparar credenciais protegidas e revogáveis para integrações.
5. **CRM-01 — Contatos e empresas:** estabelecer a base de dados de clientes pesquisável e isolada.
6. **CRM-02 — Deals:** tornar visível e atualizável o pipeline comercial.
7. **CRM-03 — Atividades:** formar uma linha do tempo operacional com próximos passos.
8. **AGT-01 — Solicitação agentic:** transformar contexto CRM selecionado em uma tarefa clara para um agente.
9. **AGT-02 — Aprovação:** impedir execução agentic não autorizada e registrar a decisão humana.
10. **CON-01 — Contrato de conector:** permitir provedores intercambiáveis com capacidades e falhas previsíveis.
11. **RUN-01 — Runs e artefatos:** tornar cada execução consultável, controlada e acompanhada de evidências.
12. **OBS-01 — Observabilidade:** permitir diagnosticar o fluxo sem expor dados sensíveis.
f
## Critérios de aceite dos itens prioritários

Os critérios abaixo são verificáveis por testes automatizados e cenários de API/UI equivalentes:

- **PLAT-01:** um usuário válido consegue fazer login e renovar a sessão; logout/revogação torna o token inutilizável; tokens inválidos ou expirados recebem `401`; toda requisição autenticada carrega `user_id` e `organization_id` no contexto.
- **PLAT-02:** um administrador consegue convidar, ativar, desativar e alterar o papel de um usuário; convite expirado não ativa acesso; usuário desativado recebe `403`/`401`; cada mudança registra ator, alvo e horário.
- **SEC-01:** cada endpoint valida papel e organização antes de ler ou alterar dados; uma tentativa de acesso cruzado retorna `403` ou `404` sem revelar o recurso; a matriz cobre CRM, tarefas, conectores e artefatos; alterações de permissão são auditadas.
- **SEC-02:** um segredo salvo nunca é retornado em texto claro nem aparece em logs/respostas de erro; somente o conector autorizado pode consumi-lo; rotação substitui o valor anterior e revogação impede novos usos; escopos ficam associados à organização e ao conector.
- **CRM-01:** é possível criar, consultar, atualizar e arquivar contato e empresa com campos obrigatórios validados; e-mail e nome são pesquisáveis; um contato pode ser vinculado a uma empresa; consultas de outra organização não retornam registros.
- **CRM-02:** um deal exige etapa, valor, responsável e vínculo com contato ou empresa; somente etapas configuradas são aceitas; mudança de etapa grava estado anterior, novo estado, ator e horário; listagem e detalhe respeitam autorização e organização.
- **CRM-03:** usuário autorizado consegue criar nota, tarefa e interação com autor, data, vínculo e status; status inválido é rejeitado; a linha do tempo ordena eventos e mostra o próximo passo; edição e conclusão mantêm o histórico essencial.
- **AGT-01:** uma solicitação exige objetivo e permite selecionar registros CRM; o resumo exibe objetivo, escopo, contexto e estado; a carga enviada ao agente contém apenas registros autorizados e um teste com registro de outra organização falha; a criação gera identificador único.
- **AGT-02:** nova tarefa inicia em `rascunho` ou `aguardando_aprovação` e não executa antes da aprovação; aprovação e rejeição exigem usuário autorizado e registram decisão, horário e motivo quando aplicável; transições fora de `rascunho` → `aguardando_aprovação` → `executando` → `concluída`/`falhou` são rejeitadas; ações externas permanecem bloqueadas sem aprovação.
- **CON-01:** o contrato comum define capacidades, formato de entrada/saída, timeout, cancelamento e erros normalizados; um conector fake passa no contrato e permite testes sem provedor externo; falha, timeout e capacidade ausente produzem estado e mensagem previsíveis; configuração referencia segredo protegido e não o expõe.
- **RUN-01:** cada execução registra identificador, solicitação, provedor, início, fim, status e correlação; sucesso, falha e timeout ficam distinguíveis e consultáveis; artefatos registram tipo, tamanho, proprietário, retenção e vínculo com a run; somente usuários autorizados baixam artefatos e o download é auditado.
- **OBS-01:** logs estruturados incluem correlação da solicitação e run, status e duração sem tokens, prompts sensíveis ou segredos; métricas contabilizam sucesso, falha, timeout e duração; health check sinaliza dependência indisponível; uma falha de conector permite localizar a run sem expor credenciais.

## Fatias de entrega ordenadas

1. **Fundação segura:** PLAT-01, PLAT-02, SEC-01 e SEC-02.
2. **CRM utilizável:** CRM-01, CRM-02 e CRM-03, com linha do tempo mínima.
3. **Primeiro fluxo agentic:** AGT-01, AGT-02, CON-01 e um conector selecionado em CON-02.
4. **Evidência operacional:** RUN-01, OBS-01, AGT-03 e RUN-02.
5. **Gestão:** REP-01; depois OBS-02 e REP-02 conforme uso real.

## Adiado ou fora de escopo

- Execução sem aprovação, comandos destrutivos irreversíveis e publicação automática em produção.
- Paridade funcional com qualquer CRM ou produto de Comp AI; marketplace de agentes e treinamento de modelos próprios.
- Suporte completo a todos os provedores, omnichannel, e-mail marketing, cobrança, forecasting avançado e aplicativo móvel.
- SSO/SCIM, multi-região, residência regulatória e migrações complexas até haver requisitos de clientes.

## Questões abertas e riscos

- Qual conector será o primeiro e quais ambientes/credenciais são suportados?
- Quais ações exigem aprovação por padrão (código, tickets, mensagens, alterações CRM) e quem pode aprovar?
- Como classificar, reter e apagar artefatos e dados pessoais conforme LGPD?
- Limites de contexto, custo, timeout e concorrência por organização ainda precisam de orçamento.
- Riscos: APIs/provedores instáveis, vazamento por contexto excessivo, alucinações, execução insegura e custo imprevisível; mitigar com isolamento, allowlists, revisão humana, limites e auditoria.
