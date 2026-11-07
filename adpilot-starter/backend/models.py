from pydantic import BaseModel, Field

class Business(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    website: str = ''
    industry: str = ''
    audience: str = ''
    city: str = ''
    goal: str = ''
    tone: str = ''
    budget: float = Field(ge=0, le=100000000)

class Analysis(BaseModel):
    summary: str
    audience_insight: str
    opportunities: list[str]
    risks: list[str]
    sources: list[str] = []
    demo: bool = False

class Strategy(BaseModel):
    id: str
    title: str
    description: str
    channels: list[str]
    budget: float
    score: int = Field(ge=0, le=100)
    hook: str
    image_prompt: str

class AnalyzeRequest(BaseModel):
    business: Business

class StrategiesRequest(BaseModel):
    business: Business
    analysis: Analysis

class ImageRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=4000)

class CreativeRequest(BaseModel):
    business: Business
    strategy: Strategy
    package: str = Field(default='Growth', pattern='^(Starter|Growth|Pro)$')

class CreativeAssets(BaseModel):
    headline: str
    caption: str
    hashtags: list[str]
    cta: str
    video_script: list[str]
    poster_text: str
    banner_text: str
    image_prompt: str
    demo: bool = False

class EvaluationRequest(BaseModel):
    business: Business
    strategy: Strategy

class Evaluation(BaseModel):
    score: int = Field(ge=0, le=100)
    criteria: list[dict]
    strengths: list[str]
    improvements: list[str]
    disclaimer: str = 'Evaluare euristică; nu reprezintă o predicție statistică a rezultatelor.'
    demo: bool = False
