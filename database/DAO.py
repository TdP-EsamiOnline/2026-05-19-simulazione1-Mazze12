from database.DB_connect import DBConnect
from model.artista import Artista
from model.genre import Genre
from model.popolarita import Popolarita


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def getAllGenre():
        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary = True)
        result = []
        query = """ select distinct g.GenreId , g.Name 
                    from Genre g """
        cursor.execute(query)
        for row in cursor:
            result.append(Genre(**row))
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllArtist():
        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)
        result = []
        query = """ select *
                    from artist a """
        cursor.execute(query)
        for row in cursor:
            result.append(Artista(**row))
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllNodes(genere):
        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)
        result = []
        query = """ select a.*
                    from artist a
                    left join album al on a.ArtistId = al.ArtistId 
                    left join track t on al.AlbumId =t.AlbumId 
                    where t.GenreId = %s
                    group by a.ArtistId  """
        cursor.execute(query, (genere.GenreId,))
        for row in cursor:
            result.append(Artista(**row))
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdges(genere, idMap):
        conn = DBConnect.get_connection()
        cursor = conn.cursor(dictionary=True)
        result = []
        query = """ select a.ArtistId , sum(il.Quantity) as pop , GROUP_CONCAT(i.CustomerId SEPARATOR ', ') as ListaClienti
                    from artist a
                    left  join album al on a.ArtistId = al.ArtistId 
                    left join track t on al.AlbumId = t.AlbumId 
                    left join invoiceline il on t.TrackId =il.TrackId 
                    left join invoice i on il.InvoiceId = i.InvoiceId 
                    where t.GenreId = %s and il.Quantity is not null
                    group by a.ArtistId"""
        cursor.execute(query, (genere.GenreId,))
        for row in cursor:
            stringa_clienti = row["ListaClienti"]
            if stringa_clienti:
                set_clienti = set(int(c.strip()) for c in stringa_clienti.split(","))
            else:
                # Se la stringa è None o vuota, il set rimane vuoto
                set_clienti = set()
            result.append(Popolarita(idMap[row["ArtistId"]], row["pop"], set_clienti))
        cursor.close()
        conn.close()
        return result




