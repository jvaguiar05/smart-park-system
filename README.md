# SmartPark – Visão Geral & Padrões do Projeto (UPX)

> **Contexto**: Projeto acadêmico da disciplina **UPX – Usina de Projetos Experimentais** (Facens), alinhado aos **ODS da ONU** (foco no **ODS 11 – Cidades e Comunidades Sustentáveis**). Tema do semestre: **Smart Cities** com ênfase em **mobilidade urbana**.

---

## 1 Propósito & Problema

**Problema**: Motoristas perdem tempo procurando vagas; estabelecimentos não expõem de forma padronizada a ocupação de seus estacionamentos.

**Objetivo do SmartPark**: Exibir, em tempo quase real, a **disponibilidade de vagas** (carro/moto) em
**estabelecimentos comerciais** parceiros, permitindo que **usuários** encontrem vagas e que **clientes (empresas)** gerenciem seus pátios e dispositivos.

Benefícios:

* Redução de tempo de busca → menor trânsito local/emissões.
* Visão de ocupação para o comércio (gestão operacional).
* Base para políticas de mobilidade (dados históricos agregados).

---

## 2 Escopo Prático (3 frentes)

1. **Front-end (App/Portal)**

   * App para usuários consultarem disponibilidade por estabelecimento/lote.
   * Painel interno (admin/backoffice) para clientes e operadores.
2. **Back-end (API + DB + serviços)**

   * API REST pública/privada; persistência; tempo real (SSE/WS).
   * Gestão de clientes, estabelecimentos, câmeras, lotes e vagas.
3. **Hardware/Edge (Visão Computacional)**

   * Agente de câmera processa vídeo localmente (detecção carro/moto).
   * Publica **eventos de mudança** de status de vaga para a API.

---

## 3 Decisões Técnicas (baseline)

* **Linguagem**: **Python** end‑to‑end.
* **Back-end**: **Django + DRF (Django REST Framework)**

  * Motivo: produtividade + **Django Admin** pronto para backoffice B2B; permissões maduras.
  * Tempo real: **SSE** (simples) ou **Django Channels** (WebSocket) no painel operacional.
* **Banco de Dados**: **PostgreSQL** (com migrações e índices); opcional **PostGIS** para geometria.
* **Cache/Filas (opcional)**: **Redis** (cache, rate limit; Celery/RQ p/ jobs).
* **Agente de Visão (Edge)**: Python + OpenCV + modelo de detecção (ex.: detector pré‑treinado) → envia eventos REST idempotentes para a API.
* **Observabilidade**: logs estruturados; métricas básicas; rastreamento (OpenTelemetry opcional).

> Nota: A pilha acima prioriza entrega rápida com governança (admin pronto). O agente de visão fica **separado** do back‑end, comunicando por REST.

---

## 4 Conceitos‑chave de Visão Computacional (enxuto)

* **Fase de Calibração (mapa)**: sistema "aprende" **onde** estão as vagas; salva **polígonos** por vaga (ex.: A1…C3) em um **mapa** (versão `mapVersion`).
* **Fase Operacional**: a cada frame, detecta **carros/motos**; cruza com polígonos; decide **livre/ocupada** e o tipo de veículo.
* **Debounce/Histerese**: mudanças só se confirmam após **N frames** consecutivos + **cooldown** mínimo.
* **Deriva (drift)**: se a câmera mexer ou o cenário mudar, sistema sinaliza **recalibração** (ajuste por fileiras, não tudo).

Resultados:

* **Mapa é estático** (versionado) e **não** precisa ser redescoberto o tempo todo.
* O agente publica **apenas mudanças** de status (eventos), reduzindo tráfego e processamento no back-end.

---

## 5 Identificadores & Convenções

* **lotCode**: código lógico do lote/estacionamento (ex.: `MAQUETE-01`).
* **cameraId**: identificador da câmera/agente (ex.: `CAM-ENTRADA`).
* **slotCode**: identificador humano de vaga em **matriz** (ex.: `A1`, `A2` … `C3`).
* **Chave canônica**: `lotCode:slotCode` (ex.: `MAQUETE-01:A1`).

---

