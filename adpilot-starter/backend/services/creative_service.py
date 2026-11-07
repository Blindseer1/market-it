"""Membrul 3: texte creative, gata de conectat cu Adobe Firefly pentru vizual."""
from models import Business, Strategy, CreativeAssets
from services.ai_service import ai_json


def demo_assets(b: Business, s: Strategy) -> CreativeAssets:
    return CreativeAssets(
        headline=s.hook,
        caption=f'{s.hook} ✨ {b.name} te așteaptă în {b.city}. Descoperă experiența și spune-ne cu cine ai veni!',
        hashtags=['#' + ''.join(b.name.split())[:24], '#DescoperaLocal', '#CampanieNoua'],
        cta='Vino să ne cunoști',
        video_script=[
            '0–3 sec: Arată problema publicului țintă într-o scenă memorabilă.',
            f'3–8 sec: Prezintă {b.name} ca soluție, în ton {b.tone.lower()}.',
            f'8–12 sec: Afișează mesajul: „{s.hook}”.',
            '12–15 sec: Încheie cu logo și un îndemn clar la acțiune.'
        ],
        poster_text=s.hook,
        banner_text=f'{b.name} • Descoperă acum',
        image_prompt=s.image_prompt,
        demo=True,
    )


async def generate_creatives(b: Business, s: Strategy) -> CreativeAssets:
    return await ai_json(
        'Ești copywriter de publicitate. Generează texte concrete, scurte și creative în română, '
        'cu scenariu video de 15 secunde în 4 cadre. Fără afirmații factuale nefondate, '
        'fără promisiuni de rezultate. Promptul imaginii să fie în engleză, fără text în imagine.',
        f'Business: {b.model_dump_json()}\nStrategie: {s.model_dump_json()}',
        CreativeAssets,
    )
