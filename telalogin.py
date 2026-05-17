import customtkinter as ctk
from Painel import Painel

class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("400x300")
        self.resizable(False, False)
        try:  
            self.iconbitmap("senha.ico")
        except:
            pass

        ctk.CTkLabel(self,
        text="ACESSO RESTRITO", 
        text_color="red",
        font=ctk.CTkFont(size=16, weight="bold")  # opcional
        ).pack(pady=10)

        ctk.CTkLabel(self, text="Usuário").pack(pady=(40, 5))
        self.entry_user = ctk.CTkEntry(self, width=250)
        self.entry_user.pack()

        ctk.CTkLabel(self, text="Senha").pack(pady=(15, 5))
        self.entry_senha = ctk.CTkEntry(self, width=250, show="*")
        self.entry_senha.pack()

        ctk.CTkButton(self, text="Entrar", command=self.verificar).pack(pady=20)
        self.label_erro = ctk.CTkLabel(self, text="", text_color="red")
        self.label_erro.pack()

    def verificar(self):
        usuario = self.entry_user.get()
        senha = self.entry_senha.get()

        if usuario == "admin" and senha == "admin":
            self.destroy()
            app = Painel()
            app.mainloop()
        else:
            self.label_erro.configure(text="Usuário ou senha incorretos")

login = TelaLogin()
login.mainloop()