## 6 Domínio & Modelo (conceitual)

**Identity**

* `User` (roles: `admin`, `client_admin`, `operator`, `app_user`).
* `APIKey` / `HMACSecret` (para agentes de câmera).

**Clientes & Locais**

* `Client` (empresa contratante; multi‑tenant simples por `client_id`).
* `Establishment` (unidade/loja do cliente).

**Dispositivos**

* `Camera` (`camera_id`, pertence a `Establishment`; `last_seen_at`, `state`, `api_key`).

**Parking**

* `Lot` (pátio/área de estacionamento; pertence a `Establishment`).
* `Slot` (`slotCode` A1…; `type` = `car`|`moto`; `polygon` \[pontos]; `active`; `row_version`).
* `SlotMapVersion` (`mapVersion`, payload do mapa, auditoria/versionamento).
* `SlotStatus` (`status` = `FREE`|`OCCUPIED`|`UNKNOWN`; `vehicle` = `car`|`motorcycle`|`none`; `confidence`; `changed_at`).
* `SlotStatusHistory` (auditoria/relatórios).

**Eventos/Ingestão**

* `SlotStatusChanged` (idempotente; `eventId`, `sequence` por vaga/câmera).
* `CameraState`/`Heartbeat` (online/offline; monitoramento).

> **Chaves & Índices**: `UNIQUE(lot_code, slot_code)`; índices em `changed_at`, `last_seen_at` e chaves de escopo por `client_id`.

---

## 7 API REST – v1 (contratos essenciais)

### 7.1 Rotas de leitura

* `GET /v1/lots/{lotCode}/slots?active=true` → **Mapa de vagas** (inclui `mapVersion`).
* `GET /v1/lots/{lotCode}/status` → **Snapshot** de status das vagas.
* `GET /v1/public/establishments` → catálogo para app (filtros por cidade, tags, etc.).
* `GET /v1/public/establishments/{id}/status` → ocupação agregada (para usuário final).

### 7.2 Rotas administrativas

* `POST /v1/lots/{lotCode}/slots/bulk` → criar/atualizar vagas (CRUD em lote).
* `PATCH /v1/lots/{lotCode}/slots/{slotCode}` → editar tipo/polígono/ativo.
* `POST /v1/cameras/{cameraId}/heartbeat` → batimento da câmera.

### 7.3 Ingestão de eventos (agente de visão)

* `POST /v1/events/slot-status` → evento de **mudança de status de vaga**.

#### 7.3.1 Payloads (exemplos)

**Mapa de Vagas** (`GET /slots`)

```json
{
  "lotCode": "MAQUETE-01",
  "mapVersion": 3,
  "projection": { "space": "pixel", "frameWidth": 1920, "frameHeight": 1080, "homographyVersion": 2 },
  "slots": [
    { "slotCode": "A1", "type": "car",  "active": true, "polygon": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] },
    { "slotCode": "C2", "type": "moto", "active": true, "polygon": [[...]] }
  ],
  "updatedAt": "2025-08-26T21:00:00Z"
}
```

**Snapshot de Status** (`GET /status`)

```json
{
  "lotCode": "MAQUETE-01",
  "asOf": "2025-08-26T21:05:12Z",
  "status": [
    { "slotCode": "A1", "status": "OCCUPIED", "vehicle": "car",  "confidence": 0.94, "changedAt": "2025-08-26T21:05:03Z" },
    { "slotCode": "A2", "status": "FREE",     "vehicle": "none", "confidence": 1.00, "changedAt": "2025-08-26T20:59:10Z" }
  ]
}
```

**Evento `SlotStatusChanged`** (`POST /events/slot-status`)

```json
{
  "eventId": "3f5f6a7e-7a0a-4c6e-9d3e-9c2b9a2c4f10",
  "eventType": "SlotStatusChanged",
  "occurredAt": "2025-08-26T21:05:03Z",
  "lotCode": "MAQUETE-01",
  "cameraId": "CAM-ENTRADA",
  "mapVersion": 3,
  "sequence": 12,
  "slot": {
    "slotCode": "A1",
    "prev": { "status": "FREE", "vehicle": "none" },
    "curr": { "status": "OCCUPIED", "vehicle": "car", "confidence": 0.94 }
  },
  "source": { "model": "detector-x", "version": "1.0.0" }
}
```

