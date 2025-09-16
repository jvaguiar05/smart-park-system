# AGENT.md – Guia de Implementação das Interfaces Django

> **Objetivo**  
> Organizar e detalhar as tarefas necessárias (sem trechos de código) para entregar:
>
> 1. Redirecionamento `/ → /home`
> 2. **Home** moderna (landing simples)
> 3. **Admin Backoffice** (Django Admin) sob prefixo próprio e com acesso apenas a superadmins
> 4. **Client Backoffice** dedicado a `client_members`
> 5. **Dashboards** com comportamento e dados **baseados em permissão/escopo** (admin vs cliente)

---

## 1) Planejamento de Rotas e Navegação

- Definir o **mapa de URLs**:
  - `/` → redireciona para `/home`
  - `/home` → landing com links para Admin Backoffice e Client Backoffice
  - `/admin_backoffice/` → Django Admin em um site custom (apenas superusers)
  - `/client_backoffice/` → painel para `client_members`
  - `/dashboards/` → rota que entrega dashboards diferentes conforme permissões do usuário
- Definir fluxo de autenticação:
  - Admin usa tela de login do Admin
  - Client Backoffice usa tela de login comum (pode ser personalizada)
- Definir comportamento de logout → redirecionar para `/home`

---

## 2) Estrutura de Pastas de Templates

- Consolidar estrutura dentro de `backend/templates/`:
  - `base.html` (layout base)
  - `home.html` (landing)
  - `backoffice/admin/` (customizações do Django Admin)
  - `backoffice/client/` (páginas do Client Backoffice)
  - `dashboards/admin.html` e `dashboards/client.html`

---

## 3) Admin Backoffice (superusers)

- Criar um `AdminSite` custom para mudar:
  - Prefixo de URL (`/admin_backoffice/`)
  - Cabeçalhos e títulos
  - Permissão: apenas usuários `is_superuser`
- Registrar os models no novo `AdminSite`
- Remover dependência do `/admin/` default, usar apenas `/admin_backoffice/`

---

## 4) Client Backoffice (client_members)

- Criar app `client_backoffice`
- Criar views protegidas:
  - Exigem login
  - Exigem associação em `client_members`
- Definir escopo de dados:
  - Filtrar dados por `client_id` vinculado ao usuário
- Criar templates dedicados (`backoffice/client/`)

---

## 5) Dashboards com Controle de Permissões

- Rota única `/dashboards/`
- View deve:
  - Verificar autenticação
  - Se `superuser` → renderizar `dashboards/admin.html`
  - Se `client_member` → renderizar `dashboards/client.html`
  - (opcional) Se `app_user` → negar ou renderizar versão reduzida
- Endpoints de dados (DRF) devem respeitar escopo:
  - Admin → visão global
  - Client Member → filtrado por `client_id`

---

## 6) Segurança e Controle de Acesso

- Utilizar **mixins** ou decorators para restringir acesso:
  - `LoginRequired`
  - `is_superuser`
  - `is_client_member`
- Criar helpers de autorização que consultam tabelas `roles` e `client_members`
- Garantir escopo multi-tenant: toda query do Client Backoffice e dashboards de cliente devem filtrar por `client_id`

---

## 7) Experiência de Usuário (UX/UI)

- **Home**: página simples, moderna e elegante com botões de entrada
- **Admin Backoffice**: usar visual padrão do Django Admin com pequenas customizações
- **Client Backoffice**: layout próprio, leve e intuitivo para funcionários
- **Dashboards**: usar gráficos e cards dinâmicos; mesma rota `/dashboards/`, conteúdo adaptado ao usuário

---

## 8) Checklist de Entrega

- [ ] `/` redireciona para `/home`
- [ ] `/home` apresenta landing moderna
- [ ] `/admin_backoffice/` funcional apenas para superusers
- [ ] `/client_backoffice/` funcional apenas para client_members
- [ ] `/dashboards/` entrega versão admin ou cliente conforme permissão
- [ ] Templates organizados por contexto (base, home, backoffice, dashboards)
- [ ] Escopo multi-tenant garantido nas queries
- [ ] Testes manuais de login/logout, permissões e navegação concluídos

---

> **Resumo**: Este guia assegura que as interfaces Django sejam expandidas de forma organizada, separando claramente as áreas de **administração global** (superuser), **gestão do cliente** (client_members) e **dashboards** específicos.  
> O Django Admin continua sendo utilizado, mas isolado em `/admin_backoffice/`, enquanto novas páginas permitem atender às necessidades do MVP sem confundir papéis e fluxos.
