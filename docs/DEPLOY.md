# ===========================================

# SmartPark - Guia de Deploy com Docker

# ===========================================

Este guia fornece instruções completas para fazer deploy do SmartPark usando Docker.

## 📋 Pré-requisitos

-   Docker Engine 20.10+
-   Docker Compose 2.0+
-   Git
-   2GB+ RAM disponível
-   10GB+ espaço em disco

## 🚀 Deploy Rápido (Desenvolvimento)

### 1. Clonar o Repositório

```bash
git clone <repository-url>
cd smart-park-system
```

### 2. Configurar Ambiente

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar configurações (opcional para desenvolvimento)
nano .env
```

### 3. Iniciar Aplicação

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar status dos containers
docker-compose ps

# Visualizar logs
docker-compose logs -f web
```

### 4. Acessar a Aplicação

-   **Aplicação Django**: http://localhost:8000
-   **Admin Django**: http://localhost:8000/admin (admin/admin123)
-   **Interface DB**: http://localhost:8080
-   **Interface Redis**: http://localhost:8081

## 🏭 Deploy de Produção

### 1. Configuração de Produção

```bash
# Criar arquivo de produção
cp .env.example .env.prod

# Configurar variáveis de produção
nano .env.prod
```

**Variáveis críticas para produção**:

```env
DJANGO_SETTINGS_MODULE=smartpark.settings.prod
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-production-key
DATABASE_URL=postgresql://user:pass@db:5432/smartpark_prod
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. Deploy com Nginx

```bash
# Usar arquivo de produção
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verificar certificados SSL (se configurado)
docker-compose exec nginx nginx -t
```

### 3. Configuração SSL (Opcional)

```bash
# Gerar certificados Let's Encrypt
docker-compose exec nginx certbot --nginx -d yourdomain.com

# Renovar certificados automaticamente
echo "0 12 * * * /usr/bin/docker-compose exec nginx certbot renew --quiet" | crontab -
```

## 🔧 Comandos Úteis

### Gerenciamento da Aplicação

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes
docker-compose down -v

# Rebuild da aplicação
docker-compose build web

# Executar comandos Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Shell interativo
docker-compose exec web python manage.py shell
docker-compose exec web bash
```

### Monitoramento

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver logs específicos
docker-compose logs web
docker-compose logs db
docker-compose logs redis

# Verificar recursos
docker stats

# Verificar saúde dos containers
docker-compose ps
```

### Backup e Restore

```bash
# Backup do banco de dados
docker-compose exec db pg_dump -U postgres smartpark_db > backup.sql

# Restore do banco de dados
docker-compose exec -T db psql -U postgres smartpark_db < backup.sql

# Backup de arquivos media
docker-compose exec web tar -czf /tmp/media_backup.tar.gz /app/media/
docker cp $(docker-compose ps -q web):/tmp/media_backup.tar.gz ./media_backup.tar.gz
```

## 🐛 Troubleshooting

### Problemas Comuns

**Container não inicia**:

```bash
# Verificar logs detalhados
docker-compose logs web

# Verificar configuração
docker-compose config

# Verificar recursos do sistema
docker system df
```

**Erro de conexão com banco**:

```bash
# Verificar se o banco está rodando
docker-compose ps db

# Testar conexão
docker-compose exec web python manage.py check --database default

# Reset do banco (CUIDADO: perde dados)
docker-compose down -v
docker-compose up -d
```

**Problemas de permissão**:

```bash
# Verificar usuário do container
docker-compose exec web whoami

# Ajustar permissões de arquivos
sudo chown -R $USER:$USER .
```

**Performance lenta**:

```bash
# Verificar recursos
docker stats

# Limpar containers parados
docker system prune

# Verificar logs de erro
docker-compose logs | grep ERROR
```

### Logs Importantes

```bash
# Logs da aplicação Django
docker-compose logs web

# Logs do banco de dados
docker-compose logs db

# Logs do Nginx (se usando)
docker-compose logs nginx

# Logs do Redis
docker-compose logs redis
```

## 📊 Monitoramento e Métricas

### Health Checks

```bash
# Verificar saúde da aplicação
curl http://localhost:8000/health/

# Verificar status dos serviços
docker-compose ps
```

### Métricas de Performance

```bash
# CPU e Memória
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Uso de disco
docker system df

# Logs de performance Django
docker-compose logs web | grep "GET\|POST"
```

## 🔒 Configuração de Segurança

### SSL/TLS

1. Configurar certificados SSL
2. Redirecionar HTTP para HTTPS
3. Configurar HSTS headers

### Firewall

```bash
# Permitir apenas portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Backup Automático

```bash
# Script de backup diário
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U postgres smartpark_db > backup_$DATE.sql
find . -name "backup_*.sql" -mtime +7 -delete
```

## 📋 Checklist de Deploy

### Pré-Deploy

-   [ ] Configurar variáveis de ambiente
-   [ ] Verificar recursos do servidor
-   [ ] Configurar domínio DNS
-   [ ] Preparar certificados SSL

### Deploy

-   [ ] Build das imagens Docker
-   [ ] Executar migrações
-   [ ] Coletar arquivos estáticos
-   [ ] Configurar Nginx
-   [ ] Verificar health checks

### Pós-Deploy

-   [ ] Testar endpoints principais
-   [ ] Verificar logs
-   [ ] Configurar monitoramento
-   [ ] Configurar backups
-   [ ] Documentar credenciais

## 🆘 Suporte

Para problemas específicos:

1. Verificar logs detalhados
2. Consultar documentação Django
3. Verificar issues do GitHub
4. Contatar equipe de desenvolvimento

## 📚 Recursos Adicionais

-   [Documentação Docker](https://docs.docker.com/)
-   [Documentação Django](https://docs.djangoproject.com/)
-   [Guias de Segurança Django](https://docs.djangoproject.com/en/5.0/topics/security/)
-   [Best Practices Docker](https://docs.docker.com/develop/best-practices/)
