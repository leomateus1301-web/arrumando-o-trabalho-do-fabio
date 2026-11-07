from django.test import TestCase, Client

class SiteAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_ct11_navegacao_paginas(self):
        # Utilizar os endereços exatos validados no teste manual
        urls = ['/', '/servicos/', '/quem-somos/', '/contato/']
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Falha ao carregar a página: {url}")

    def test_ct12_pagina_inexistente(self):
        response = self.client.get('/pagina-que-nao-existe/')
        self.assertEqual(response.status_code, 404)

    def test_ct15_chatbot_metodo_get(self):
        response = self.client.get('/chatbot/mensagem/')
        self.assertIn(response.status_code, [405, 403])