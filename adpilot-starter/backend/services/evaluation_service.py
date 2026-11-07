"""Membrul 4: evaluare transparentă și reproductibilă, nu forecast inventat."""
from models import Business, Strategy, Evaluation

def evaluate(b: Business, s: Strategy) -> Evaluation:
    criteria = [
        {'name':'Potrivire cu publicul', 'score':min(95, 68 + (10 if b.audience else 0) + (8 if s.channels else 0)), 'reason':'Public și canale declarate'},
        {'name':'Claritatea mesajului', 'score':min(95, 55 + min(len(s.hook), 55)//2), 'reason':'Hook-ul este evaluat prin lungime, nu performanță reală'},
        {'name':'Fezabilitatea bugetului', 'score':90 if s.budget <= b.budget else 40, 'reason':'Bugetul propus se încadrează în limita declarată' if s.budget <= b.budget else 'Bugetul propus depășește limita'},
        {'name':'Diversitatea canalelor', 'score':85 if len(s.channels) >= 2 else 60, 'reason':'Număr de canale distincte'},
    ]
    score = round(sum(c['score'] for c in criteria)/len(criteria))
    improvements = ['Testați două variante de mesaj cu buget mic înainte de extindere.', 'Urmăriți clicuri și conversii cu un cod sau link dedicat.']
    if s.budget > b.budget: improvements.insert(0, 'Reduceți alocarea propusă pentru a respecta bugetul.')
    return Evaluation(score=score, criteria=criteria, strengths=['Obiectiv și public definite', 'Strategie cu canale de distribuție'], improvements=improvements, demo=True)
