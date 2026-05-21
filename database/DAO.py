from database.DB_connect import DBConnect
from model.artista import Artista
from model.genre import Genre
from model.popolarita import Popolarita


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def getAllArtist():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """ select distinct *
                    from artist"""
        cursor.execute(query)

        for row in cursor:
            result.append(Artista(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllGenre():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary = True)
        query = """ select distinct *
                    from genre"""
        cursor.execute(query)

        for row in cursor:
            result.append(Genre(**row))

        cursor.close()
        conn.close()
        return result

    """I vertici sono gli artisti (Artist) che possiedono
    almeno un brano (Track) appartenente al genere selezionato."""
    @staticmethod
    def getAllNodes(codGenere):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select distinct  art.ArtistId , art.Name
                    from track t
                    left join album a on t.AlbumId = a.AlbumId
                    left join artist art on a.ArtistId = art.ArtistId 
                    where t.GenreId = %s"""
        cursor.execute(query, (codGenere,))

        for row in cursor:
            result.append(Artista(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdges(codGenere, idMap):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """
                    select tt.artistid , sum(il.Quantity ) as pop, GROUP_CONCAT(i.CustomerId SEPARATOR ', ') as ListaClienti
                    from (	select distinct  t.TrackId, t.AlbumId, art.ArtistId, art.Name 
		                    from track t
		                    left join album a on t.AlbumId = a.AlbumId
		                    left join artist art on a.ArtistId = art.ArtistId 
		                    where t.GenreId = %s) tt
                    left join invoiceline il on il.TrackId = tt.TrackId 
                    left join invoice i on i.invoiceId = il.InvoiceId
                    where il.Quantity is not null
                    group by tt.artistid
                    order by pop asc """
        cursor.execute(query, (codGenere,))

        for row in cursor:
            # Trasformiamo la stringa "1, 5, 23" in un set di interi {1, 5, 23}
            stringa_clienti = row["ListaClienti"]
            if stringa_clienti:
                # Creiamo il set convertendo ogni elemento in intero in un colpo solo
                set_clienti = set(int(c.strip()) for c in stringa_clienti.split(","))
            else:
                # Se la stringa è None o vuota, il set rimane vuoto
                set_clienti = set()

            result.append(Popolarita(idMap[row["artistid"]], row["pop"], set_clienti))

        cursor.close()
        conn.close()
        return result






