# Usar uma imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar o conteúdo do diretório local para o container
COPY . /app

# Instalar as dependências do projeto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expor a porta do Flask (5000)
EXPOSE 5000

# Definir o comando para iniciar a aplicação Flask
CMD ["python", "app.py"]
