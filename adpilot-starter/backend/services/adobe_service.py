"""Adobe Firefly async image generation.

The API can return a status URL. We only poll URLs supplied by Adobe and
restricted to the Firefly API host. Jobs are stored in memory for hackathon use.
"""
import os
from urllib.parse import urlparse
import httpx
from fastapi import HTTPException

JOBS: dict[str,str] = {}

async def _token(client:httpx.AsyncClient, client_id:str, secret:str)->str:
    response=await client.post('https://ims-na1.adobelogin.com/ims/token/v3',data={
        'grant_type':'client_credentials','client_id':client_id,'client_secret':secret,
        'scope':os.getenv('ADOBE_SCOPES','openid,AdobeID,session,additional_info,read_organizations,firefly_api,ff_apis')})
    if response.is_error: raise HTTPException(502,f'Adobe OAuth: HTTP {response.status_code}')
    return response.json()['access_token']

def _image_url(data:dict):
    outputs=data.get('outputs') or []
    if outputs and isinstance(outputs[0],dict):
        image=outputs[0].get('image') or {}
        return image.get('url') if isinstance(image,dict) else None
    return None

def _status_url(data:dict):
    candidate=data.get('statusUrl') or data.get('status_url') or data.get('pollingUrl')
    if not candidate and isinstance(data.get('links'),dict):
        candidate=data['links'].get('status')
        if isinstance(candidate,dict): candidate=candidate.get('href')
    if not candidate: return None
    p=urlparse(candidate)
    if p.scheme!='https' or p.hostname!='firefly-api.adobe.io' or p.username or p.password:
        return None
    return candidate

async def generate_image(prompt:str)->dict:
    client_id=os.getenv('ADOBE_CLIENT_ID');secret=os.getenv('ADOBE_CLIENT_SECRET')
    if not client_id or not secret: raise HTTPException(503,'Lipsesc cheile Adobe Firefly API')
    async with httpx.AsyncClient(timeout=50,follow_redirects=False) as client:
        token=await _token(client,client_id,secret)
        response=await client.post('https://firefly-api.adobe.io/v3/images/generate-async',headers={
            'Authorization':f'Bearer {token}','x-api-key':client_id,'Content-Type':'application/json','Accept':'application/json'},json={'prompt':prompt})
        if response.is_error: raise HTTPException(502,f'Adobe generate: HTTP {response.status_code}: {response.text[:160]}')
        data=response.json()
        job_id=str(data.get('jobId') or data.get('job_id') or data.get('id') or '')
        status_url=_status_url(data)
        if job_id and status_url: JOBS[job_id]=status_url
        image_url=_image_url(data)
        return {'status':'completed' if image_url else 'pending','image_url':image_url,'job_id':job_id or None,
                'message':None if image_url else ('Job pornit. Poți verifica progresul.' if status_url else 'Job pornit; verifică răspunsul Adobe pentru URL-ul de polling.')}

async def get_image_status(job_id:str)->dict:
    status_url=JOBS.get(job_id)
    if not status_url: raise HTTPException(404,'Job necunoscut sau URL de status indisponibil')
    client_id=os.getenv('ADOBE_CLIENT_ID');secret=os.getenv('ADOBE_CLIENT_SECRET')
    if not client_id or not secret: raise HTTPException(503,'Lipsesc cheile Adobe')
    async with httpx.AsyncClient(timeout=40,follow_redirects=False) as client:
        token=await _token(client,client_id,secret)
        response=await client.get(status_url,headers={'Authorization':f'Bearer {token}','x-api-key':client_id,'Accept':'application/json'})
        if response.is_error: raise HTTPException(502,f'Adobe status: HTTP {response.status_code}')
        data=response.json(); image_url=_image_url(data)
        status='completed' if image_url else str(data.get('status','pending')).lower()
        return {'status':status,'image_url':image_url,'job_id':job_id,'message':None if image_url else 'Generarea este în curs.'}
