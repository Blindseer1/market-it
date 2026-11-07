import os
import unittest
os.environ['DEMO_MODE']='true'
from fastapi.testclient import TestClient
from main import app

BUSINESS={'name':'BrewLab Coffee','website':'','industry':'HoReCa','audience':'Studenți 18–25 ani','city':'București','goal':'Clienți noi','tone':'Amuzant','budget':500}

class APITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.client=TestClient(app)
    def test_health(self):
        r=self.client.get('/api/health');self.assertEqual(r.status_code,200);self.assertTrue(r.json()['demo'])
    def test_complete_demo_flow(self):
        a=self.client.post('/api/analyze',json={'business':BUSINESS});self.assertEqual(a.status_code,200)
        s=self.client.post('/api/strategies',json={'business':BUSINESS,'analysis':a.json()});self.assertEqual(s.status_code,200)
        self.assertEqual(len(s.json()['strategies']),3)
        strategy=s.json()['strategies'][0]
        c=self.client.post('/api/creatives',json={'business':BUSINESS,'strategy':strategy,'package':'Growth'})
        self.assertEqual(c.status_code,200);self.assertEqual(len(c.json()['video_script']),4)
        e=self.client.post('/api/evaluate',json={'business':BUSINESS,'strategy':strategy})
        self.assertEqual(e.status_code,200);self.assertEqual(len(e.json()['criteria']),4)
        img=self.client.post('/api/generate-image',json={'prompt':strategy['image_prompt']})
        self.assertEqual(img.status_code,200);self.assertEqual(img.json()['status'],'demo')
    def test_demo_personalization(self):
        b={**BUSINESS,'name':'Nova Salon','industry':'Beauty & Wellness','tone':'Premium','budget':900}
        a=self.client.post('/api/analyze',json={'business':b}).json()
        self.assertIn('demonstra',a['summary'].lower())
        st=self.client.post('/api/strategies',json={'business':b,'analysis':a}).json()['strategies']
        self.assertEqual(st[0]['title'],'Experiența care contează')
        self.assertEqual(sum(s['budget'] for s in st),900)
    def test_invalid_package(self):
        a=self.client.post('/api/analyze',json={'business':BUSINESS}).json()
        st=self.client.post('/api/strategies',json={'business':BUSINESS,'analysis':a}).json()['strategies'][0]
        r=self.client.post('/api/creatives',json={'business':BUSINESS,'strategy':st,'package':'Unknown'})
        self.assertEqual(r.status_code,422)
    def test_validation(self):
        r=self.client.post('/api/analyze',json={'business':{**BUSINESS,'budget':-1}})
        self.assertEqual(r.status_code,422)

if __name__=='__main__':unittest.main()
