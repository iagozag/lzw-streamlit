import streamlit as st
import os
import subprocess

# Definir os diretórios de entrada e saída
INPUT_DIR = "inputs/"
OUTPUT_DIR = "outputs/"
EXECUTABLE = "./main"

# Função para salvar o arquivo na pasta "inputs"
def save_uploaded_file(uploaded_file):
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)

    file_path = os.path.join(INPUT_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Função para executar a compressão/descompressão
def run_compression(file_path, max_bits, fixed, stats, decompress):
    output_file = os.path.basename(file_path)
    if decompress:
        output_file = output_file.replace(".lzw", ".decompressed")
    else:
        output_file += ".lzw"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_path = os.path.join(OUTPUT_DIR, output_file)

    # Construir o comando
    command = [EXECUTABLE]
    command.append(file_path[7:])

    if decompress:
        command.append("--decompress")
    else:
        command.append("--compress")

    command += ["--max-bits", str(max_bits)]

    if fixed:
        command.append("--fixed")
    if stats:
        command.append("--stats")

    # Executar o comando
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Verificar o resultado
    if process.returncode == 0:
        return output_path
    else:
        st.error(f"Erro ao executar o comando: {' '.join(command)}")
        st.error(process.stderr.decode())
        return None

# Interface do Streamlit
st.title("Compressão e Descompressão de Arquivos")

# Escolher a operação
operation = st.selectbox("Escolha a operação:", ["Compressão", "Descompressão"])
uploaded_file = st.file_uploader("Escolha um arquivo para fazer upload")

# Opções de compressão
max_bits = st.slider("Número máximo de bits (--max-bits)", min_value=9, max_value=16, value=12)
fixed = st.checkbox("--fixed (tabela de tamanho fixo)", value=False)
stats = st.checkbox("--stats (mostrar estatísticas)", value=False)

# Botão para iniciar o processo
if st.button("Executar"):
    if uploaded_file is not None:
        # Salvar o arquivo
        file_path = save_uploaded_file(uploaded_file)

        # Determinar se é compressão ou descompressão
        decompress = operation == "Descompressão"

        # Executar o processo
        output_path = run_compression(file_path, max_bits, fixed, stats, decompress)

        if output_path:
            # Disponibilizar para download
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Baixar Arquivo",
                    data=f,
                    file_name=os.path.basename(output_path),
                    mime="application/octet-stream"
                )
            st.success("Processo concluído com sucesso!")
    else:
        st.warning("Por favor, faça o upload de um arquivo.")
