import copy
import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._grafo = nx.DiGraph()
        self._artisti = DAO.getAllArtist()
        self._idMap = {}
        for a in self._artisti:
            self._idMap[a.ArtistId] = a
        self._elencoInfluenzaArtisti=[]


    def getAllGenre(self):
        return DAO.getAllGenre()

    def getAllNodes(self, genere):
        return DAO.getAllNodes(genere)

    def getAllPopolarita(self, genere):
        return DAO.getAllEdges(genere, self._idMap)

    def addEdges(self, genere):
        elenco_pop= self.getAllPopolarita(genere)
        for i in range(len(elenco_pop)):
            for j in range(i+1, len(elenco_pop)):
                nodoA= elenco_pop[i]
                nodoB= elenco_pop[j]
                if self._grafo.has_node(nodoA.artist) and self._grafo.has_node(nodoB.artist):
                    #Controllo sull'intersezione degli acquirenti dei brani dei due artisti
                    if nodoA.ListaClienti.intersection(nodoB.ListaClienti): #Indica se c'è almeno un'intersezione
                        #Controllo sul peso degli archi per capire la direzione in cui inserirlo
                        peso_arco = nodoA.pop + nodoB.pop
                        if nodoA.pop > nodoB.pop:
                            self._grafo.add_edge(nodoA.artist, nodoB.artist, weight= peso_arco)
                        elif nodoA.pop < nodoB.pop:
                            self._grafo.add_edge(nodoB.artist, nodoA.artist, weight = peso_arco)
                        else:
                            self._grafo.add_edge(nodoA.artist, nodoB.artist, weight=peso_arco)
                            self._grafo.add_edge(nodoB.artist, nodoA.artist, weight=peso_arco)


    def buildGraph(self, genere):
        self._grafo.clear()
        elencoNodi = self.getAllNodes(genere)
        self._grafo.add_nodes_from(elencoNodi)
        self.addEdges(genere)
        self.getGraphDetails()

    def getGraphDetails(self):
        print(f"{len(self._grafo.nodes())} nodi -- {len(self._grafo.edges())} archi")
        return len(self._grafo.nodes()), len(self._grafo.edges())

    def getTopArtist(self):
        elencoArtisti = self._grafo.nodes()
        topArtist = None
        influenza_max=-1
        for a in elencoArtisti:
            peso_uscente = 0
            for u, v, diz_attributi in self._grafo.out_edges(a, data=True):
                peso_uscente += diz_attributi["weight"]
            # Calcolo dei pesi entranti
            peso_entrante = 0
            for u, v, diz_attributi in self._grafo.in_edges(a, data=True):
                peso_entrante += diz_attributi["weight"]
            influenza = peso_uscente - peso_entrante
            self._elencoInfluenzaArtisti.append((a, influenza))
            if influenza > influenza_max:
                topArtist=a
                influenza_max=influenza
        return topArtist, influenza_max

    def getTop5(self):
        lista_ordinata = sorted(self._elencoInfluenzaArtisti, key=lambda x: x[1], reverse = True)
        return lista_ordinata[:5]

    def getNodes(self):
        return self._grafo.nodes()

    def getPesoArco(self, u, v):
        return self._grafo[u][v]["weight"]

    def getPath(self, v0):
        parziale =[v0]
        self._bestPath=[]
        self._costoCammino = -1
        #Inizio a ciclare sui vicini del mio nodo
        for v in self._grafo.successors(v0):
            parziale.append(v)
            self._ricorsione(parziale)
            parziale.pop()
        return self._bestPath, self._costoCammino

    def _ricorsione(self, parziale):
        punteggio_attuale = self._score(parziale)
        if punteggio_attuale > self._costoCammino: #Ricerca il cammino con costo massimo
            self._bestPath = copy.deepcopy(parziale)
            self._costoCammino = punteggio_attuale
        #Definisco i controlli i base ai quali stabilisco se aggiungere o meno un nodo per
        #proseguire il mio cammino
        nodo_corrente = parziale[-1]
        for v in self._grafo.successors(nodo_corrente):
            if v not in parziale:
                pesoE = self.getPesoArco(nodo_corrente, v)
                nodo_precedente = parziale[-2]
                peso_prec = self.getPesoArco(nodo_precedente, nodo_corrente)
                if pesoE > peso_prec: #Cammino ad archi con peso crescente
                    parziale.append(v)
                    self._ricorsione(parziale)
                    parziale.pop()

    def _score(self, parziale):
        score = 0
        for i in range(len(parziale)-1):
            score += self._grafo[parziale[i]][parziale[i+1]]["weight"]
        return score