**Erros (padrão)**

```json
{ "code": "UNKNOWN_SLOT", "message": "Slot A7 not found in MAQUETE-01", "traceId": "..." }
```

---

## 8 Regras de Decisão (vaga)

* **Ocupada** se **IoU/overlap** (veículo × polígono) ≥ **t** (ex.: 0.15–0.25).
* **Confirmação**: mudança só após **N frames** consecutivos (ex.: `N=3`) e **cooldown** mínimo (ex.: 1–2 s).
* **Tipos**: `type` da vaga vem do **cadastro**; `vehicleDetected` da **detecção** (`car`|`motorcycle`).
* **Estados**: `FREE` | `OCCUPIED` | `UNKNOWN` (ex.: câmera offline → `UNKNOWN`).

---

## 9 Segurança & LGPD

* **TLS** obrigatório; timestamps **UTC ISO‑8601**.
* **Autorização por papéis** (`admin`, `client_admin`, `operator`, `app_user`).
* **Agentes** (câmeras): autenticação por **API Key** + **HMAC** (headers `X-Timestamp`, `X-Signature`).
* **Idempotência**: `eventId` (ou `Idempotency-Key`) + `sequence` por vaga.
* **Privacidade**: processamento **no edge**; **não enviar frames** ao back‑end (somente metadados). Se necessário, anonimizar (blur) localmente.

---

## 10 Desempenho & Limitações (expectativas realistas)

* **Precisão** (dia/boa luz): carros \~90–95%; motos 80–90% (melhora com amostras do cenário).
* **Latency/FPS**: 10–25 FPS no edge moderado; eventos só em mudanças.
* **Limitações**: noite/chuva/sombra dura; oclusões; motos pequenas próximas às linhas.

---

## 11 MVP & Entregas (sugestão)

**Sprint 1** – API base + ingestão de eventos + snapshot; modelos/migrações; admin registrado.

**Sprint 2** – Cadastro de vagas (A1…C3) via admin + upload/edição de polígonos; painel simples.

**Sprint 3** – Debounce/histerese; heartbeat; `UNKNOWN` quando offline; SSE no painel.

**Sprint 4** – Métricas/histórico; alertas básicos; refinamento de UX e documentação.

---

## 12 Testes & Aceitação (checklist)

* [ ] Câmera sobe → baixa `mapVersion` atual; envia heartbeat.
* [ ] Evento fora de ordem/duplicado → ignorado/idempotente.
* [ ] Troca de estado só após N frames + cooldown.
* [ ] Câmera offline → slots do lote em `UNKNOWN` após timeout.
* [ ] Admin CRUD de Client/Establishment/Lot/Slot/Camera (com filtros/roles).
* [ ] App/Portal lê `/public/establishments` e `/lots/{lot}/status`.

---

## 13 Glossário

* **Lote (Lot)**: área de estacionamento (ex.: pátio da loja).
* **Vaga (Slot)**: posição individual (ex.: `A1`).
* **Mapa**: coleção de polígonos das vagas (versionado).
* **Agente de Visão**: serviço na borda que processa vídeo e publica eventos.
* **Drift**: desalinhamento do campo de visão (câmera mexeu/cenário mudou).

---

## 14 Extensões Futuras (fora do MVP)

* Tarifação/contratos de cliente; relatórios avançados e dashboards públicos.
* Auditoria completa (SlotStatusHistory) e exportações.
* Geofencing; múltiplas câmeras por lote; fusão de sensores.
* Classificação de uso indevido (moto em vaga de carro etc.).
* Integração com placas/controle de acesso (preservando LGPD).

---

> **Resumo**: O SmartPark é um sistema **event‑driven** com **mapa estático** de vagas e **status dinâmico** vindo do edge. A arquitetura com **Django+DRF** para backoffice e **Python CV** no agente entrega rapidamente um produto operável (B2B + B2C), com contratos REST claros, segurança básica (HMAC/TLS) e escalabilidade para a maquete e além.
