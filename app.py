import streamlit as st
import os
import subprocess

# Definir os diretórios de entrada e saída
INPUT_DIR = "inputs/"
OUTPUT_DIR = "outputs/"
STATS_DIR = "stats/"
EXECUTABLE = "./main"

# Função para salvar o arquivo na pasta "inputs"
def save_uploaded_file(uploaded_file, decompress):
    file_path = None

    if decompress:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        file_path = os.path.join(OUTPUT_DIR, uploaded_file.name)
    else:
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
        output_file = output_file[:-4]
    else:
        output_file += ".lzw"

    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(STATS_DIR):
        os.makedirs(STATS_DIR)

    output_path = os.path.join(INPUT_DIR, output_file) if decompress else os.path.join(OUTPUT_DIR, output_file)
    stats_file = os.path.join(STATS_DIR, (file_path[8:] if decompress else file_path[7:]) + ".stats")

    # Construir o comando
    command = [EXECUTABLE]
    command.append(file_path[8:] if decompress else file_path[7:])

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
        return output_path, stats_file if stats else None
    else:
        st.error(f"Error executing command: {' '.join(command)}")
        st.error(process.stderr.decode())
        return None, None


# Interface do Streamlit
st.title("File Compression / Decompression")

# Inicializar o estado da sessão
if "output_path" not in st.session_state:
    st.session_state.output_path = None
if "stats_file" not in st.session_state:
    st.session_state.stats_file = None

# Escolher a operação
operation = st.selectbox("Choose operation:", ["Compression", "Decompression"])
uploaded_file = st.file_uploader("Choose a file to upload")

# Opções de compressão
max_bits = st.slider("Maximum number of bits (--max-bits)", min_value=9, max_value=16, value=12)
fixed = st.checkbox("--fixed (fixed length table)", value=False)
stats = st.checkbox("--stats (show stats)", value=False)

# Botão para iniciar o processo
if st.button("Run"):
    if uploaded_file is not None:
        # Determinar se é compressão ou descompressão
        decompress = operation == "Decompression"

        # Salvar o arquivo
        file_path = save_uploaded_file(uploaded_file, decompress)

        # Executar o processo
        output_path, stats_file = run_compression(file_path, max_bits, fixed, stats, decompress)

        # Atualizar o estado da sessão
        st.session_state.output_path = output_path
        st.session_state.stats_file = stats_file

        st.success("Process completed successfully!")
    else:
        st.warning("Please, upload a file.")

# Exibir o botão de download e estatísticas se os dados estiverem disponíveis
if st.session_state.output_path:
    with open(st.session_state.output_path, "rb") as f:
        st.download_button(
            label="Download file",
            data=f,
            file_name=os.path.basename(st.session_state.output_path),
            mime="application/octet-stream"
        )

if stats and st.session_state.stats_file:
    with open(st.session_state.stats_file, "r") as sf:
        stats_data = sf.read().replace("\n", "<br>")
        st.markdown(
            f"<div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; white-space: pre-wrap;'>{stats_data}</div>",
            unsafe_allow_html=True
        )
