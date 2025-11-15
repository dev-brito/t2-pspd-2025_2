#!/bin/bash

# Nome do arquivo a ser replicado (mude para o seu arquivo)
FILE="big-file.txt"
COPIES=15

# 1. Verificar se o arquivo existe
if [ ! -f "$FILE" ]; then
    echo "Erro: Arquivo '$FILE' não encontrado."
    exit 1
fi

# 2. Salvar o conteúdo original em um arquivo temporário
# Isso é crucial para evitar que o 'cat' leia o conteúdo crescente do arquivo
# enquanto escreve, o que levaria a um loop infinito (fork bomb) e corrupção.
TMP_FILE=$(mktemp)
cat "$FILE" > "$TMP_FILE"

# 3. Limpar o arquivo original (usando >)
# Isso garante que a primeira cópia não seja o conteúdo duplicado.
> "$FILE"

# 4. Concatenar o conteúdo 100 vezes
echo "Replicando o conteúdo de '$FILE' $COPIES vezes..."

# Loop de 1 até o número de cópias
for i in $(seq 1 $COPIES); do
    cat "$TMP_FILE" >> "$FILE" # Adiciona o conteúdo do temporário ao original
done

# 5. Remover o arquivo temporário
rm "$TMP_FILE"

echo "Replicação concluída. '$FILE' agora tem o conteúdo original repetido $COPIES vezes."
