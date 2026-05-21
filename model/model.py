import copy
import networkx as nx
from database.DAO import DAO


class Model:

    def __init__(self):
        self._grafo = nx.DiGraph()
        self._AllArtist = DAO.getAllArtist()
        self._idMap = {}
        for a in self._AllArtist:
            self._idMap[a.ArtistId] = a

    def getAllArtist(self):
        return DAO.getAllArtist()

    def getAllGenre(self):
        return DAO.getAllGenre()

    def getAllNodes(self, codGenre):
        return DAO.getAllNodes(codGenre)

    def addEdges(self, codGenere):
        allEdges = DAO.getAllEdges(codGenere, self._idMap)
        if len(allEdges) == 0:
            print("Nessun nodo trovato")
            return

        # Per rispettare rigorosamente il vincolo sui nodi del grafo pre-inseriti
        # creiamo una mappa rapida {Id_Artista: Oggetto_Popolarita}
        pop_map = {p.artist.ArtistId: p for p in allEdges}

        # Poiché non possiamo modificare il DAO per fare la query sui co-acquisti,
        # e assumendo che la richiesta consideri le relazioni tra tutti gli artisti
        # estratti da getAllEdges che hanno una popolarità valorizzata (e quindi acquistati):
        for i in range(len(allEdges)):
            for j in range(i + 1, len(allEdges)):
                u = allEdges[i]
                v = allEdges[j]

                # 1. CONTROLLO CRUCIALE: Hanno almeno un cliente (compratore) in comune?
                # .intersection() interseca i due set. Se l'intersezione contiene elementi,
                # viene valutata come True, altrimenti se è un set vuoto viene valutata come False.
                if u.ListaClienti.intersection(v.ListaClienti):
                    # 2. Assicuriamoci che i nodi esistano effettivamente nel grafo
                    if self._grafo.has_node(u.artist) and self._grafo.has_node(v.artist):
                        peso_arco = u.pop + v.pop

                        if u.pop > v.pop:
                            self._grafo.add_edge(
                                 u.artist, v.artist, weight=peso_arco
                            )
                        elif v.pop > u.pop:
                            self._grafo.add_edge(
                                v.artist, u.artist, weight=peso_arco
                            )
                        else:
                            # Stessa popolarità -> Entrambi i versi
                            self._grafo.add_edge(
                                u.artist, v.artist, weight=peso_arco
                            )
                            self._grafo.add_edge(
                                v.artist, u.artist, weight=peso_arco
                            )

    def buildGraph(self, codGenere):
        self._grafo.clear()
        allNodes = self.getAllNodes(codGenere)
        self._grafo.add_nodes_from(allNodes)
        self.addEdges(codGenere)

    # SOSTITUISCE: trovaArtistaTop con il calcolo richiesto dell'influenza
    def calcolaArtistaPiuInfluente(self):
        #Inizializzo le variabili di confronto
        best_artist = None
        max_influenza = float("-inf")
        #Inizio a ciclare per ogni nodo del mio grafo
        for nodo in self._grafo.nodes():
            # Calcolo dei pesi uscenti dal nodo considerato
            peso_uscente = 0
            for u, v, diz_attributi in self._grafo.out_edges(nodo, data=True):
                peso_uscente += diz_attributi["weight"]
            # Calcolo dei pesi entranti
            peso_entrante=0
            for u, v, diz_attributi in self._grafo.in_edges(nodo, data=True):
                peso_entrante += diz_attributi["weight"]

            influenza = peso_uscente - peso_entrante

            if influenza > max_influenza:
                max_influenza = influenza
                best_artist = nodo

        return best_artist, max_influenza

    # NUOVO METODO: Recupera i 5 archi con peso maggiore
    def getTop5Archi(self):
        archi_pesati = []
        for u, v, data in self._grafo.edges(data=True):
            archi_pesati.append((u, v, data["weight"]))

        # Ordina in ordine decrescente in base al peso (elemento in posizione 2)
        archi_pesati.sort(key=lambda x: x[2], reverse=True)
        return archi_pesati[:5]

    def getInformatinGraph(self):
        return len(self._grafo.nodes()), len(self._grafo.edges())

##### PUNTO 2 #####
    # Metodo di utilità per il Controller per ottenere i nodi correnti
    def getNodes(self):
        return list(self._grafo.nodes())

    # Metodo di utilità per recuperare il peso di un arco specifico
    def getPesoArco(self, u, v):
        return self._grafo[u][v]['weight']

    import copy

    def getPath(self, v0):
        # Inizializzazione della struttura dati fornita
        parziale = [v0]

        # Inizializziamo le variabili d'istanza per memorizzare la soluzione migliore
        self._bestPath = []
        self._costoCammino = -1  # Valore iniziale per la ricerca del massimo

        # Esploriamo i vicini del nodo di partenza v0
        # Nota: usiamo successors() perché il grafo è diretto (DiGraph)
        for v in self._grafo.successors(v0):
            parziale.append(v)

            # Avviamo la ricorsione passando il cammino iniziale [v0, v]
            self.ricorsione(parziale)

            # Backtracking: Rimuoviamo il vicino per testare le altre strade nel ciclo (Aggiunte le parentesi)
            parziale.pop()

        return self._bestPath

    def ricorsione(self, parziale):
        # 1. VERIFICO SE LA SOLUZIONE PARZIALE È MIGLIORE DEL BEST -- Ottimalità
        # Utilizziamo la funzione _score fornita nel tuo pattern per calcolare il peso totale
        punteggio_attuale = self._score(parziale)

        if punteggio_attuale > self._costoCammino:
            self._bestPath = copy.deepcopy(parziale)
            self._costoCammino = punteggio_attuale

        # 2. VERIFICO SE HA SENSO CONTINUARE -- Terminazione (Non ci sono vincoli di interruzione precoce)

        # 3. FACCIO LA MIA RICORSIONE
        # Il nodo corrente da cui cercare i successivi è sempre l'ultimo inserito nel cammino
        nodo_corrente = parziale[-1]

        # Recuperiamo i vicini (successori) dell'ultimo nodo (corretto l'errore delle foto)
        for v in self._grafo.successors(nodo_corrente):

            # Vincolo fondamentale: il cammino deve essere SEMPLICE (niente cicli/ripassaggi)
            if v not in parziale:

                # Peso del potenziale arco che andremmo ad aggiungere (es. da parziale[-1] a v)
                pesoE = self._grafo[nodo_corrente][v]["weight"]

                # Peso dell'ultimo arco che abbiamo attraversato per arrivare qui (da parziale[-2] a parziale[-1])
                nodo_precedente = parziale[-2]
                peso_precedente = self._grafo[nodo_precedente][nodo_corrente][
                    "weight"
                ]

                # CONDIZIONE 2.C: Il peso del nuovo arco deve essere STRETTAMENTE CRESCENTE
                if pesoE > peso_precedente:
                    parziale.append(v)

                    # Chiamata ricorsiva (corretto il nome del metodo in self.ricorsione)
                    self.ricorsione(parziale)

                    # Backtracking
                    parziale.pop()

    def _score(self, parziale):
        score = 0
        # Corretto il bug sintattico delle foto: len(parziale) - 1
        # Iteriamo su tutti gli archi sequenziali del cammino parziale per sommarne i pesi
        for i in range(len(parziale) - 1):
            score += self._grafo[parziale[i]][parziale[i + 1]]["weight"]
        return score