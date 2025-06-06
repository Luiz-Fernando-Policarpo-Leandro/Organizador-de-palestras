import re

class Palestra:
    # Classe da palestra
    def __init__(self, titulo, duracao_minutos):
        self.titulo = titulo
        self.duracao = duracao_minutos
        self.hora_inicio = None # Hora definida no agendamento

    def __repr__(self):
        return f"Palestra(Titulo='{self.titulo}', Duracao={self.duracao}min)"

class OrganizadorConferencia:
    def __init__(self):
        self.filepath = "proposals.txt"
        self.propostas = []  # Palestras a serem agendadas
        self.cronograma = [] # Cronograma final organizado em trilhas

        # Horários fixos da conferência em minutos
        self.INICIO_MANHA = 9 * 60
        self.FIM_MANHA = 12 * 60
        self.HORA_DO_ALMOCO = 13 * 60
        self.INICIO_NETWORKING = 16 * 60
        self.FIM_NETWORKING = 17 * 60

    def minutosParaHora(self, minutos):
        # Converte minutos para HH:MM
        return f"{minutos // 60:02d}:{minutos % 60:02d}"

    def carregarPropostas(self):
        # Carrega propostas do arquivo e cria objetos Palestra
        with open(self.filepath, 'r') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: 
                    continue

                match = re.match(r"^(.*?)\s+(\d+min|lightning)$", linha)
                if not match:
                    print(f"Erro ao ler linha: {linha}")
                    continue

                titulo_str, duracao_str = match.groups()
                duracao = 5 if duracao_str == "lightning" else int(duracao_str.replace("min", ""))
                self.propostas.append(Palestra(titulo_str.strip(), duracao))
        
        # Ordena palestras pela maior duração
        self.propostas.sort(key=lambda p: p.duracao, reverse=True)

    def agendar(self):
        # Agenda palestras para uma nova trilha (manhã e tarde)
        resultado = []
        
        # --- Sessão da Manhã ---
        palestrasManha = []
        horaAtualManha = self.INICIO_MANHA
        propostasDisponiveisAtual = list(self.propostas) # Cópia para iteração segura
        
        for palestra in propostasDisponiveisAtual:
            # Verifica se a palestra cabe na sessão
            if horaAtualManha + palestra.duracao <= self.FIM_MANHA:
                palestra.hora_inicio = horaAtualManha # Define hora de início
                palestrasManha.append(palestra)
                horaAtualManha += palestra.duracao # Avança o tempo
                self.propostas.remove(palestra) # Remove da lista principal
        
        resultado.append({"periodo": "manhã", "palestras": palestrasManha, "fimMinutos": horaAtualManha})
        
        # Sessão da Tarde XD
        palestrasDaTarde = []
        horaAtualTarde = self.HORA_DO_ALMOCO
        propostasDisponiveisAtual = list(self.propostas) # Nova cópia
        
        for palestra in propostasDisponiveisAtual:
            fimPotencial = horaAtualTarde + palestra.duracao
            # Verifica se a palestra cabe na sessão e antes do fim do networking
            if fimPotencial <= self.FIM_NETWORKING:
                palestra.hora_inicio = horaAtualTarde
                palestrasDaTarde.append(palestra)
                horaAtualTarde += palestra.duracao
                self.propostas.remove(palestra)
        
        resultado.append({"periodo": "tarde", "palestras": palestrasDaTarde, "fimMinutos": horaAtualTarde})
        
        # Retorna a trilha e um flag se algo foi agendado
        foiAgendadoNestaTrilha = (len(palestrasManha) > 0 or len(palestrasDaTarde) > 0)
        return resultado, foiAgendadoNestaTrilha

    def organizarConferencia(self):
        # Orquestra o processo de organização
        self.carregarPropostas()
        
        # Cria trilhas enquanto houver propostas
        while self.propostas:
            novaTrilha, agendado = self.agendar()
            # Interrompe se nenhuma palestra for agendada e ainda houver propostas
            if not agendado and self.propostas:
                print("Aviso: Nem todas as palestras puderam ser agendadas.")
                break
            self.cronograma.append(novaTrilha) # Adiciona a nova trilha

    def imprimir(self):
        # Imprime o cronograma final
        for i, trilha in enumerate(self.cronograma):
            print(f"\n---")
            print(f"## Trilha {chr(65 + i)}:\n") # A, B, C...
            
            for sessao in trilha:
                for palestra in sessao["palestras"]:
                    horaStr = self.minutosParaHora(palestra.hora_inicio)
                    duracaoDisplay = f"{palestra.duracao}min" if palestra.duracao != 5 else "lightning"
                    print(f"{horaStr} {palestra.titulo.strip()} {duracaoDisplay}")
                
                if sessao["periodo"] == "manhã": print("12:00 Almoço")
                
                if sessao["periodo"] == "tarde":
                    fimUltimaPalestraMinutos = sessao["fimMinutos"]
                    # Calcula o horário do networking
                    horaNetworkingMinutos = max(fimUltimaPalestraMinutos, self.INICIO_NETWORKING)
                    horaNetworkingMinutos = min(horaNetworkingMinutos, self.FIM_NETWORKING)
                    print(f"{self.minutosParaHora(horaNetworkingMinutos)} Evento de Networking")


if __name__ == "__main__":
    organizador = OrganizadorConferencia()
    organizador.organizarConferencia()
    organizador.imprimir()