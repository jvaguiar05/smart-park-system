# 🚀 CI/CD Pipeline - SmartPark

Este diretório contém a configuração completa do pipeline CI/CD do SmartPark usando GitHub Actions.

## 📋 Workflows Configurados

### 1. `django.yml` - Pipeline Principal

**Triggers**: Push e PR para `main` e `develop`

**Jobs:**

-   **Test Suite**: Testa em Python 3.11, 3.12, 3.13 com PostgreSQL
-   **Code Quality**: Linting com flake8, black, isort, mypy
-   **Security Scan**: Verificação de vulnerabilidades com safety e bandit
-   **Build Check**: Validação de build para deploy

### 2. `pr-checks.yml` - Checks de Pull Request

**Triggers**: PRs para `main` e `develop`

**Jobs:**

-   **Quick Tests**: Testes rápidos em PRs
-   **Validate Migrations**: Validação de migrações Django
-   **Documentation Check**: Verificação de documentação

### 3. `dependabot.yml` - Atualizações Automáticas

**Funcionalidade**: Mantém dependências atualizadas

-   **Python packages**: Semanal (segunda-feira, 10h)
-   **GitHub Actions**: Semanal (segunda-feira, 10h)

## 🔧 Configurações Adicionais

### Arquivos de Configuração

-   `.coveragerc`: Configuração de coverage
-   `pytest.ini`: Configuração do pytest
-   `smartpark/settings/test.py`: Settings otimizadas para testes

### Templates

-   `ISSUE_TEMPLATE/`: Templates para bug reports e feature requests
-   `PULL_REQUEST_TEMPLATE.md`: Template para PRs

## 📊 Coverage e Qualidade

**Coverage Mínimo**: 80%
**Ferramentas de Qualidade**:

-   Black (formatação)
-   isort (imports)
-   flake8 (linting)
-   mypy (type checking)
-   safety (vulnerabilidades)
-   bandit (segurança)

## 🚦 Status dos Workflows

Para verificar o status dos workflows:

1. Acesse a aba "Actions" no GitHub
2. Verifique os badges no README principal
3. PRs mostram status dos checks automaticamente

## 📝 Como Usar

### Para Desenvolvedores

1. **Fork** o repositório
2. **Crie branch** para sua feature
3. **Faça commits** seguindo convenções
4. **Abra PR** - workflows executam automaticamente
5. **Aguarde aprovação** dos checks

### Para Maintainers

1. **Revise PRs** com checks verdes
2. **Merge** para `main` dispara build completo
3. **Monitor** workflows para issues

## 🔍 Troubleshooting

### Testes Falhando

```bash
# Executar localmente
cd backend
python manage.py test

# Com coverage
coverage run manage.py test
coverage report
```

### Problemas de Linting

```bash
# Corrigir formatação
black backend/
isort backend/

# Verificar issues
flake8 backend/
```

### Issues de Dependências

```bash
# Verificar vulnerabilidades
safety check -r requirements/base.txt

# Verificar segurança
bandit -r backend/
```

## 📈 Métricas

O pipeline coleta métricas sobre:

-   **Cobertura de testes**
-   **Tempo de execução**
-   **Qualidade do código**
-   **Vulnerabilidades de segurança**

## 🛠️ Manutenção

### Atualizações Semanais

-   Dependabot cria PRs automaticamente
-   Review e merge conforme necessário

### Monitoramento

-   Verifique workflows falhando regularmente
-   Atualize Python/Django versions conforme necessário
-   Mantenha documentação atualizada
