# W wyniku bliżej nieokreślonej awarii dane o zapasach niektórych produktów
# uległy uszkodzeniu. Korzystając z bazy SQL monitorującej te informacje
# przywróć porządek na magazynie - dokumentację API znajdziesz pod adresem
# $DOMAIN/docs. Pamiętaj, że tylko zapytania GET są darmowe!
#
# Autoryzacja dostępu do API jest dwustopniowa:
#  1. ze ścieżki /login/aws uwierzytelnionej przez HTTP Basic Access uzyskujesz
#     token Bearer o określonym czasie ważności
#  2. wszystkie pozostałe ścieżki uwierzytelniane są przez podanie w nagłówku
#     Authorization ciągu "Bearer <access_token>"
#
from sqlite3 import connect

DOMAIN = "https://recruitment.developers.emako.pl"

sql = connect(database="database.sqlite")


sql.close()
