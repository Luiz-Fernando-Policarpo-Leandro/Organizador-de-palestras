import re

class Palestra:
    def __init__(self, titulo, duracao_minutos):
        self.titulo = titulo
        self.duracao = duracao_minutos
        self.hora_inicio = None  # Hora definida no agendamento

    def __repr__(self):
        return f"Palestra(Titulo='{self.titulo}', Duracao={self.duracao}min)"


class OrganizadorConferencia:
    def __init__(self, filepath="proposals.txt"):
        self.filepath = filepath
        self.propostas = []   # Palestras a serem agendadas
        self.cronograma = []  # Cronograma final organizado em trilhas

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
        # Carrega propostas do arquivo e cria objetos da classe Palestra
        try:
            with open(self.filepath, 'r', encoding="UTF-8") as f:
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

            self.propostas.sort(key=lambda p: p.duracao, reverse=True)

        except FileNotFoundError:
            print(f"Lista Palestra inexistente: {self.filepath}")

    def agendarSessao(self, propostas, hora_inicio, hora_fim):
        palestras_sessao = []
        hora_atual = hora_inicio
        restantes = []

        for palestra in propostas:
            if hora_atual + palestra.duracao <= hora_fim:
                palestra.hora_inicio = hora_atual
                palestras_sessao.append(palestra)
                hora_atual += palestra.duracao
            else:
                restantes.append(palestra)

        return palestras_sessao, restantes, hora_atual

    def agendar(self):
        nova_trilha_agendada = []

        # Sessão da manhã
        palestrasManha, restantesManha, fimManha = self.agendarSessao(self.propostas, self.INICIO_MANHA, self.FIM_MANHA)
        nova_trilha_agendada.append({
            "periodo": "manhã",
            "palestras": palestrasManha,
            "fimMinutos": fimManha
        })

        # Sessão da tarde
        palestrasTarde, restantesTarde, fimTarde = self.agendarSessao(restantesManha, self.HORA_DO_ALMOCO, self.FIM_NETWORKING)
        nova_trilha_agendada.append({
            "periodo": "tarde",
            "palestras": palestrasTarde,
            "fimMinutos": fimTarde
        })

        # Atualiza propostas com as que sobraram
        self.propostas = restantesTarde

        foiAgendado = bool(palestrasManha or palestrasTarde)
        return nova_trilha_agendada, foiAgendado

    def organizarConferencia(self):
        self.carregarPropostas()

        while self.propostas:
            novaTrilha, agendado = self.agendar()
            if not agendado:
                print("Aviso: Nem todas as palestras puderam ser agendadas.")
                break
            self.cronograma.append(novaTrilha)

    def imprimir(self):
        for i, trilha in enumerate(self.cronograma):
            print(f"\n---")
            print(f"## Trilha {chr(65 + i)}:\n")  # transforma número em letra (A, B, C...)

            for sessao in trilha:
                for palestra in sessao["palestras"]:
                    horaStr = self.minutosParaHora(palestra.hora_inicio)
                    duracaoDisplay = f"{palestra.duracao}min" if palestra.duracao != 5 else "lightning"
                    print(f"{horaStr} {palestra.titulo.strip()} {duracaoDisplay}")

                if sessao["periodo"] == "manhã":
                    print("12:00 Almoço")
                elif sessao["periodo"] == "tarde":
                    horaNetworking = max(sessao["fimMinutos"], self.INICIO_NETWORKING)
                    horaNetworking = min(horaNetworking, self.FIM_NETWORKING)
                    print(f"{self.minutosParaHora(horaNetworking)} Evento de Networking")


if __name__ == "__main__":
    organizador = OrganizadorConferencia()
    organizador.organizarConferencia()
    organizador.imprimir()
