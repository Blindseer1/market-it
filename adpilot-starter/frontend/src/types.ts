export type Business={name:string;website:string;industry:string;audience:string;city:string;goal:string;tone:string;budget:number};
export type Analysis={summary:string;audience_insight:string;opportunities:string[];risks:string[];sources:string[];demo:boolean};
export type Strategy={id:string;title:string;description:string;channels:string[];budget:number;score:number;hook:string;image_prompt:string};
export type ImageResult={image_url:string|null;status:string;job_id?:string|null;message?:string};
export type CreativeAssets={headline:string;caption:string;hashtags:string[];cta:string;video_script:string[];poster_text:string;banner_text:string;image_prompt:string;demo:boolean};
export type Evaluation={score:number;criteria:{name:string;score:number;reason:string}[];strengths:string[];improvements:string[];disclaimer:string;demo:boolean};
