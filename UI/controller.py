import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._genere=None
        self._source= None

    def fillDDGenre(self):
        elencoGeneri = self._model.getAllGenre()
        for g in elencoGeneri:
            self._view._ddGenre.options.append(
                ft.dropdown.Option( data= g,
                                    key= g.Name,
                                    on_click= self._choiceGenre)
            )

    def _choiceGenre(self,e):
        self._genere = e.control.data
        print(f"Hai selezionato il genere {self._genere.Name}")


    def handleCreaGrafo(self, e):
        if self._genere is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text(f"Per favore selziona un genere per poter procedere")
            )
            self._view.update_page()
            return
        self._model.buildGraph(self._genere)
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"Grafo correttamente creato")
        )
        nNodes, nEdges = self._model.getGraphDetails()
        self._view.txt_result.controls.append(
            ft.Text(f"Il grafo presenta {nNodes} nodi e {nEdges} archi")
        )
        self.fillDDArtist(self._genere)
        self._view.update_page()
        topArtist, maxI = self._model.getTopArtist()
        self._view.txt_result.controls.append(
            ft.Text(f"L'artista con la maggiore influenza è:", color = "green"))
        self._view.txt_result.controls.append(ft.Text(f"{topArtist.Name} con un'influenza di {maxI}"))
        self._view.update_page()
        elencoArtistiInfluenza = self._model.getTop5()
        self._view.txt_result.controls.append(
            ft.Text(f"Di seguito riportata la top 5 degli artisti più influenti", color = "green"))
        for a in elencoArtistiInfluenza:
            self._view.txt_result.controls.append(
            ft.Text(f"{a[0].Name} con un'influenza di {a[1]}"))
        self._view.update_page()

    def fillDDArtist(self, genere):
        self._artistiGenere = self._model.getAllNodes(genere)
        for a in self._artistiGenere:
            self._view._ddArtist.options.append(
                ft.dropdown.Option(data = a,
                                   key = a.Name,
                                   on_click = self._choiceSource)
            )

    def _choiceSource(self, e):
        self._source = e.control.data
        return self._source



    def handleCammino(self,e):
        if len(self._model.getNodes()) == 0:
            self._view.txt_result.controls.append(ft.Text("Errore: Crea prima il grafo!", color="red"))
            self._view.update_page()
            return
        if self._source is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text(f"Per favore selziona un artista per poter procedere")
            )
            self._view.update_page()
            return
        bestPath , costoCammino = self._model.getPath(self._source)
        if len(bestPath) <= 1:
            self._view.txt_result.controls.append(
                ft.Text("Nessun cammino trovato a partire da questo artista con pesi crescenti."))
        else:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text(f"Il cammino massimo travato a partire dal nodo sorgente: {self._source}")
            )
            for a in range(len(bestPath)-1):
                self._view.txt_result.controls.append(
                ft.Text(f"{bestPath[a].Name} --> {bestPath[a+1].Name}: {self._model.getPesoArco(bestPath[a], bestPath[a+1])}")
                )

            self._view.txt_result.controls.append(
                ft.Text(f"Lunghezza cammino (numero di nodi): {len(bestPath)} \n"
                        f"Costo totale del cammino: {costoCammino}"))
            self._view.update_page()




