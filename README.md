# Control iD ADP Integrador

Projeto pessoal em Python para ler marcacoes de ponto exportadas por um equipamento/API Control iD, associar cada registro ao usuario cadastrado e exibir os dados em formato JSON.

> Status atual: o script implementa a leitura e o tratamento dos dados vindos do Control iD. As variaveis de ambiente do ADP ja aparecem na configuracao local, mas o `main.py` ainda nao envia dados para a API do ADP.

## O que o projeto faz

- Carrega credenciais e URLs a partir de um arquivo `.env`.
- Faz login no Control iD usando o endpoint `login.fcgi`.
- Busca os usuarios cadastrados no Control iD via `load_objects.fcgi`.
- Exporta o arquivo AFD usando `export_afd.fcgi`.
- Interpreta cada linha do AFD para extrair:
  - NSR
  - data e hora da marcacao
  - ID do funcionario
  - CRC da linha
- Cruza o ID do funcionario com a lista de usuarios.
- Imprime no terminal uma lista JSON com as marcacoes enriquecidas.

## Como o fluxo funciona

1. `load_dotenv()` carrega as variaveis do arquivo `.env`.
2. `login_controlid()` autentica no Control iD e retorna uma sessao.
3. `get_users(session)` carrega usuarios com os campos `id`, `name` e `registration`.
4. `get_afd(session)` exporta as linhas do AFD.
5. `parse_afd_line(line)` separa os campos de cada linha do AFD.
6. `main()` junta os dados de marcacao com os dados do funcionario e imprime o resultado.

## Estrutura do projeto

```text
.
|-- main.py              # Script principal da integracao
|-- state.json           # Estado local; hoje nao e usado pelo main.py
|-- .env.example         # Exemplo de configuracao sem segredos
|-- .gitignore           # Arquivos locais que nao devem ir para o GitHub
`-- requirements.txt     # Dependencias Python do projeto
```

## Requisitos

- Python 3
- Acesso de rede ao equipamento/API Control iD
- Credenciais validas do Control iD
- Dependencias Python listadas em `requirements.txt`

## Configuracao

Crie um arquivo `.env` na raiz do projeto seguindo o modelo abaixo:

```env
CONTROLID_URL=http://endereco-do-controlid
CONTROLID_USER=usuario
CONTROLID_PASSWORD=senha

# Reservado para evolucao futura da integracao com ADP.
ADP_API_URL=https://api-adp.example.com
ADP_TOKEN=token_adp
```

Importante: o arquivo `.env` pode conter senhas e tokens. Ele nao deve ser enviado para o GitHub.

## Instalacao

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Como executar

Com o ambiente virtual ativo e o `.env` configurado:

```powershell
python main.py
```

Durante a execucao, o script mostra mensagens de progresso no terminal:

```text
Fazendo login...
Login OK
Carregando usuarios...
Usuarios encontrados: 10
Lendo AFD...
```

Ao final, a saida esperada e uma lista JSON parecida com esta:

```json
[
  {
    "nsr": 23,
    "timestamp": "2025-12-03T14:52:00",
    "employee": {
      "id": 152,
      "name": "Nome do funcionario",
      "registration": "12345"
    }
  }
]
```

Se o funcionario de uma marcacao nao for encontrado na lista de usuarios, o campo `employee` sera `null`.

## Variaveis de ambiente

| Variavel | Obrigatoria | Uso atual |
| --- | --- | --- |
| `CONTROLID_URL` | Sim | URL base do Control iD. |
| `CONTROLID_USER` | Sim | Usuario usado para login no Control iD. |
| `CONTROLID_PASSWORD` | Sim | Senha usada para login no Control iD. |
| `ADP_API_URL` | Nao | Reservada para uma futura integracao com ADP. |
| `ADP_TOKEN` | Nao | Reservada para uma futura integracao com ADP. |

## Limitacoes atuais

- O codigo ainda nao envia dados para o ADP.
- O arquivo `state.json` possui `last_nsr`, mas o script atual ainda nao usa esse valor para filtrar marcacoes ja processadas.
- Linhas AFD com formato invalido ou tamanho menor que o esperado sao ignoradas.
- O parser usa posicoes fixas da linha AFD, entao alteracoes no formato exportado podem exigir ajuste no `parse_afd_line`.
- Ainda nao ha testes automatizados.

## Proximos passos possiveis

- Implementar o envio das marcacoes para a API do ADP.
- Usar `state.json` para processar apenas registros com NSR maior que o ultimo ja sincronizado.
- Criar logs de execucao e tratamento de erros mais detalhado.
- Adicionar testes para o parser de linhas AFD.
- Criar um modo de execucao agendado para sincronizacao recorrente.

## Seguranca

Antes de publicar no GitHub, confira se arquivos com credenciais reais nao foram adicionados ao controle de versao. O `.gitignore` deste projeto ja ignora `.env` e `.venv/`.
