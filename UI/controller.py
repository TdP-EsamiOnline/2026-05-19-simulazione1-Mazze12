import flet as ft


class Controller:

    def __init__(self, view, model):
        self._view = view
        self._model = model
        self._genre = None
        self._codiceGenere = None

    def fillDDGenre(self):
        allGenre = self._model.getAllGenre()
        for g in allGenre:
            self._view._ddGenre.options.append(
                ft.dropdown.Option(
                    data=g, key=g.Name, on_click=self._choiceGenre
                )
            )

    def _choiceGenre(self, e):
        self._genre = e.control.data
        self._codiceGenere = self._genre.GenreId
        print(f"Hai selezionato il genere: {self._genre}")

    def handleCreaGrafo(self, e):
        if self._genre is None:
            self._view.txt_result.controls.clear()
            self._view.txt_result.controls.append(
                ft.Text(
                    f"Devi selezionare un genere dal menù a tendina",
                    color="red",
                )
            )
            self._view.update_page()
            return

        # Creazione del grafo
        self._model.buildGraph(self._genre.GenreId)
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"Grafo correttamente creato", color="green")
        )

        # Informazioni di base numeriche
        nNodes, nEdges = self._model.getInformatinGraph()
        self._view.txt_result.controls.append(
            ft.Text(f"Numero di nodi: {nNodes} nodi")
        )
        self._view.txt_result.controls.append(
            ft.Text(f"Numero di archi: {nEdges} archi")
        )

        # Richiesta Punto C: Artista più influente (peso uscenti - entranti)
        artista_top, influenza = self._model.calcolaArtistaPiuInfluente()
        if artista_top:
            self._view.txt_result.controls.append(
                ft.Text(
                    f"L'artista più influente è {artista_top.Name} con influenza: {influenza}"
                )
            )
        else:
            self._view.txt_result.controls.append(
                ft.Text("Nessun artista influente trovato (grafo vuoto)")
            )

        # Richiesta Punto C: Visualizzazione dei 5 archi con peso maggiore
        self._view.txt_result.controls.append(
            ft.Text(
                "\nI 5 archi con peso maggiore sono:",
                color="blue",
            )
        )
        top_archi = self._model.getTop5Archi()
        for u, v, peso in top_archi:
            self._view.txt_result.controls.append(
                ft.Text(f"Arco: {u.Name} -> {v.Name} | Peso totale: {peso}")
            )

        self._view.update_page()

        # Questo pezzo va inserito in handleCreaGrafo, subito dopo aver calcolato i top 5 archi
        # Lo inseriamo qui per popolare il menu degli artisti subito dopo la creazione del grafo
        # --- NUOVA AGGIUNTA PER IL PUNTO 2.a ---
        # Recuperiamo i nodi del grafo appena creato (che sono gli artisti di quel genere)
        nodi_grafo = self._model.getNodes()

        # Puliamo le vecchie opzioni se presenti
        self._view._ddArtist.options.clear()

        # Popoliamo il menu a tendina degli artisti
        for artista in nodi_grafo:
            self._view._ddArtist.options.append(
                ft.dropdown.Option(
                    data=artista,
                    key=str(artista.ArtistId),
                    text=artista.Name,
                    on_click=self._choiceArtist
                )
            )
        self._view.update_page()

    # Metodo di supporto per catturare l'artista selezionato dal dropdown
    def _choiceArtist(self, e):
        self._artist_selezionato = e.control.data
        print(f"Hai selezionato l'artista di partenza: {self._artist_selezionato}")


    # --- RISOLUZIONE PUNTO 2.b e 2.c ---
    def handleCammino(self, e):
        # 1. Verifica che il grafo sia stato creato
        if len(self._model.getNodes()) == 0:
            self._view.txt_result.controls.append(ft.Text("Errore: Crea prima il grafo!", color="red"))
            self._view.update_page()
            return

        # 2. Verifica che l'utente abbia selezionato un artista di partenza
        if not hasattr(self, '_artist_selezionato') or self._artist_selezionato is None:
            self._view.txt_result.controls.append(
                ft.Text("Errore: Seleziona un artista di partenza dal menu!", color="red"))
            self._view.update_page()
            return

        # 3. Invocazione della logica sul Model
        cammino_ottimo = self._model.getPath(self._artist_selezionato)

        # 4. Visualizzazione dei risultati nella View
        self._view.txt_result.controls.append(
            ft.Text(f"\n--- CAMMINO MASSIMO CRESCENTE DA {self._artist_selezionato.Name} ---",
                    color="green")
        )

        if len(cammino_ottimo) <= 1:
            self._view.txt_result.controls.append(
                ft.Text("Nessun cammino trovato a partire da questo artista con pesi crescenti."))
        else:
            self._view.txt_result.controls.append(
                ft.Text(f"Lunghezza cammino (numero di nodi): {len(cammino_ottimo)}"))

            # Stampiamo il percorso passo dopo passo mostrando il peso dell'arco intermedio
            for i in range(len(cammino_ottimo) - 1):
                u = cammino_ottimo[i]
                v = cammino_ottimo[i + 1]
                peso = self._model.getPesoArco(u, v)
                self._view.txt_result.controls.append(
                    ft.Text(f"Passo {i + 1}: {u.Name} --> {v.Name} (Peso Arco: {peso})")
                )

        self._view.update_page()


