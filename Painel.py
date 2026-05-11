import customtkinter as ctk
import requests
import threading

class Painel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Painel de Consulta CNPJ")
        self.geometry("700x500")
        try:  
            self.iconbitmap("icone.ico")
        except:
            pass

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # sidebar
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="Painel de Consulta",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))

        ctk.CTkFrame(
            self.sidebar, height=1, fg_color="gray40"
        ).pack(fill="x", padx=10, pady=(0, 10))

        # botões normais — sem o Sair aqui
        botoes = ["Início", "Consultar CNPJ"]
        for nome in botoes:
            ctk.CTkButton(
                self.sidebar,
                text=nome,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                anchor="w",
                hover_color=("gray85", "gray25")
            ).pack(fill="x", padx=10, pady=3)

        # botão Sair FORA do for
        ctk.CTkButton(
            self.sidebar,
            text="Sair",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            anchor="w",
            hover_color=("gray85", "gray25"),
            command=self.sair
        ).pack(fill="x", padx=10, pady=(50, 3))

        # área principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.titulo = ctk.CTkLabel(
            self.main_frame,
            text="Painel de Consulta CNPJ",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.titulo.pack(anchor="w", pady=(0, 20))

        frame_busca = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame_busca.pack(fill="x", pady=(0, 15))

        self.frame_resultado = ctk.CTkScrollableFrame(
            self.main_frame,
            label_text="Resultado da Consulta",
            label_font=ctk.CTkFont(size=13, weight="bold"))     
        self.frame_resultado.pack(fill="both", expand=True, pady=10)

        self.label_resultado = ctk.CTkLabel(
            self.frame_resultado,
            text="Nenhuma consulta realizada.",
            justify="left",
            anchor="nw",
            wraplength=400
        )
        self.label_resultado.pack(padx=20, pady=20, fill="both", expand=True)

        self.btn_copiar = ctk.CTkButton(
            self.frame_resultado,
            text="Copiar dados",
            width=120,
            state="disabled",
            command=self.copiar_resultado
        )
        self.btn_copiar.pack(pady=(0, 15))

        self.entry_cnpj = ctk.CTkEntry(
            frame_busca,
            placeholder_text="Digite o CNPJ — ex: 00.000.000/0001-00",
            width=350
        )
        self.entry_cnpj.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            frame_busca,
            text="Consultar",
            width=100,
            command=self.consultar_cnpj
        ).pack(side="left")

    # ---- funções abaixo, todas no mesmo nível ----

    def consultar_cnpj(self):
        cnpj = self.entry_cnpj.get()

        if cnpj == "":
            self.label_resultado.configure(text="Por favor, insira um CNPJ válido.")
            self.entry_cnpj.configure(border_color="red")
            return

        cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")

        if len(cnpj_limpo) != 14:
            self.label_resultado.configure(text="CNPJ inválido! Precisa ter 14 dígitos.")
            self.entry_cnpj.configure(border_color="red")
            return

        self.label_resultado.configure(text="Consultando...")

        try:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
            resposta = requests.get(url, timeout=10)
            dados = resposta.json()

            if resposta.status_code == 200:
                texto = (
                    f"Razão Social:  {dados.get('razao_social', '-')}\n"
                    f"Situação:      {dados.get('descricao_situacao_cadastral', '-')}\n"
                    f"CEP:           {dados.get('cep', '-')}\n"
                    f"Município:     {dados.get('municipio', '-')} / {dados.get('uf', '-')}\n"
                    f"Endereço:      {dados.get('logradouro', '-')}, {dados.get('numero', '-')}"
                )
                self.label_resultado.configure(text=texto)
                self.btn_copiar.configure(state="normal")
                self.entry_cnpj.configure(border_color="")
            else:
                self.label_resultado.configure(text="CNPJ não encontrado.")
                self.entry_cnpj.configure(border_color="red")

        except Exception as erro:
            self.label_resultado.configure(text=f"Erro de conexão: {erro}")
            self.entry_cnpj.configure(border_color="red")
    def copiar_resultado(self):
        texto = self.label_resultado.cget("text")
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.btn_copiar.configure(text="Copiado! ✓")
        self.after(2000, lambda: self.btn_copiar.configure(text="Copiar dados"))

    def sair(self):
        self.destroy()

if __name__ == "__main__":
    app = Painel()
    app.mainloop()