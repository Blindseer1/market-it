import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import AnalyzeRequest, StrategiesRequest, ImageRequest, Analysis, Strategy, CreativeRequest, CreativeAssets, EvaluationRequest, Evaluation
from services.website_analyzer import extract_website
from services.ai_service import analyze, strategies
from services.adobe_service import generate_image, get_image_status
from services.creative_service import demo_assets, generate_creatives
from services.evaluation_service import evaluate

load_dotenv()
app = FastAPI(title='AdPilot AI API', version='0.3.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173','http://127.0.0.1:5173'], allow_methods=['GET','POST'], allow_headers=['Content-Type'])
DEMO = os.getenv('DEMO_MODE', 'true').lower() == 'true'

def demo_market(b):
    sector=b.industry.lower()
    if any(word in sector for word in ('cafenea','horeca','restaurant')):
        return ('Testați oferte locale, conținut video despre produse și recomandări între prieteni.',
                ['Video scurt cu produsul și experiența din locație','Ofertă cu QR pentru grupuri','Parteneriate cu creatori locali'])
    if any(word in sector for word in ('fashion','retail','beauty','salon')):
        return ('Testați demonstrații vizuale ale produsului, testimoniale autentice și oferte limitate.',
                ['Reels demonstrative înainte/după fără afirmații neverificate','Postări cu beneficii și preț transparent','Cod promoțional pentru prima comandă'])
    return ('Testați mesaje despre problema rezolvată, exemple de utilizare și un îndemn clar la acțiune.',
            ['Video educativ de 15 secunde','Carousel cu trei beneficii verificabile','Landing page cu ofertă și formular'])


@app.get('/api/health')
def health(): return {'ok':True,'demo':DEMO,'adobe_configured':bool(os.getenv('ADOBE_CLIENT_ID') and os.getenv('ADOBE_CLIENT_SECRET'))}

@app.post('/api/analyze', response_model=Analysis)
async def analyze_business(req: AnalyzeRequest):
    b=req.business
    if DEMO:
        insight, opportunities = demo_market(b)
        return Analysis(summary=f'{b.name} activează în domeniul {b.industry}, în {b.city}. {insight} Analiză demonstrativă, fără cercetare live.', audience_insight=f'Public: {b.audience}. Obiectiv: {b.goal}. Adaptați mesajul la nevoile acestui segment.', opportunities=opportunities, risks=['Bugetul necesită prioritizare','Concurența trebuie verificată din surse reale','Nu există date istorice de conversie'], sources=[],demo=True)
    if not os.getenv('OPENAI_API_KEY'): raise HTTPException(503,'Lipsește OPENAI_API_KEY')
    site=await extract_website(b.website) if b.website else {'text':'','sources':[]}
    try: return await analyze(b,site['text'],site['sources'])
    except Exception as exc: raise HTTPException(502, f'Analiza AI a eșuat: {str(exc)[:180]}')

@app.post('/api/strategies')
async def generate_strategies(req: StrategiesRequest):
    b=req.business
    if DEMO:
        concepts=[
            ('Povestea în 15 secunde','Video vertical despre problema publicului și cum o rezolvă oferta.',['Instagram Reels','TikTok'],87,'O zi mai bună începe aici.',.50),
            ('Vino cu un prieten','Ofertă pentru două persoane, cu cod QR măsurabil.',['Instagram Stories','Materiale QR'],83,'Mai bine împreună. Descoperă oferta.',.30),
            ('Comunitatea decide','Campanie participativă cu povești, voturi și conținut de la clienți.',['Instagram','Facebook'],79,'Tu alegi următoarea experiență!',.20)
        ]
        if 'serios' in b.tone.lower() or 'premium' in b.tone.lower():
            concepts[0]=('Experiența care contează','Video elegant care prezintă avantajele reale ale produsului sau serviciului.',['Instagram','Facebook'],86,'Calitatea se vede în detalii.',.50)
        return {'strategies':[Strategy(id=f'strategy_{i+1}',title=t,description=f'{d} Adaptată pentru {b.industry} și publicul {b.audience}.',channels=c,budget=round(b.budget*share,2),score=sc,hook=h,image_prompt=f'High quality professional advertising photo for {b.name}, {b.industry}, {t}, {b.tone} atmosphere, target audience {b.audience}, clean composition, no text, no letters, no watermark') for i,(t,d,c,sc,h,share) in enumerate(concepts)]}
    if not os.getenv('OPENAI_API_KEY'): raise HTTPException(503,'Lipsește OPENAI_API_KEY')
    try: return {'strategies':await strategies(b,req.analysis)}
    except Exception as exc: raise HTTPException(502, f'Generarea strategiilor a eșuat: {str(exc)[:180]}')

@app.post('/api/creatives',response_model=CreativeAssets)
async def creatives(req: CreativeRequest):
    if DEMO: return demo_assets(req.business,req.strategy)
    if not os.getenv('OPENAI_API_KEY'): raise HTTPException(503,'Lipsește OPENAI_API_KEY')
    try: return await generate_creatives(req.business,req.strategy)
    except Exception as exc: raise HTTPException(502,f'Generarea materialelor a eșuat: {str(exc)[:180]}')

@app.post('/api/evaluate',response_model=Evaluation)
async def evaluation(req: EvaluationRequest): return evaluate(req.business,req.strategy)

@app.post('/api/generate-image')
async def image(req: ImageRequest):
    if DEMO: return {'status':'demo','image_url':None,'job_id':None,'message':'Mod demo: setează DEMO_MODE=false și configurează Adobe pentru generare reală.'}
    return await generate_image(req.prompt)

@app.get('/api/image-status/{job_id}')
async def image_status(job_id:str):
    if DEMO: return {'status':'demo','image_url':None,'job_id':job_id,'message':'Mod demo'}
    return await get_image_status(job_id)
