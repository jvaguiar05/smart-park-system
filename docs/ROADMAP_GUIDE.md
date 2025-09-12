# 📌 Roadmap Guide – SmartPark (Django + DRF)

## ✅ Concluído até agora
1. **Repositório GitHub criado** (`smart-park-system`).  
2. **Ambiente virtual** configurado localmente (`.venv`) com Python 3.13.2.  
   - Uso do `pip-tools` (`base.in`, `dev.in`, `requirements/`).  
   - Dependências do Django e DRF corretamente instaladas no `requirements/dev.txt`.  
3. **Projeto Django inicializado** dentro de `backend/` com:
   - `smartpark/` como diretório principal de settings.  
   - `apps/` criado para organizar módulos de domínio.  
4. **App Core** criado em `backend/apps/core/`.  
   - Registrado no `INSTALLED_APPS`.  
   - Corrigido `urls.py` e importação para evitar erros de `ModuleNotFoundError`.  
5. **Script DBML → Models Django** criado e ajustado.  
   - Usado `pydbml` para processar `smart-park-db.md`.  
   - Models geradas e ajustadas (ex.: OneToOne vs ForeignKey).  
6. **Migrações iniciais** para todas as models definidas no DBML concluídas e aplicáveis.  
   - Commit feito com migrations versionadas.  

---

## ⏭️ Próximos Passos

### Passo 1 – Banco & Configurações
- [ ] Configurar PostgreSQL no `settings/dev.py` (credenciais `.env`).  
- [ ] Rodar `python manage.py migrate` contra banco real.  
- [ ] Criar **superuser** inicial para acesso ao Django Admin.  

### Passo 2 – Autenticação & Autorização
- [ ] Implementar `users`, `roles`, `user_roles` e `refresh_tokens`.  
- [ ] Adicionar fluxo **JWT + Refresh Token** conforme [MVP spec].  
- [ ] Adicionar permissões baseadas em **roles** (`app_user`, `client_admin`, `admin`).  

### Passo 3 – Tenancy & Estruturas de Clientes
- [ ] Implementar `clients` e `client_members`.  
- [ ] Configurar escopo multi-tenant básico via `client_id`.  
- [ ] CRUD para `Client` com validações de aprovação (`Pending` → `Active`).  

### Passo 4 – Catálogo de Locais
- [ ] CRUD de `store_types`, `establishments`, `lots`, `slots`.  
- [ ] Validar unicidade (`lot_code`, `slot_code`).  
- [ ] Endpoints públicos para listagem de estabelecimentos e status de vagas.  

### Passo 5 – Hardware & Eventos
- [ ] CRUD de `cameras` + `api_keys`.  
- [ ] Endpoint `POST /events/slot-status` com validação HMAC/API Key.  
- [ ] Atualizar `slot_status` em tempo real.  

### Passo 6 – Testes & Qualidade
- [ ] Criar estrutura de testes unitários (`apps/*/tests/`).  
- [ ] Testar fluxo completo: login → refresh → logout; client admin → requests; hardware → events.  
- [ ] Logs básicos estruturados para auditoria mínima.  

---

## 🛠️ Roadmap Pós-MVP
- Histórico (`slot_status_history`).  
- Debounce/histerese centralizada no backend.  
- Heartbeat de câmeras (`camera_heartbeats`).  
- Idempotência (`event_id`, `sequence`).  
- Painéis/dashboards.  
- Políticas LGPD avançadas (anonimização, retenção).  

---

## 📖 Referências Internas
- `smart-park-db.md` → schema DBML com todas as tabelas【286†smart-park-db.md】.  
- `smart-park-mvp.md` → escopo e requisitos funcionais do MVP【288†smart-park-mvp.md】【294†smart-park-mvp.md】.  
- `SmartPark.md` → visão geral do projeto e padrões adotados【290†SmartPark.md】【293†SmartPark.md】.  
