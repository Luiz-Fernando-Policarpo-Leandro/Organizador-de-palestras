import re

class OrganizadorConferencia:
    def __init__(self):
        self.filepath = "proposals.txt"
        self.propostas = []
        self.cronograma = []

        self.inicioManha = 9 * 60
        self.fimManha = 12 * 60
        self.inicioTarde = 13 * 60
        self.inicioNetworking = 16 * 60
        self.fimNetworking = 17 * 60

    def minutosParaHora(self, minutos):
        return f"{minutos // 60:02d}:{minutos % 60:02d}"

    def carregarPropostas(self):
        with open(self.filepath, 'r') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: 
                    continue

                match = re.match(r"^(.*?)\s+(\d+min|lightning)$", linha)
                if not match:
                    print(f"Erro ao ler linha: {linha}");
                    continue

                titulo, duracaoTexto = match.groups()
                duracao = 5 if duracaoTexto == "lightning" else int(duracaoTexto.replace("min", ""))
                self.propostas.append((titulo.strip(), duracao))
        
        self.propostas.sort(key=lambda x: x[1], reverse=True)

    def agendar(self):
        trilhaAtual = []
        
        palestrasManha = []
        horaAtualManha = self.inicioManha
        propostasSessao = list(self.propostas)
        i = 0
        while i < len(propostasSessao):
            titulo, duracao = propostasSessao[i]
            if horaAtualManha + duracao <= self.fimManha:
                palestrasManha.append((self.minutosParaHora(horaAtualManha), titulo, duracao))
                horaAtualManha += duracao
                self.propostas.remove((titulo, duracao)); propostasSessao.pop(i)
            else: i += 1
        
        trilhaAtual.append({"periodo": "manhã", "palestras": palestrasManha, "fimMinutos": horaAtualManha})
        
        palestrasTarde = []
        horaAtualTarde = self.inicioTarde
        propostasSessao = list(self.propostas)
        i = 0
        while i < len(propostasSessao):
            titulo, duracao = propostasSessao[i]
            fimPotencial = horaAtualTarde + duracao
            
            if fimPotencial <= self.fimNetworking:
                palestrasTarde.append((self.minutosParaHora(horaAtualTarde), titulo, duracao))
                horaAtualTarde += duracao
                self.propostas.remove((titulo, duracao)); propostasSessao.pop(i)
            else: i += 1
        
        trilhaAtual.append({"periodo": "tarde", "palestras": palestrasTarde, "fimMinutos": horaAtualTarde})
        
        return trilhaAtual, (len(palestrasManha) > 0 or len(palestrasTarde) > 0)

    def organizarConferencia(self):
        self.carregarPropostas()
        
        while self.propostas:
            novaTrilha, agendado = self.agendar()
            if not agendado and self.propostas:
                print("Aviso: Nem todas as palestras puderam ser agendadas. Verifique as restrições de tempo."); break
            self.cronograma.append(novaTrilha)

    def imprimir(self):
        for i, trilha in enumerate(self.cronograma):
            print(f"\n---")
            print(f"## Trilha {chr(65 + i)}:\n")
            
            for sessao in trilha:
                for horaStr, titulo, duracao in sessao["palestras"]:
                    duracaoDisplay = f"{duracao}min" if duracao != 5 else "lightning"
                    print(f"{horaStr} {titulo} {duracaoDisplay}")
                
                if sessao["periodo"] == "manhã": print("12:00 Almoço")
                
                if sessao["periodo"] == "tarde":
                    fimUltimaPalestraMinutos = sessao["fimMinutos"]
                    horaNetworkingMinutos = max(fimUltimaPalestraMinutos, self.inicioNetworking)
                    horaNetworkingMinutos = min(horaNetworkingMinutos, self.fimNetworking)
                    print(f"{self.minutosParaHora(horaNetworkingMinutos)} Evento de Networking")

if __name__ == "__main__":
    organizador = OrganizadorConferencia()
    organizador.organizraConferencia()
    organizador.imprimir()