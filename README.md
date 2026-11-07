# MarketIt

**Stack:** React 18 + Vite + TypeScript + CSS + Recharts; Python + FastAPI + Pydantic; OpenAI API; Adobe Firefly Services API.

## Ce funcționează acum

1. Formular complet de business, cu preview live.
2. Analiză de business: demo imediat sau OpenAI + website extraction în modul live.
3. Trei strategii cu selecție, canale, hook, buget și scor demonstrativ.
4. Editor de campanie: titlu, buget, hook, descriere, prompt Adobe, ton, obiectiv.
5. Pachete Starter / Growth / Pro — doar simulare comercială, fără plată.
6. Creative Studio: poster CSS, text social media, hashtaguri, CTA, script video, concept banner.
7. Evaluare cu criterii și recomandări transparente, fără a pretinde predicții de reach.
8. Generare Adobe Firefly asincronă: cerere + polling când Adobe returnează status URL.
9. Export JSON, brief TXT, poster PNG; salvare automată a progresului în `localStorage`.
10. Dashboard Recharts cu alocare buget; design responsive.
11. Istoric local cu până la 12 campanii și restaurarea lor din sidebar.
12. Modul demo adaptează analiza și strategiile după industrie, ton și buget.
13. Verificare automată periodică a jobului Adobe, când API-ul oferă un identificator de job.
14. Cinci teste automate pentru backend, inclusiv personalizare și validare.

**Atenție:** În modul demo datele sunt fictive, iar posterul este randat de CSS/Canvas, nu de Adobe. Pentru generare reală, sunt necesare chei și acces Firefly Services API. Adobe poate modifica forma răspunsurilor; validați integrarea cu contul vostru.

## Pornire rapidă

### Terminal 1 — backend (Python 3.10+)

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
py -m uvicorn main:app --reload  # Windows; pe Linux/macOS: python -m uvicorn main:app --reload
```

Backend: http://localhost:8000/docs · Health: http://localhost:8000/api/health

### Terminal 2 — frontend (Node 20+)

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

Site: **http://localhost:5173**. Vite redirecționează `/api` spre FastAPI (`localhost:8000`). Nu trebuie să configurați CORS manual pentru acest flux.

## Activare AI și Adobe

În `backend/.env`:

```env
DEMO_MODE=false
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
ADOBE_CLIENT_ID=...
ADOBE_CLIENT_SECRET=...
```

Pentru demo fără chei, păstrați `DEMO_MODE=true`. Când `DEMO_MODE=false`, analiza, strategiile și copy-ul folosesc OpenAI; imaginile folosesc Adobe. Cheile rămân exclusiv pe server. Nu puneți `.env` în Git.

## Împărțirea între cei 4 membri

| Membru | Ownership | Fișiere principale | Următorul pas |
|---|---|---|---|
| 1 — Frontend & UX | Formular, wizard, responsive | `frontend/src/App.tsx`, `styles.css` | Spargeți App în componente și validați mai bine formularul |
| 2 — AI & research | Analiză și strategii | `backend/services/ai_service.py`, `website_analyzer.py`, `models.py` | Surse reale, prompturi testate, tratarea cazurilor website inaccesibil |
| 3 — Creative & Adobe | Texte și imagine | `backend/services/creative_service.py`, `adobe_service.py` | Test real Firefly, status polling, control costuri, prompturi |
| 4 — Dashboard & QA | Scoruri, export, demo | `backend/services/evaluation_service.py`, `frontend/src/components/Dashboard.tsx` | Teste, KPI, comparație, prezentare și deployment |

**Regulă de colaborare:** păstrați contractele din `backend/models.py` și `frontend/src/types.ts` sincronizate. Înainte de merge, testați întregul flux.

## Endpointuri

- `GET /api/health` — status backend, demo și configurare Adobe.
- `POST /api/analyze` — `{ "business": Business }` → `Analysis`.
- `POST /api/strategies` — `{ "business": Business, "analysis": Analysis }` → `{ "strategies": Strategy[] }`.
- `POST /api/creatives` — `{ "business": Business, "strategy": Strategy, "package": "Growth" }` → `CreativeAssets`.
- `POST /api/evaluate` — `{ "business": Business, "strategy": Strategy }` → `Evaluation`.
- `POST /api/generate-image` — `{ "prompt": "..." }` → `ImageResult`.
- `GET /api/image-status/{job_id}` — `ImageResult` pentru joburile Adobe cu status URL disponibil.

## Testare

Din `backend/`, după instalarea dependențelor:

```bash
python -m unittest discover -s tests -v
```

Din `frontend/`:

```bash
npm run build
```

## Ce NU este implementat

- Nu există plată reală, conturi sau analytics de reach real.
- Nu există forecast statistic al conversiilor; evaluarea este euristică.
- Nu există stocare cloud; progresul este salvat numai în browserul curent.
- În Firefly, polling-ul este disponibil numai dacă răspunsul furnizează un URL de status acceptat. Stocarea joburilor este în memorie și se pierde la restart.
- Nu există garanția că Firefly API este disponibil în contul Adobe. Verificați accesul înainte de demo.
- Website scraping are protecții de bază, dar nu este adecvat pentru expunere publică fără protecții suplimentare împotriva SSRF / DNS rebinding.

## Pitch recomandat (2 minute)

1. Formular cu cafenea fictivă și buget 500 RON.
2. Analiză → trei strategii → selectarea uneia.
3. Editarea hook-ului → Growth → Creative Studio.
4. Poster + social copy + script video + evaluare.
5. Dacă Adobe este configurat, generați o imagine; altfel folosiți fallback-ul CSS și explicați clar că e demo.

## Verificări și limitări (important)

- Backend: `cd backend && py -m unittest discover -s tests -v` — 5 teste trecute în mediul de dezvoltare.
- Frontend: `cd frontend && npm.cmd run build` — necesită instalarea dependențelor; instalarea npm nu a putut fi finalizată în mediul de creare, deci buildul frontend trebuie verificat pe PC-ul vostru.
- Nu există procesator de plăți, publicare automată pe rețele sociale, date reale de reach sau baze de date centralizate. Aceste funcții necesită integrări suplimentare și nu sunt prezentate ca funcționale.
- Modul live OpenAI/Adobe necesită acces valid la servicii și poate avea costuri. Integrarea Adobe trebuie validată cu un cont Firefly Services API.
- Nu introduceți date confidențiale în câmpul website; conținutul extern este tratat ca sursă neîncredere.

## Pornire Windows PowerShell (fără schimbarea ExecutionPolicy)

Terminal 1:
```powershell
cd backend
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload
```
Terminal 2:
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Vizitați `http://localhost:5173/` și `http://127.0.0.1:8000/docs`.
