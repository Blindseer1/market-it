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

@app.get('/api/health')
def health(): return {'ok':True,'demo':DEMO,'adobe_configured':bool(os.getenv('ADOBE_CLIENT_ID') and os.getenv('ADOBE_CLIENT_SECRET'))}

@app.post('/api/analyze', response_model=Analysis)
async def analyze_business(req: AnalyzeRequest):
    b=req.business
    if DEMO:
        return Analysis(summary=f'{b.name} activează în domeniul {b.industry}, în {b.city}. Aceasta este o analiză ilustrativă, nu cercetare live.', audience_insight=f'Public țintă: {b.audience}. Testați mesaje adaptate obiectivului „{b.goal}”.', opportunities=['Conținut video scurt adaptat publicului','Oferte cu cod QR măsurabil','Colaborări locale și conținut de comunitate'], risks=['Bugetul necesită prioritizare','Concurență posibilă pe canalele sociale','Lipsesc date istorice de conversie'], sources=[],demo=True)
    if not os.getenv('OPENAI_API_KEY'): raise HTTPException(503,'Lipsește OPENAI_API_KEY')
    site=await extract_website(b.website) if b.website else {'text':'','sources':[]}
    try: return await analyze(b,site['text'],site['sources'])
    except Exception as exc: raise HTTPException(502, f'Analiza AI a eșuat: {str(exc)[:180]}')

@app.post('/api/strategies')
async def generate_strategies(req: StrategiesRequest):
    b=req.business
    if DEMO:
        concepts=[('Survival Mode ON','Video scurt, amuzant, construit în jurul unei probleme cotidiene.',['Instagram Reels','TikTok'],87,'3 ore de somn. 1 cafea. Restart.',.50),('Bring Your Friend','Ofertă pentru două persoane, cu cod QR pentru urmărirea conversiilor.',['Instagram Stories','Flyere QR'],83,'Adu un prieten. Experiența e mai bună în doi.',.30),('Community Stories','Campanie participativă bazată pe poveștile și reacțiile comunității.',['TikTok','Instagram'],79,'Care este cea mai amuzantă poveste a ta?',.20)]
        return {'strategies':[Strategy(id=f'strategy_{i+1}',title=t,description=d,channels=c,budget=round(b.budget*share),score=sc,hook=h,image_prompt=f'Premium advertising photograph for {b.name}, industry {b.industry}, campaign {t}, {b.tone} mood, appealing to {b.audience}, clean composition, no lettering, no logos, no text') for i,(t,d,c,sc,h,share) in enumerate(concepts)]}
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
