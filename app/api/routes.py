from fastapi import APIRouter

router = APIRouter()

# Autoryzacja i użytkownicy
@router.post("/auth/register")      # Rejestracja nowego użytkownika
@router.post("/auth/login")         # Logowanie, zwraca JWT
@router.post("/auth/reset-password")# Reset hasła
@router.get("/users/me")            # Pobierz dane aktualnego użytkownika
@router.get("/users/")              # (Admin) Lista użytkowników
@router.patch("/users/{user_id}")   # (Admin) Edycja/blokowanie/odblokowanie

# Zgłoszenia Helpdesk (Tickets)
@router.post("/tickets/")           # Utwórz nowe zgłoszenie
@router.get("/tickets/")            # Lista zgłoszeń (filtry: status, kategoria, priorytet, itd.)
@router.get("/tickets/{ticket_id}") # Szczegóły zgłoszenia
@router.patch("/tickets/{ticket_id}") # Aktualizacja zgłoszenia (status, pracownik, opis)
@router.post("/tickets/{ticket_id}/comment") # Dodaj komentarz do zgłoszenia
@router.post("/tickets/{ticket_id}/attachment") # Dodaj załącznik

# Kategorie i priorytety
@router.get("/categories/")         # Lista kategorii
@router.post("/categories/")        # Dodaj kategorię (admin)
@router.get("/priorities/")         # Lista priorytetów
@router.post("/priorities/")        # Dodaj priorytet (admin)

# Powiadomienia (opcjonalnie)
@router.get("/notifications/")      # Lista powiadomień użytkownika

# Statystyki i raporty (admin)
@router.get("/stats/")              # Statystyki systemowe, np. liczba zgłoszeń, czas obsługi
